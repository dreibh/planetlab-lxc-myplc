Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://cvs.planet-lab.org/cvs/myplc

Summary: PlanetLab Central (PLC) Portable Installation
Name: myplc
Version: 0.5
Release: 5%{?pldistro:.%{pldistro}}%{?date:.%{date}}
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

%prep
%setup -q

%build
pushd MyPLC
./build.sh
popd

%install
rm -rf $RPM_BUILD_ROOT

pushd MyPLC

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
* Fri Jan 19 2007 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.5-3
- Split off myplc-devel into separate spec file, so that it can be
  built standalone.

* Tue Aug 22 2006 Mark Huang <mlhuang@CS.Princeton.EDU> - 0.4-3, 0.5-3
- MyPLC 0.4 RC3.
- Fix upgrade path from RC1.
- Always regenerate plc_config.xml at first startup
- Upgrade kernel, iptables, vnet to 2.6.17-1.2142_FC4-3.planetlab
- Minor PlanetFlow fixes
- pl_mom/swapmon: Minor fixes
- bootcd: Added Supermicro IPMI support
- bootmanager: Cleanup, fixed check for new disks

* Wed Aug 09 2006 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr>
- introduces variable %{build_devel} to allow custom sites to skip building
  the myplc-devel package.

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

