%define lib_name_orig         lib%{name}
%define lib_major             4
%define lib_name              %{mklibname %{name} %{lib_major}}
%define lib_name_devel        %{mklibname %{name} -d}
%define lib_name_static_devel %{mklibname %{name} -d -s}

Summary:        Utilities for lm_sensors
Name:           lm_sensors
Version:        3.0.0
Release:        %mkrel 2
License:        GPL
Group:          System/Kernel and hardware
URL:            http://www.lm-sensors.nu/
Source0:        http://dl.lm-sensors.org/lm-sensors/releases/lm_sensors-%{version}.tar.bz2
Source1:        http://dl.lm-sensors.org/lm-sensors/releases/lm_sensors-%{version}.tar.bz2.sig
Source2:        lm_sensors.init
Provides:       lm_utils = %{version}-%{release}
Obsoletes:      lm_utils < %{version}-%{release}
Requires:       perl
Requires(pre):  rpm-helper
Requires(postun): rpm-helper
Requires:       %{lib_name} >= %{version}
BuildRequires:  bison
BuildRequires:  chrpath
BuildRequires:  flex
BuildRequires:  kernel-source
BuildRequires:  librrdtool-devel
BuildRequires:  libsysfs-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

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

%package -n %{lib_name}
Summary:        Libraries needed for lm_sensors
Group:          System/Libraries
Provides:       %{lib_name} = %{version}-%{release}

%description -n %{lib_name}
Libraries to access lm_sensors internal data.

%package -n %{lib_name_devel}
Summary:        Development libraries and header files for lm_sensors
Group:          Development/C
Requires(pre): %{lib_name} = %{version}-%{release}
Requires(postun): %{lib_name} = %{version}-%{release}
Requires:       %{lib_name} = %{version}-%{release}
Provides:       %{_lib}%{name}-devel = %{version}-%{release}
Provides:       %{lib_name_orig}-devel = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Obsoletes:      %{name}-devel < %{version}-%{release}
Conflicts:      %{mklibname %{name} 3}-devel

%description -n %{lib_name_devel}
Development libraries and header files for lm_sensors.

You might want to use this package while building applications that might
take advantage of lm_sensors if found.

%package -n %{lib_name_static_devel}
Summary:        Static libraries for lm_sensors
Group:          Development/C
Requires(pre):  %{lib_name_devel} = %{version}-%{release}
Requires(postun): %{lib_name_devel} = %{version}-%{release}
Provides:       %{lib_name_orig}-static-devel = %{version}-%{release}
Conflicts:      %{mklibname %{name} 3}-static-devel

%description -n %{lib_name_static_devel}
This package contains static libraries for lm_sensors.

%prep
%setup -q

%{__cat} > README.urpmi << EOF
* To use this package, you'll have to launch "sensors-detect" as root, and answer a few questions.
  There is no need to modify startup files as shown at the end, all will be done for you.

* A special note for via686a and i2c-viapro: if you don t see the values, you probably have a PCI conflict.
  It will be corrected in next kernel. Change the %{_sysconfdir}/sysconfig/lm_sensors to use i2c-isa + via686a
  (or i2c-viapro + another sensor)
EOF

%build
%define _MAKE_DEFS COMPILE_KERNEL=0 WARN=1 PREFIX=%{_prefix} LINUX=%{_usrsrc}/linux I2C_HEADERS=%{_usrsrc}/linux/include ETCDIR=%{_sysconfdir} MANDIR=%{_mandir} PROG_EXTRA:=sensord LIBDIR=%{_libdir}
%define MAKE_DEFS %{_MAKE_DEFS}

%{make} %{MAKE_DEFS} user

%install
%{__rm} -rf %{buildroot}

%define MAKE_DEFS %{_MAKE_DEFS} DESTDIR=%{buildroot}

%{make} %{MAKE_DEFS} user_install

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__cp} -a %{SOURCE2} %{buildroot}%{_initrddir}/lm_sensors

%{_bindir}/chrpath -d %{buildroot}%{_bindir}/sensors
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/sensord

%ifnarch ppc
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/isadump
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/isaset
%endif

%clean
%{__rm} -rf %{buildroot}

%post -n %{lib_name} -p /sbin/ldconfig

%postun -n %{lib_name} -p /sbin/ldconfig

%post
%_post_service lm_sensors

%preun
%_preun_service lm_sensors

%files
%defattr(-,root,root)
%doc CHANGES CONTRIBUTORS COPYING INSTALL doc/ README.urpmi
%config(noreplace) %{_sysconfdir}/sensors3.conf
%attr(0755,root,root) %{_initrddir}/lm_sensors
%{_bindir}/sensors
%{_bindir}/sensors-conf-convert
%ifnarch ppc
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

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/libsensors.so.*

%files -n %{lib_name_devel}
%defattr(-,root,root)
%{_libdir}/libsensors.so
%dir %{_includedir}/sensors
%{_includedir}/sensors/*
%{_mandir}/man3/*

%files -n %{lib_name_static_devel}
%defattr(-,root,root)
%{_libdir}/libsensors.a
