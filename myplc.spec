Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 3.3
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Portable Installation
Name: myplc
Version: 0.5
Release: 1%{?pldistro:.%{pldistro}}%{?date:.%{date}}
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
pushd myplc
./build.sh
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd myplc

# Install host startup script and configuration file
install -D -m 755 host.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/plc
install -D -m 644 plc.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/plc

# Create convenient symlink
install -d -m 755 $RPM_BUILD_ROOT/%{_sysconfdir}
ln -sf /plc/data/etc/planetlab $RPM_BUILD_ROOT/%{_sysconfdir}/planetlab

# Install root filesystem
install -d -m 755 $RPM_BUILD_ROOT/plc/root
install -D -m 644 root.img $RPM_BUILD_ROOT/plc/root.img

# Install data directory
find data | cpio -p -d -u $RPM_BUILD_ROOT/plc/

popd

%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo
if [ -n "$SUDO_USER" ] ; then
    # Allow user to delete the build directory
    chown -R $SUDO_USER .
    # Some temporary cdroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
    # Allow user to delete the built RPM(s)
    chown -R $SUDO_USER %{_rpmdir}/%{_arch}
fi

%pre
if [ -x %{_sysconfdir}/init.d/plc ] ; then
    service plc stop
fi

%post
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc
    /sbin/chkconfig plc on
fi

%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
    %{_sysconfdir}/init.d/plc stop
    if [ -x /sbin/chkconfig ] ; then
        /sbin/chkconfig plc off
	/sbin/chkconfig --del plc
    fi
fi

%files
%defattr(-,root,root,-)
# Host startup script and configuration file
%{_sysconfdir}/init.d/plc
%{_sysconfdir}/sysconfig/plc

# Symlink to /etc/planetlab within data directory
%{_sysconfdir}/planetlab

# Root filesystem
/plc/root.img
/plc/root

# Data directory
%dir /plc/data
%config(noreplace) /plc/data/*

%changelog
* Wed Apr  5 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.2-1
- Basic functionality complete. Consolidate into a single package
  installed in /plc.

* Fri Mar 17 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.1-1
- Initial build.

