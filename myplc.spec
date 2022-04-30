%define name myplc
%define version 7.1
%define taglevel 0

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}


Name: %{name}
Version: %{version}
Release: %{release}
License: PlanetLab
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab %{plrelease}
URL: %{SCMURL}

%define nodefamily %{pldistro}-%{distroname}-%{_arch}


####################### myplc - mostly a meta-package
Summary: PlanetLab Central (PLC) Portable Installation
Group: Applications/Systems

# planetlab stuff
Requires: myplc-docs
Requires: myplc-release
Requires: myplc-core
Requires: createrepo
## serverside only
#Requires: bootmanager
#Requires: bootcd-%{nodefamily}
#Requires: bootcd-initscripts
#Requires: nodeimage-%{nodefamily}
#Requires: nodeconfig
#Requires: nodeyum
Requires: www-register-wizard


# starting with f16 we depend on this new rpm
%if "%{distro}" == "Fedora" && %{distrorelease} >= 16
Requires: rpm-sign
%endif


%description
MyPLC is a complete PlanetLab Central (PLC) portable installation.
The default installation consists of a web server, an XML-RPC API
server, a boot server, and a database server: the core components of
PLC. The installation may be customized through a graphical
interface. All PLC services are started up and shut down through a
single System V init script.


####################### myplc-core
# Warning: it appears that Requires should come here
# BEFORE the %description thingy

%package core

Summary: core contents of myplc with API + db + www UI

# as much as possible, requires should have gone
# with the individual packages, but well
Requires: myplc-config
Requires: plcapi
Requires: plewww

# this technically is a plcapi dependency
# but it's simpler here for chosing which
Requires: python3-mod_wsgi

# this technically is a plewww dependency
# starting with f27 we depend on this new rpm
%if "%{distro}" == "Fedora" && %{distrorelease} >= 27
Requires: php-fpm
%endif

Requires: redhat-lsb
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
Requires: python3-devel
Requires: dnf
#Requires: PyXML
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
Requires: ed
Requires: cronie


%description core
The core of myplc is about its API + database + web interface.
Installing this will not require any node-oriented
package, like bootcd, nodeimage, or bootmanager.

####################### myplc-config

%package config

Summary: PlanetLab Central (PLC) configuration python module
Group: Applications/Systems
Requires: python3

%description config
This package provides the Python module to configure MyPLC.



%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

# Install configuration scripts
echo "* Installing plc_config.py in %{python3_sitelib}"
install -D -m 755 plc_config.py ${RPM_BUILD_ROOT}/%{python3_sitelib}/plc_config.py

echo "* Installing scripts in /usr/bin"
mkdir -p ${RPM_BUILD_ROOT}/usr/bin
rsync -av --exclude .svn bin/ ${RPM_BUILD_ROOT}/usr/bin/
(cd $RPM_BUILD_ROOT/usr/bin; ln -s mtail.py mtail)
chmod 755 ${RPM_BUILD_ROOT}/usr/bin/*

# Install initscript
echo "* Installing plc initscript"
install -D -m 755 systemd/plc-ctl ${RPM_BUILD_ROOT}/usr/bin/plc-ctl
install -D -m 644 systemd/plc.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/plc.service

# Install initscripts
echo "* Installing plc.d initscripts"
find plc.d | cpio -p -d -u ${RPM_BUILD_ROOT}/etc/
chmod 755 ${RPM_BUILD_ROOT}/etc/plc.d/*

# Install db-config.d files
echo "* Installing db-config.d files"
mkdir -p ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
cp db-config.d/* ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d
chmod 444 ${RPM_BUILD_ROOT}/etc/planetlab/db-config.d/*

# Extra scripts (mostly for mail and dns) not installed by myplc by default.  Used in production
echo "* Installing scripts in /etc/support-scripts"
mkdir -p ${RPM_BUILD_ROOT}/etc/support-scripts
cp support-scripts/* ${RPM_BUILD_ROOT}/etc/support-scripts
chmod 444 ${RPM_BUILD_ROOT}/etc/support-scripts/*

# copy initscripts to etc/plc_sliceinitscripts
mkdir -p ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts
cp plc_sliceinitscripts/* ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts
chmod 444 ${RPM_BUILD_ROOT}/etc/plc_sliceinitscripts/*

# Install configuration file
echo "* myplc: Installing configuration file"
install -D -m 444 plc_config.dtd ${RPM_BUILD_ROOT}/etc/planetlab/plc_config.dtd
sed -e "s,@PLDISTRO@,%{pldistro},g" -e "s,@FCDISTRO@,%{distroname},g" -e "s,@ARCH@,%{_arch},g" \
    default_config.xml > ${RPM_BUILD_ROOT}/etc/planetlab/default_config.xml
chmod 444 ${RPM_BUILD_ROOT}/etc/planetlab/default_config.xml

echo "* Installing bashrc convenience"
install -D -m 644 bashrc ${RPM_BUILD_ROOT}/usr/share/myplc/bashrc

# yumgroups.xml and yum repo : let noderepo handle that

%clean
rm -rf $RPM_BUILD_ROOT

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
systemctl enable plc

%if "%{distro}" == "Fedora" && %{distrorelease} >= 27
systemctl enable php-fpm
systemctl start  php-fpm
%endif

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
    systemctl disable plc
fi


%files
/usr/share/myplc/bashrc

%files core
%defattr(-,root,root,-)
/usr/lib/systemd/system/plc.service
/usr/bin/plc-ctl
/etc/plc.d
/etc/planetlab
/etc/plc_sliceinitscripts
/etc/support-scripts
# keep a detailed list, to avoid duplicate of plc-config,
# that belongs to the myplc-config rpm
/usr/bin/plc-config-tty
/usr/bin/db-config
/usr/bin/dns-config
/usr/bin/refresh-peer.py*
/usr/bin/mtail.py*
/usr/bin/mtail
/usr/bin/plc-map.py*
/usr/bin/plc-kml.py*
/usr/bin/clean-empty-dirs.py*
/usr/bin/plc-check-ssl-peering.py*
/usr/bin/plc-orphan-accounts.py*
/usr/bin/spot-aliens.py*
/usr/bin/check-hrns.py*
/usr/bin/check-vsys-defaults.py*
/usr/bin/spot-dup-accounts.sh


%files config
%defattr(-,root,root,-)
/usr/bin/plc-config
%{python3_sitelib}/plc_config.py*
%exclude %{python3_sitelib}/__pycache__/*.pyc

%changelog
* Sat Apr 30 2022 Thierry Parmentelat <thierry.parmentelat@inria.fr> - myplc-7.1-0
- ready on f35

* Mon Jan 07 2019 Thierry Parmentelat <thierry.parmentelat@inria.fr> - myplc-7.0-0
- suitable for python3 on both f27 and f29

* Sun Jul 16 2017 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.3-4
- takes care of creating plcapi log file

* Wed Feb 18 2015 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.3-3
- tweaked renew_reminder for federation

* Fri Mar 21 2014 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.3-2
- tweaks in check-hrns.py
- do not require PyXML any more

* Tue Dec 10 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.3-1
- review check-hrns for plcapi-5.3
- add PLC_HRN_ROOT in usual plc-config-tty's settings

* Thu Oct 10 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.2-5
- reduce the scope of check-hrns.py script, now that the SFA layer handles this natively
- add an rpm-sign dependency on feedora>=16

* Fri Jun 28 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.2-4
- drop PLC_OMF_XMPP_{USER,PASSWORD} from config

* Tue Apr 23 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.2-3
- plc.d/gpg now does not rm /dev/random but preserves it
- this is because libvirt won't let us run mknod

* Wed Apr 10 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.2-2
- fix typo in check-hrns - used to print 'host' while dealing with persons

* Thu Mar 07 2013 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.2-1
- supports httpd config for either mod_python (preferred) or mod_wsgi
- requires mod_wsgi on f18 only, otherwise mod_python
- supports httpd config for apache 2.4 (f18)
- new config variable PLC_FLAVOUR_VIRT_MAP to set 'virt' from fcdistro

* Wed Dec 19 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-6
- bugfix in check-vsys-defaults.py

* Wed Dec 19 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-5
- define open_basedir in php.ini to stop confidentiality leak
- new utility slice_ssh_keys.py for showing sliver keys (OMF interop)
- new config setting PLC_VSYS_DEFAULTS for vsys tags granted to all
- new utilities check-hrns.py and check-vsys-defaults.py

* Fri Aug 31 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-4
- set TimeoutSec to 300 in plc.service
- remove ref to deprecated svn $URL$ in db-config usage

* Mon Jul 09 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-3
- expose mtail.py as simply mtail

* Mon May 07 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-2
- plc-kml.py now has support for nodegroups

* Mon Apr 16 2012 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.1-1
- use nodeimage package instead of deprecated bootstrapfs
- has systemd-friendly startup script
- plc_reload moved to functions/ - no more service plc reload
- no svn keywords anymore

* Mon Sep 26 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-19
- new maintenance/monitoring script spot-aliens to look for glitches in refreshpeer+sfa

* Tue Jun 07 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-18
- new settings for myslice (comon&tophat) and monitor (db)
- removed mentions of chroot in description
- can redo myplc-docs on broken f12-latex
- set short_open_tag in php.ini
- fixes in gen-sites-xml (is that still used ?)
- partial-repo.sh has moved to 'build' where it more belongs
- tweaks in convenience tool 'mtail'

* Tue Mar 22 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-17
- fixed changelog, no change from 5.0-16

* Mon Mar 21 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-16
- requires ed for the plc.d/packages step
- sirius initscript to handle stop and restart

* Fri Feb 04 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-15
- ignore steps in db-config.d if they have a '.' or '~' in their name

* Wed Jan 26 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-14
- can redo myplc-docs without the doc for monitor

* Mon Jan 24 2011 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-13
- no semantic change - just fixed specfile for git URL

* Wed Dec 01 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-12
- needed for plcapi-5.0-19, i.e. tag permissions based on roles

* Mon Oct 04 2010 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - myplc-5.0-11
- add missing files to rpm package

* Mon Oct 04 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-10
- mtail.py -s for SFA
- spot-aliesm.py is a utility script for sanity checks of the PLC db when running refreshpeer+sfa

* Thu Jul 15 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-9
- avoid duplication of the plc-config binary in both myplc and myplc-config rpms

* Mon Jul 12 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - myplc-5.0-8
- plc-config-tty now has a validator on booleans
- e.g. entering 'True' now is rejected rather than silently recording 'false'

* Tue Jul 06 2010 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - MyPLC-5.0-7
- disable mod_wsgi

* Mon Jul 05 2010 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - MyPLC-5.0-6
- module name changes
- start wsgi support

* Tue Jun 22 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-5
- new setting PLC_RESERVATION_GRANULARITY

* Wed May 12 2010 Talip Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - MyPLC-5.0-4
- * partial-repo.sh script
- * preserve key along with certificates

* Fri Apr 02 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-3
- set date.timezone to GMT if not set in php.ini for php-5.3 / fedora12

* Fri Mar 12 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-2
- legacy scripts gen-sites-xml & gen-static-content back in (sigh)
- new OMF category in the config
- create the drl system slice

* Fri Jan 29 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-5.0-1
- first working version of 5.0:
- pld.c/, db-config.d/ and nodeconfig/ scripts should now sit in the module they belong to
- nodefamily is 3-fold with pldistro-fcdistro-arch
- new PLC_FLAVOUR config category
- reviewed module layout
- cleaned up old chroot-related build stuff (does not need the build module when building anymore)

* Sat Jan 09 2010 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-37
- support for fedora 12
- new package myplc-config for use by sfa
- drupal user registration turned off

* Thu Dec 31 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-36
- - fix to make sure when API, BOOT, MONITOR are on the same
- machine as WWW that the SSL key,cert for WWW takes precedence.
- - Do proper setup for SSL CA certficate to be used as the server
- chain.

* Wed Dec 23 2009 Marc Fiuczynski <mef@cs.princeton.edu> - MyPLC-4.3-35
- - Change sysctl.conf source to be PlanetLabConfsysctl.con rather than the php script.

* Tue Dec 22 2009 Baris Metin <Talip-Baris.Metin@sophia.inria.fr> - MyPLC-4.3-34
- depend on pcucontrol

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
- /etc/planetlab/db-config.d doesn''t exist
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

%define module_current_branch 4.3
