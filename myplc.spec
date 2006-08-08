Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Portable Installation
Name: myplc
Version: 0.5
Release: 2%{?pldistro:.%{pldistro}}%{?date:.%{date}}
License: PlanetLab
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

%package devel
Summary: PlanetLab Central (PLC) Development Environment
Group: Development/Tools
AutoReqProv: no

%description devel
This package install a complete PlanetLab development environment
contained within a chroot jail. The default installation consists of a
local CVS repository bootstrapped with a snapshot of all PlanetLab
source code, and all the tools necessary to compile it.

%prep
%setup -q

%build
pushd myplc
./build_devel.sh %{?cvstag:-t %{cvstag}}
./build.sh %{?cvstag:-t %{cvstag}}
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd myplc

#
# myplc
#

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

#
# myplc-devel
#

# Install host startup script and configuration file
install -D -m 755 host.init $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/plc-devel
install -D -m 644 plc-devel.sysconfig $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/plc-devel

# Install root filesystem
install -d -m 755 $RPM_BUILD_ROOT/plc/devel/root
install -D -m 644 devel/root.img $RPM_BUILD_ROOT/plc/devel/root.img

# Install data directory
find devel/data | cpio -p -d -u $RPM_BUILD_ROOT/plc/

# Make sure /cvs is never upgraded once installed by giving it a
# unique name. A hard-linked copy is made in %post.
mv $RPM_BUILD_ROOT/plc/devel/data/{cvs,cvs-%{version}-%{release}}

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
    %{_sysconfdir}/init.d/plc stop
fi

# Old versions of myplc used to ship with a bootstrapped database and
# /etc/planetlab directory. Including generated files in the manifest
# was dangerous; if /plc/data/var/lib/pgsql/data/base/1/16676 changed
# names from one RPM build to another, it would be rpmsaved and thus
# effectively deleted. Now we do not include these files in the
# manifest. However, to avoid deleting these files in the process of
# upgrading from one of these old versions of myplc, we must back up
# the database and /etc/planetlab and restore them after the old
# version has been uninstalled in %triggerpostun (also in %post, in
# case we are force upgrading to the same version).
#
# This code can be removed once all myplc-0.4-1 installations have
# been upgraded to at least myplc-0.4-2.

# 0 = install, 1 = upgrade
if [ $1 -gt 0 ] ; then
    for dir in /var/lib/pgsql/data /etc/planetlab ; do
	if [ -d /plc/data/$dir ] ; then
	    echo "Preserving /plc/data/$dir"
	    mkdir -p /plc/data/$dir.rpmsave
	    tar -C /plc/data/$dir -cpf - . | \
	       tar -C /plc/data/$dir.rpmsave -xpf -

	    # Except for the default configuration file and DTD, which
	    # really should be considered for upgrade.
	    rm -f /plc/data/$dir.rpmsave/{default_config.xml,plc_config.dtd}
	fi
    done
fi

%post
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc
    /sbin/chkconfig plc on
fi

# Force a regeneration to take into account new variables
touch /plc/data/etc/planetlab/default_config.xml

%triggerpostun -- %{name}
# 0 = erase, 1 = upgrade
if [ $1 -gt 0 ] ; then
    for dir in /var/lib/pgsql/data /etc/planetlab ; do
	if [ -d /plc/data/$dir.rpmsave -a -d /plc/data/$dir ] ; then
	    echo "Merging /plc/data/$dir"
	    if tar -C /plc/data/$dir.rpmsave -cpf - . | \
	       tar -C /plc/data/$dir -xpf - ; then
		rm -rf /plc/data/$dir.rpmsave
	    fi
	fi
    done
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

%pre devel
if [ -x %{_sysconfdir}/init.d/plc-devel ] ; then
    %{_sysconfdir}/init.d/plc-devel stop
fi

%post devel
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc-devel
    /sbin/chkconfig plc-devel on
fi

# If /cvs does not already exist, make a hard-linked copy of this
# version's /cvs repository.
if [ ! -d /plc/devel/data/cvs ] ; then
    cp -rl /plc/devel/data/{cvs-%{version}-%{release},cvs}
fi

%preun devel
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

%files devel
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
* Thu Jul 13 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.4-2, 0.5-2
- MyPLC 0.4 RC2.
- Fix many spec files (License replaces Copyright).
- Fix kernel build under gcc32 (module verification bug).
- Fix vnet build under gcc32
- Fix PlanetFlow. MySQL RPM postinstall script no longer starts the
  server. Also, get hostnames list from PLC_WWW_HOST, not
  www.planet-lab.org.
- Fix pl_mom/bwmon to use cached values if NM is unresponsive
- Fix pl_mom/swapmon reset logic to avoid endless loops
- Remove ksymoops, add kernel-smp to standard PlanetLab package group
- Add kernel-smp boot support to bootmanager
- Add badblock search support to bootmanager
- Build development environment (myplc-devel). Add support for
  building myplc itself inside myplc-devel.
- Move step-specific initialization to appropriate plc.d scripts
- Fix postgresql startup failure when bootstrapping
- Allow CA to be configured for each SSL certificate set. Stop doing
  root CA stuff, this is outside the scope of MyPLC. MyPLC now only
  generates self-signed certificates, but supports replacement of the
  self-signed certificates with real certifcates signed by another CA,
  as long as the CA is specified.
- Self-sign the MA/SA SSL certificate (and by extension, the MA/SA API
  certificate).
- pl_mom: Workarounds for when NM queries time out.
- plc_api: Honor PLC_MAIL_ENABLED.

* Wed Jul  6 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.4-1, 0.5-1
- First stable release of MyPLC 0.4 RC1.

* Wed Apr  5 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.2-1
- Basic functionality complete. Consolidate into a single package
  installed in /plc.

* Fri Mar 17 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.1-1
- Initial build.

