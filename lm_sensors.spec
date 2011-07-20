%define lib_name_orig   lib%{name}
%define major 4
%define libname %mklibname %{name} %major
%define develname %mklibname %{name} -d
%define staticname %mklibname %{name} -d -s

Summary:	Utilities for lm_sensors
Name:		lm_sensors
Version:	3.3.0
Release:	%mkrel 3
Epoch:		1
License:	LGPLv2+
Group:		System/Kernel and hardware
URL:		http://www.lm-sensors.org
Source0:	http://dl.lm-sensors.org/lm-sensors/releases/%{name}-%{version}.tar.bz2
Source1: lm_sensors.sysconfig
# these 2 were taken from PLD-linux, Thanks!
Source2: sensord.sysconfig
Source3: sensord.init
Patch0: lm_sensors-3.3.0-systemd.patch
Requires:	%{libname} = %{epoch}:%{version}-%{release}
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	flex
BuildRequires:	librrdtool-devel
BuildRequires:	libsysfs-devel
Requires(pre):	rpm-helper
Requires(postun):	rpm-helper
Requires(post): systemd-units
%ifarch %{ix86} x86_64
Requires: /usr/sbin/dmidecode
%endif
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

%prep
%setup -q
%patch0 -p0


%build
export CFLAGS="%{optflags}"
make PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir} EXLDFLAGS= \
  PROG_EXTRA=sensord user


%install
make PREFIX=%{_prefix} LIBDIR=%{_libdir} MANDIR=%{_mandir} PROG_EXTRA=sensord \
  DESTDIR=$RPM_BUILD_ROOT user_install
rm $RPM_BUILD_ROOT%{_libdir}/libsensors.a

ln -s sensors.conf.5.gz $RPM_BUILD_ROOT%{_mandir}/man5/sensors3.conf.5.gz

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sensors.d
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT/lib/systemd/system
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/lm_sensors
install -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/sensord
install -p -m 755 %{SOURCE3} $RPM_BUILD_ROOT%{_initrddir}/sensord
ln -s $RPM_BUILD_ROOT%{_initrddir}/sensord $RPM_BUILD_ROOT%{_initrddir}/lm_sensors
install -p -m 644 prog/init/lm_sensors.service \
    $RPM_BUILD_ROOT/lib/systemd/system


# Note non standard systemd scriptlets, since reload / stop makes no sense
# for lm_sensors
%triggerun -- lm_sensors < 3.3.0-2
if [ -L /etc/rc3.d/S26lm_sensors ]; then
    /bin/systemctl enable lm_sensors.service >/dev/null 2>&1 || :
fi
/sbin/chkconfig --del lm_sensors

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable lm_sensors.service > /dev/null 2>&1 || :
fi

%_preun_service sensord

%post
%_post_service sensord

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGES CONTRIBUTORS README doc
%config(noreplace) %{_sysconfdir}/sensors3.conf
%{_initrddir}/sensord
%{_initrddir}/lm_sensors
%config(noreplace) %{_sysconfdir}/sysconfig/sensord
%config(noreplace) %{_sysconfdir}/sysconfig/lm_sensors
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
/lib/systemd/system/lm_sensors.service

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libsensors.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/libsensors.so
%dir %{_includedir}/sensors
%{_includedir}/sensors/*
%{_mandir}/man3/*
