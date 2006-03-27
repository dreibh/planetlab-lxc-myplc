# Fedora Core release version to base the installation on. Currently
# supported: 2, 4.
%define releasever 2

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 3.0
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Portable Installation
Name: myplc
Version: %{releasever}.0
Release: 1
License: BSD
Group: Applications/Systems
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%define debug_package %{nil}

%description
MyPLC is a complete PlanetLab Central (PLC) portable installation
contained within a chroot jail. The default installation consists of a
web server, an XML-RPC API server, a boot server, and a database
server: the core components of PLC. The installation may be customized
through a graphical interface. All PLC services are started up and
shut down through a single System V init script installed in the host
system.

%prep
%setup -q

%build
cd myplc
./build.sh -r %{releasever} -d %{_datadir}

# If run under sudo, allow user to delete the build directory
if [ -n "$SUDO_USER" ] ; then
    chown -R $SUDO_USER .
    # Some temporary chroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
fi

%install
rm -rf $RPM_BUILD_ROOT

cd myplc
install -d -m 755 $RPM_BUILD_ROOT/%{_datadir}/plc/fc%{releasever}
install -D -m 644 fc%{releasever}.img $RPM_BUILD_ROOT/%{_datadir}/plc/fc%{releasever}.img
find data%{releasever} | cpio -p -d -u $RPM_BUILD_ROOT/%{_datadir}/plc/
install -D -m 755 host.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/plc
install -D -m 644 plc.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/plc

%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo, allow user to delete the built RPM
if [ -n "$SUDO_USER" ] ; then
    chown $SUDO_USER %{_rpmdir}/%{_arch}/%{name}-%{version}-%{release}.%{_arch}.rpm
fi

%post
chkconfig --add plc
chkconfig plc on

%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
    chkconfig plc off
    chkconfig --del plc
fi

%files
%defattr(-,root,root,-)
%dir %{_datadir}/plc/fc%{releasever}
%{_datadir}/plc/fc%{releasever}.img
%{_datadir}/plc/data%{releasever}
%{_sysconfdir}/init.d/plc
%{_sysconfdir}/sysconfig/plc

%changelog
* Fri Mar 17 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.1-1
- Initial build.

