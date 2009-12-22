#
# $Id$
#
%define url $URL$

%define name myplc
%define version 4.3
%define taglevel 33

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Summary: PlanetLab Central (PLC) Portable Installation
Name: %{name}
Version: %{version}
Release: %{release}
License: PlanetLab
Group: Applications/Systems
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %(echo %{url} | cut -d ' ' -f 2)

# as much as possible, requires should go in the subpackages specfile
Requires: bzip2
Requires: tar 
Requires: less
Requires: sendmail
Requires: sendmail-cf
Requires: openssl
Requires: expect
Requires: php-pgsql
Requires: curl
Requires: rsync
Requires: python-devel
Requires: vixie-cron
Requires: yum
Requires: PyXML
Requires: createrepo
Requires: cpio
Requires: wget
Requires: php
Requires: openssh
Requires: dnsmasq
Requires: diffutils
Requires: gzip
Requires: vim-minimal
Requires: findutils
Requires: xmlsec1
Requires: xmlsec1-openssl
# planetlab stuff
Requires: bootmanager
Requires: bootcd-%{pldistro}-%{_arch}
Requires: PLCWWW
Requires: www-register-wizard
Requires: nodeconfig
Requires: PLCAPI
Requires: pcucontrol
Requires: bootstrapfs-%{pldistro}-%{_arch}
Requires: myplc-docs
Requires: myplc-release

# argh - ugly - we might wish to use something from build/config.%{pldistro} instead
%if "%{pldistro}" == "onelab"
Requires: dummynet_image
%endif

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

%install
pushd MyPLC
rm -rf $RPM_BUILD_ROOT
./build.sh %{pldistro} $RPM_BUILD_ROOT
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
    [ -d %{_rpmdir}/noarch ] && chown -h -R $SUDO_USER %{_rpmdir}/noarch
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
	if [ -d $dir ] ; then
	    echo "Preserving $dir"
	    mkdir -p $dir.rpmsave
	    tar -C $dir -cpf - . | \
	       tar -C $dir.rpmsave -xpf -

	    # Except for the default configuration file and DTD, which
	    # really should be considered for upgrade.
	    rm -f $dir.rpmsave/{default_config.xml,plc_config.dtd}
	fi
    done
fi

%post
if [ -x /sbin/chkconfig ] ; then
    /sbin/chkconfig --add plc
    /sbin/chkconfig plc on
fi
pushd /usr/share/myplc &> /dev/null
python plc_config.py build
python plc_config.py install
popd &> /dev/null

%triggerpostun -- %{name}
# 0 = erase, 1 = upgrade
if [ $1 -gt 0 ] ; then
    for dir in /var/lib/pgsql/data /etc/planetlab ; do
	if [ -d $dir.rpmsave -a -d $dir ] ; then
	    echo "Merging $dir"
	    if tar -C $dir.rpmsave -cpf - . | \
	       tar -C $dir -xpf - ; then
		rm -rf $dir.rpmsave
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
/etc/init.d/plc
/etc/plc.d
/etc/planetlab
/etc/plc_sliceinitscripts/sirius
/etc/support-scripts/gen_aliases.py*
/etc/support-scripts/renew_reminder.py*
/etc/support-scripts/renew_reminder_logrotate
/usr/bin/plc-config
/usr/bin/plc-config-tty
/usr/bin/db-config
/usr/bin/dns-config
/usr/bin/plc-map.py*
/usr/bin/plc-kml.py*
/usr/bin/refresh-peer.py*
/usr/bin/clean-empty-dirs.py*
/usr/bin/mtail.py*
/usr/bin/plc-check-ssl-peering.py*
/usr/bin/plc-orphan-accounts.py*
/usr/share/myplc

%changelog
* Fri Dec 18 2009 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - MyPLC-4.3-33
- * validate input according to type in plc_config
- * added the _genicw system slice
- * add tag types for sites and persons
- * add new tags for nodes and slices for exemption from myops

* Thu Nov 26 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-32
- turn off drupal on a box that acts as BOOT server but not as WWW server
- cleanup some obsolete code for old chroot-jail packaging in the process
- new bootcd-kernel script for keeping bootcd variants up2date

* Mon Nov 09 2009 Daniel Hokka Zakrisson <daniel@hozac.com> - MyPLC-4.3-31
- Make the /etc/hosts manipulation optional.

* Thu Nov 05 2009 Daniel Hokka Zakrisson <daniel@hozac.com> - MyPLC-4.3-30
- Fix SetRole.

* Tue Nov 03 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-29
- - Added "SetRole()" so that db-config.d/ scriplets can insert roles
- into the DB.
- - Added the root ssh key handling support back into plc.d/ssh and the
- default xml file.  This should be identical to the way it was in
- rc12.
- - Added support in the db-config.d/01-init script to register the root
- ssh public key with the default administrator.  In this way the root
- ssh key will make it into the root account on the nodes by means of
- NodeManager's specialaccounts plugin.

* Tue Oct 20 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-28
- db-config ignores sliver tags
- sirius's db-config script renamed (was sirious)

* Tue Oct 13 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-27
- fix for silverauth - missing tag types now created at plc startup time

* Fri Oct 09 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-26
- plc.d/ssl preserves SSL certificates when it thinkfs they're obsolete

* Wed Oct 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-25
- companion to NM's specialaccounts plugin
- do not generate /etc/planetlab/root_ssh_key* anymore
- remove related config. variables and conf_files

* Sun Sep 20 2009 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.3-24
- clarified description text to refer only to plcrt and not other optional
- packages.

* Sat Sep 19 2009 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.3-23
- fixed a bug setting slice multiple attributes with the same tag name

* Mon Sep 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-22
- SSL setup for monitor box, and related new config variables
- new conf_file for /etc/planetlab/extensions
- various tweaks in db-config internals, about initscripts among others
- also more messages defined in the db

* Tue Jul 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-21
- create node tags, like e.g. 'arch', that were not handled with 4.3-20

* Tue Jul 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-20
- bugfix in db-config, tag 4.3-19 would not fly

* Mon Jul 06 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-19
- Refactored db-config into snippets in db-config.d/.

* Thu Jul 02 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-18
- oops, tag 4.3-17 was broken and would not work

* Wed Jul 01 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-17
- bugfix - escape sequences inserted in xml configs

* Fri Jun 26 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-16
- Handle db-config.d files properly.

* Tue Jun 23 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-15
- - Fix /etc/init.d/plc to have command usage show up on the tty rather
- than the log file
- - Fix db-config to be a bit more cautious when
- /etc/planetlab/db-config.d doesn't exist
- - Clean up db-config approach to ignore .bak, *~, .rpm{save,new}, and
- .orig files.
- - Refactor generic plc-config-tty code into plc_config.py.
- plc-config-tty now contains MyPLC specific paths, "usual" variables,
- and the list of validated variables and the corresponding
- validator() function. This refactoring lets one reuse plc_config.py
- as a generic cmdline configuration tool for highly customer MyPLC
- like software.

* Mon Jun 15 2009 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.3-14
- update PCU Type descriptions.
- updates to init scripts

* Wed Jun 03 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-13
- requires monitor-pcucontrol so register-wizard can work

* Tue May 26 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-12
- cleaned up plc-config-tty, no more need to configure plc-devel

* Tue May 19 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-11
- first draft of plc-orpha-accounts.py, and rename check-ssl-peering into plc-<>

* Wed May 06 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-9
- fix issue in db-config that prevented correct operation

* Wed May 06 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-8
- remove support for chroot-based packaging - no crond nor syslog step anymore
- plc init script now named plc.init instead of former guest.init

* Mon May 04 2009 Stephen Soltesz <soltesz@cs.princeton.edu> - MyPLC-4.3-7
- add Monitor to docs build

* Wed Apr 29 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-6
- plc_config.py and plc-config-tty: generalized to work for more diverse
- MyPLC configurations.
- plc.d/httpd: only update httpd_conf with /data for chroot-ed MyPLC
- deployments and increase the memory limits in php.ini
- plc.d/crond: add --full option to vacuumdb

* Tue Apr 07 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-5
- avoid generating ssl certificates for disabled services among www api boot

* Mon Mar 30 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-4
- cleaned up old entries in db-config
- mtail more robust

* Tue Mar 24 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-3
- php include path tweaked for plekit includes
- reviewed myplc (fka native) packaging dependencies
- renumbered 4.3

* Thu Jan 29 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-2
- rename myplc into myplc-chroot and myplc-native into myplc
- new settings (shortname & hrn_root) for local peer

* Wed Sep 10 2008 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-1
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

* Fri Aug 31 2007 Marc E. Fiuczynski <mef@CS.Princeton.EDU>
- initial build.

%define module_current_branch 4.2
