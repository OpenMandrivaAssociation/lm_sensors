%define major 4
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

Summary:	Utilities for lm_sensors
Name:		lm_sensors
Epoch:		1
Version:	3.4.0
Release:	2
License:	LGPLv2+
Group:		System/Kernel and hardware
Url:		http://www.lm-sensors.org
Source0:	http://dl.lm-sensors.org/lm-sensors/releases/%{name}-%{version}.tar.bz2
Source1:	lm_sensors.sysconfig
# these 2 were taken from PLD-linux, Thanks!
Source2:	sensord.sysconfig
Patch0:		lm_sensors-3.3.5-add-ConditionVirtualization-no.patch
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	sysfsutils-devel
BuildRequires:	pkgconfig(librrd)
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
%ifarch %{ix86} x86_64
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

%prep
%setup -q
%apply_patches

%build
%setup_compile_flags

%make CC=%{__cc} PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_libdir} MANDIR=%{_mandir} EXLDFLAGS=%{ldflags} \
	PROG_EXTRA=sensord user

%install
make PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} LIBDIR=%{_libdir} MANDIR=%{_mandir} PROG_EXTRA=sensord \
	DESTDIR=%{buildroot} user_install

rm %{buildroot}%{_libdir}/libsensors.a

ln -s sensors.conf.5.gz %{buildroot}%{_mandir}/man5/sensors3.conf.5.gz

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/sensors.d
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/lm_sensors
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/sensord
# (tpg) service files
install -p -m 644 prog/init/lm_sensors.service %{buildroot}%{_unitdir}
install -p -m 644 prog/init/sensord.service %{buildroot}%{_unitdir}
install -p -m 644 prog/init/fancontrol.service %{buildroot}%{_unitdir}

cat > README.urpmi << EOF
* To use this package, you will have to launch "sensors-detect" as root, and ask few questions.
  No need to modify startup files as shown at the end, all will be done.

* Special note for via686a and i2c-viapro :	if you don t see the values, you probably have a PCI conflict.
  It will be corrected in next kernel. Change the /etc/sysconfig/lm_sensors to use i2c-isa + via686a
  (or i2c-viapro + another sensor)
EOF


%files
%doc CHANGES CONTRIBUTORS README doc README.urpmi
%config(noreplace) %{_sysconfdir}/sensors3.conf
%config(noreplace) %{_sysconfdir}/sysconfig/sensord
%config(noreplace) %{_sysconfdir}/sysconfig/lm_sensors
%{_bindir}/sensors
%{_bindir}/sensors-conf-convert
%ifnarch ppc %{arm} %{mips} aarch64
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
