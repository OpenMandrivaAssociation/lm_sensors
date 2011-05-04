%define lib_name_orig   lib%{name}
%define major 4
%define libname %mklibname %{name} %major
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Summary:	Utilities for lm_sensors
Name:		lm_sensors
Version:	3.3.0
Release:	%mkrel 2
Epoch:		1
License:	GPLv2+
Group:		System/Kernel and hardware
URL:		http://www.lm-sensors.org
Source0:	http://dl.lm-sensors.org/lm-sensors/releases/%{name}-%{version}.tar.bz2
Source1:	%{SOURCE0}.sig
Source2:	lm_sensors-2.8.2-sensors
Requires:	%{libname} = %{epoch}:%{version}-%{release}
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	librrdtool-devel
BuildRequires:	libsysfs-devel
Requires(pre):	rpm-helper
Requires(postun):	rpm-helper
BuildRoot:      %{_tmppath}/%{name}-%{version}

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
Provides:	%{libname} = %{epoch}:%{version}-%{release}

%description -n %{libname}
Libraries to access lm_sensors internal data.

%package -n %{develname}
Summary:	Development libraries and header files for lm_sensors
Group:		Development/C
Requires(pre):	%{libname} = %{epoch}:%{version}-%{release}
Requires(postun):	%{libname} = %{epoch}:%{version}-%{release}
Requires:	%{libname} = %{epoch}:%{version}-%{release}
Provides:	lib%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel = %{epoch}:%{version}-%{release}
Obsoletes:	%{name}-devel < %{epoch}:%{version}-%{release}

%description -n %{develname}
Development libraries and header files for lm_sensors.

You might want to use this package while building applications that might
take advantage of lm_sensors if found.

%package -n %{staticname}
Summary:	Static libraries for lm_sensors
Group:		Development/C
Requires(pre):	%{develname} = %{epoch}:%{version}-%{release}
Requires(postun):	%{develname} = %{epoch}:%{version}-%{release}
Provides:	lib%{name}-static-devel = %{epoch}:%{version}-%{release}
Obsoletes:	%{name}-static-devel < %{epoch}:%{version}-%{release}

%description -n %{staticname}
This package contains static libraries for lm_sensors.

%prep
%setup -q

%build
%setup_compile_flags
%define _MAKE_DEFS COMPILE_KERNEL=0 WARN=1 PREFIX=%{_prefix} ETCDIR=%{_sysconfdir} MANDIR=%{_mandir} PROG_EXTRA:=sensord LIBDIR=%{_libdir}
%define MAKE_DEFS %{_MAKE_DEFS}

# (tpg) get rid of custom ldflags, rpath
sed -i -e 's/EXLDFLAGS :=.*/EXLDFLAGS :=$(LDFLAGS)/g' Makefile

%{make} %{MAKE_DEFS} user

%install
%{__rm} -rf %{buildroot}

%define MAKE_DEFS %{_MAKE_DEFS} DESTDIR=%{buildroot}

%{make} %{MAKE_DEFS} user_install
%{__mkdir_p} %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/lm_sensors
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/sensord
%{_bindir}/chrpath -d %{buildroot}%{_bindir}/sensors
%ifnarch ppc %arm %mips
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/isadump
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/isaset
%endif

%{__cat} > README.urpmi << EOF
* To use this package, you'll have to launch "sensors-detect" as root, and ask few questions.
  No need to modify startup files as shown at the end, all will be done.

* Special note for via686a and i2c-viapro : if you don t see the values, you probably have a PCI conflict.
  It will be corrected in next kernel. Change the /etc/sysconfig/lm_sensors to use i2c-isa + via686a
  (or i2c-viapro + another sensor)
EOF

%clean
%{__rm} -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%post
%_post_service lm_sensors

%preun
%_preun_service lm_sensors

%files
%defattr(-,root,root)
%doc CHANGES CONTRIBUTORS README doc README.urpmi
%config(noreplace) %{_sysconfdir}/sensors3.conf
%{_initrddir}/lm_sensors
%{_bindir}/sensors
%{_bindir}/sensors-conf-convert
%ifnarch ppc %arm %mips
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

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libsensors.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/libsensors.so
%dir %{_includedir}/sensors
%{_includedir}/sensors/*
%{_mandir}/man3/*

%files -n %{staticname}
%defattr(-,root,root)
%{_libdir}/libsensors.a
