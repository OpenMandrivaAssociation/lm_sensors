%define lib_name_orig   lib%{name}
%define lib_major       3
%define lib_name        %mklibname %{name} %{lib_major}
%define kversion        2.6.22

Summary:        Utilities for lm_sensors
Name:           lm_sensors
Version:        2.10.8
Release:        %mkrel 1
Epoch:          1
License:        GPL
Group:          System/Kernel and hardware
URL:            http://www.lm-sensors.nu/
Source0:        ftp://ftp.netroedge.com/pub/lm-sensors/lm_sensors-%{version}.tar.gz
Source1:        ftp://ftp.netroedge.com/pub/lm-sensors/lm_sensors-%{version}.tar.gz.asc
Source2:        lm_sensors-2.8.2-sensors
Patch0:         lm_sensors-2.9.1-misleading_error_message.patch
Provides:       lm_utils = %{epoch}:%{version}-%{release}
Obsoletes:      lm_utils < %{epoch}:%{version}-%{release}
Requires:       perl
Requires(pre):  rpm-helper
Requires(postun): rpm-helper
Requires:       %{lib_name} = %{epoch}:%{version}-%{release}
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
Provides:       %{lib_name} = %{epoch}:%{version}-%{release}

%description -n %{lib_name}
Libraries to access lm_sensors internal data.

%package -n %{lib_name}-devel
Summary:        Development libraries and header files for lm_sensors
Group:          Development/C
Requires(pre): %{lib_name} = %{epoch}:%{version}-%{release}
Requires(postun): %{lib_name} = %{epoch}:%{version}-%{release}
Requires:       %{lib_name} = %{epoch}:%{version}-%{release}
Provides:       %{_lib}%{name}-devel = %{epoch}:%{version}-%{release}
Provides:        %{lib_name_orig}-devel = %{epoch}:%{version}-%{release}
Provides:       %{name}-devel = %{epoch}:%{version}-%{release}
Obsoletes:      %{name}-devel < %{epoch}:%{version}-%{release}

%description -n %{lib_name}-devel
Development libraries and header files for lm_sensors.

You might want to use this package while building applications that might
take advantage of lm_sensors if found.

%package -n %{lib_name}-static-devel
Summary:        Static libraries for lm_sensors
Group:          Development/C
Requires(pre):  %{lib_name}-devel = %{epoch}:%{version}-%{release}
Requires(postun): %{lib_name}-devel = %{epoch}:%{version}-%{release}
Provides:       %{lib_name_orig}-static-devel = %{epoch}:%{version}-%{release}

%description -n %{lib_name}-static-devel
This package contains static libraries for lm_sensors.

%prep
%setup -q
%patch0 -p0 -b .misleading_error_message

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
%{__rm} %{buildroot}/usr/include/linux/i2c-dev.h
%{__rm} %{buildroot}/usr/include/linux/sensors.h
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/i2cget
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/i2cset
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/i2cdump
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/sensord
%{_bindir}/chrpath -d %{buildroot}%{_sbindir}/i2cdetect
%{_bindir}/chrpath -d %{buildroot}%{_bindir}/sensors
%ifnarch ppc
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
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%post
%_post_service lm_sensors

%preun
%_preun_service lm_sensors

%files
%defattr(-,root,root)
%doc BACKGROUND BUGS CHANGES CONTRIBUTORS INSTALL README TODO doc README.urpmi
%config(noreplace) %{_sysconfdir}/sensors.conf
%attr(0755,root,root) %{_initrddir}/lm_sensors
%{_bindir}/sensors
%{_bindir}/ddcmon
%{_sbindir}/i2cdetect
%{_sbindir}/i2cdump
%{_sbindir}/i2cget
%{_sbindir}/i2cset
%ifnarch ppc
%{_sbindir}/isadump
%{_sbindir}/isaset
%endif
%{_sbindir}/sensors-detect
%{_sbindir}/sensord
%{_mandir}/man1/*
%{_mandir}/man5/*
%{_mandir}/man8/*
%{_bindir}/decode-dimms.pl
%{_bindir}/decode-edid.pl
%{_bindir}/decode-vaio.pl
%{_bindir}/decode-xeon.pl
%{_sbindir}/fancontrol
%{_sbindir}/fancontrol.pl
%{_sbindir}/pwmconfig

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/libsensors.so.*

%files -n %{lib_name}-devel
%defattr(-,root,root)
%{_libdir}/libsensors.so
%dir %{_includedir}/sensors
%{_includedir}/sensors/*
%{_mandir}/man3/*

%files -n %{lib_name}-static-devel
%defattr(-,root,root)
%{_libdir}/libsensors.a
