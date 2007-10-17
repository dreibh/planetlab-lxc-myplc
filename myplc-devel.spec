Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Development Environment
Name: myplc-devel
Version: 0.5
Release: 3%{?pldistro:.%{pldistro}}%{?date:.%{date}}
License: PlanetLab
Group: Development/Tools
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
AutoReqProv: no

%define debug_package %{nil}

%description
This package installs a complete PlanetLab development environment
contained within a chroot jail. The default installation consists of
all the tools necessary to compile MyPLC.

%prep
%setup -q

%build
pushd MyPLC
./build_devel.sh
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd MyPLC

# Install host startup script and configuration file
install -D -m 755 host.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/plc-devel
install -D -m 644 plc-devel.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/plc-devel

# Install root filesystem
install -d -m 755 $RPM_BUILD_ROOT/plc/devel/root
install -D -m 644 devel/root.img $RPM_BUILD_ROOT/plc/devel/root.img

# Install data directory
find devel/data | cpio -p -d -u $RPM_BUILD_ROOT/plc/

popd

%clean
rm -rf $RPM_BUILD_ROOT

# If run under sudo
if [ -n "$SUDO_USER" ] ; then
    # Allow user to delete the build directory
    chown -h -R $SUDO_USER .
    # Some temporary cdroot files like /var/empty/sshd and
    # /usr/bin/sudo get created with non-readable permissions.
    find . -not -perm +0600 -exec chmod u+rw {} \;
    # Allow user to delete the built RPM(s)
    chown -h -R $SUDO_USER %{_rpmdir}/%{_arch}
fi

%pre
if [ -x %{_sysconfdir}/init.d/plc-devel ] ; then
    %{_sysconfdir}/init.d/plc-devel stop
fi

%post
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc-devel
    /sbin/chkconfig plc-devel on
fi

%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
    %{_sysconfdir}/init.d/plc-devel stop
    if [ -x /sbin/chkconfig ] ; then
        /sbin/chkconfig plc-devel off
	/sbin/chkconfig --del plc-devel
    fi
fi

%files
%defattr(-,root,root,-)
# Host startup script and configuration file
%{_sysconfdir}/init.d/plc-devel
%{_sysconfdir}/sysconfig/plc-devel

# Root filesystem
/plc/devel/root.img
/plc/devel/root

# Data directory
%dir /plc/devel/data
%config(noreplace) /plc/devel/data/*

%changelog
* Fri Jan 19 2007 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.5-3
- Initial build.
