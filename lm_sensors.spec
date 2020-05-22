# lm_sensors is used by mesa, mesa is used by wine and steam
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 5
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d
%define lib32name lib%{name}%{major}
%define dev32name lib%{name}-devel

Summary:	Utilities for lm_sensors
Name:		lm_sensors
Epoch:		1
Version:	3.6.0
%define dashedv %(echo %{version} |sed -e 's,\\.,-,g')
Release:	1
License:	LGPLv2+
Group:		System/Kernel and hardware
Url:		http://github.com/lm-sensors/lm-sensors
Source0:	https://github.com/lm-sensors/lm-sensors/archive/V%{dashedv}.tar.gz
Source1:	lm_sensors.sysconfig
# these 2 were taken from PLD-linux, Thanks!
Source2:	sensord.sysconfig
Patch0:		lm_sensors-3.3.5-add-ConditionVirtualization-no.patch
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	sysfsutils-devel
BuildRequires:	pkgconfig(librrd)
%ifarch %{ix86} %{x86_64}
Requires:	dmidecode
%endif

%description
This package contains a collection of user space tools for general SMBus
access and hardware monitoring. SMBus, also known as System Management Bus,
is a protocol for communicating through a I2C ('I squared C') bus. Many modern
mainboards have a System Management Bus. There are a lot of devices which can
be connected to a SMBus; the most notable are modern memory chips with EEPROM
memories and chips for hardware monitoring.

Most modern mainboards incorporate some form of hardware monitoring chips.
These chips read things like chip temperatures, fan rotation speeds and
voltage levels. There are quite a few different chips which can be used
by mainboard builders for approximately the same results.

%package -n %{libname}
Summary:	Libraries needed for lm_sensors
Group:		System/Libraries

%description -n %{libname}
Libraries to access lm_sensors internal data.

%package -n %{devname}
Summary:	Development libraries and header files for lm_sensors
Group:		Development/C
Requires:	%{libname} = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel = %{epoch}:%{version}-%{release}

%description -n %{devname}
Development libraries and header files for lm_sensors.

You might want to use this package while building applications that might
take advantage of lm_sensors if found.

%if %{with compat32}
%package -n %{lib32name}
Summary:	Libraries needed for lm_sensors (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
Libraries to access lm_sensors internal data.

%package -n %{dev32name}
Summary:	Development libraries and header files for lm_sensors (32-bit)
Group:		Development/C
Requires:	%{lib32name} = %{epoch}:%{version}-%{release}

%description -n %{dev32name}
Development libraries and header files for lm_sensors.

You might want to use this package while building applications that might
take advantage of lm_sensors if found.
%endif

%prep
%autosetup -n lm-sensors-%{dashedv} -p1

%build
%setup_compile_flags

%if %{with compat32}
mkdir build32
cp -a $(ls -1 |grep -v build32) build32
cd build32
export LD_LIBRARY_PATH="$(pwd)/lib"
export CFLAGS="$(echo ${CFLAGS} |sed -e 's,-m64,,g')"
export LDFLAGS="$(echo ${LDFLAGS} |sed -e 's,-m64,,g')"
%make_build CC="gcc -m32" PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_prefix}/lib MANDIR=%{_mandir} EXTRALDFLAGS="$(echo %{ldflags} |sed -e 's,-m64,,g') -m32" user
cd ..
%endif

export LD_LIBRARY_PATH="$(pwd)/lib"
%make CC="%{__cc}" PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_libdir} MANDIR=%{_mandir} EXLDFLAGS="%{ldflags}" \
	PROG_EXTRA=sensord user

%install
%if %{with compat32}
cd build32
make CC="gcc -m32" PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_prefix}/lib MANDIR=%{_mandir} \
	DESTDIR=%{buildroot} user_install
rm -f %{buildroot}%{_prefix}/lib/libsensors.a
cd ..
%endif
make PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_libdir} MANDIR=%{_mandir} PROG_EXTRA=sensord \
	DESTDIR=%{buildroot} user_install

rm %{buildroot}%{_libdir}/libsensors.a

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/sensors.d
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/lm_sensors
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/sensord
# (tpg) service files
install -p -m 644 prog/init/lm_sensors.service %{buildroot}%{_unitdir}
install -p -m 644 prog/init/sensord.service %{buildroot}%{_unitdir}
install -p -m 644 prog/init/fancontrol.service %{buildroot}%{_unitdir}

cat > README.omv << EOF
* To use this package, you will have to launch "sensors-detect" as root, and ask few questions.
  No need to modify startup files as shown at the end, all will be done.

* Special note for via686a and i2c-viapro :	if you don t see the values, you probably have a PCI conflict.
  It will be corrected in next kernel. Change the /etc/sysconfig/lm_sensors to use i2c-isa + via686a
  (or i2c-viapro + another sensor)
EOF


%files
%doc CHANGES CONTRIBUTORS README doc README.omv
%config(noreplace) %{_sysconfdir}/sensors3.conf
%config(noreplace) %{_sysconfdir}/sysconfig/sensord
%config(noreplace) %{_sysconfdir}/sysconfig/lm_sensors
%{_bindir}/sensors
%{_bindir}/sensors-conf-convert
%ifnarch ppc %{armx} %{mips} riscv64
%{_sbindir}/isadump
%{_sbindir}/isaset
%endif
%{_sbindir}/sensors-detect
%{_sbindir}/sensord
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_sbindir}/fancontrol
%{_sbindir}/pwmconfig
%{_unitdir}/*.service

%files -n %{libname}
%{_libdir}/libsensors.so.%{major}*

%files -n %{devname}
%{_libdir}/libsensors.so
%dir %{_includedir}/sensors
%{_includedir}/sensors/*
%{_mandir}/man3/*

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libsensors.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/libsensors.so
%endif
