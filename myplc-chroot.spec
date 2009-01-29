#
# $Id$
#
%define url $URL$

%define name myplc-chroot
%define version 5.0
%define taglevel 2

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Summary: PlanetLab Central (PLC) Portable Installation
Name: %{name}
Version: %{version}
Release: %{release}
License: PlanetLab
Group: Applications/Systems
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

Requires: tar

Provides: myplc

%define debug_package %{nil}

%description
MyPLC is a complete PlanetLab Central (PLC) portable installation
contained within a chroot jail. The default installation consists of a
web server, an XML-RPC API server, a boot server, and a database
server: the core components of PLC. All PLC services are started up and
shut down through a single System V init script installed in the host
system. The related Web Interface is now separately packaged
in the PLCWWW component. 

%prep
%setup -q

%build
pushd MyPLC
./build-chroot.sh %{pldistro}
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
    %{_sysconfdir}/init.d/plc safestop
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
    %{_sysconfdir}/init.d/plc safestop
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
* Thu Jan 29 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-2
- rename myplc into myplc-chroot and myplc-native into myplc
- new settings (shortname & hrn_root) for local peer

* Wed Sep 10 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-1
- First iteration of new data model
- Bunch of various fixes

* Tue May 20 2008 Faiyaz Ahmed <faiyaza@cs.princeton.edu> - MyPLC-4.2-15
- Removed proper ops from planetflow slice.

* Wed May 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-14
- myplc-native requires myplc-docs
- fixed doc build by locating locally installed DTDs at build-time

* Sun May 11 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-13
- turn myplc-docs off for now

* Sat May 10 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-12
- figures in doc package

* Fri May 09 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-11
- no more doc packaged outside of myplc-docs - doc/ cleaned up 
- chroot packaging does not have docs anymore
- 'cvs' and 'dev' not required from myplc-native anymore
- cosmetic change in kml output

* Thu May 08 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-10
- defaults for *_IP conf vars now void, expect more accurate /etc/hosts
- gethostbyname uses python rather than perl (hope this shrinks deps) 
- doc: reviewed myplc doc - deprecated everything related to myplc-devel
- doc: packaging doc in myplc-native (myplc&PLCAPI) & removed target files from svn
- make sync now works towards vserver-based myplc only 

* Mon May 05 2008 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.2-9
- 
- added vsys 'pfmount' script to the default netflow slice attributes.
- 

* Thu Apr 24 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-8
- plc.d/bootcd step altered for handling legacy bootcd smooth migration
- to new bootcd packaging

* Wed Apr 23 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-7
- changes needed for bootcd 4.2 : new, possible multiple, installation locations, and new rpm name

* Tue Apr 22 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-6
- packaging of mplc-release in myplc-native
- sudoers.php is new to PlanetLabConf (needs nodeconfig-4.2-4)
- resolv file in /etc/resolv.conf, not plc_resolv.conf
- improved sirius script
- remove the 'driver' node-network-setting that was unused, and new 'Multihome' category
- expires more properly set 

* Mon Apr 07 2008 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.2-4 MyPLC-4.2-5
- 

* Wed Mar 26 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.2-3 MyPLC-4.2-4
- renew_reminder script moved to support-scripts/
- gen-aliases script added in support-scripts/
- sirius initscript moved to plc_sliceinitscripts (formerly inlined in db-config)
- plc-map script : no javascript for googlemap anymore, see new plc-kml script instead
- nodefamily-aware (creates legacy symlink /var/www/html/install-rpms/planetlab)
- new native slice attributes 'capabilities', 'vsys' and 'codemux'
- new setting 'Mom list address' for sending emails to a separate destination
- starts rsyslogd/syslogd as appropriate
- expects nodeconfig package (former PlanetLabConf/ dir from PLCWWW)
- convenience generation of yum.conf in resulting image based on build/mirroring

* Thu Feb 14 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-4.2-2 myplc-4.2-3
- refresh-peer.py removed (duplicate with PLCAPI)
- plc.d/ scripts cleaned up
- sirius initscript updated
- slice auto renewal fixed

* Thu Jan 31 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-4.2-1 myplc-4.2-2
- knows how to checkpoint and restore
- packages step more robust, in particular with empty node repository
- miscell tweaks for native packaging

* Wed Jan 09 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-4.0-15 myplc-4.2-0
moving to 4.2 - no change

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


%define module_current_branch 4.2
