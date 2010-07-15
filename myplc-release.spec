#
# $Id$
#
%define url $URL$

%define name myplc-release
%define version 5.0
%define taglevel 9

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Summary: PlanetLab Central (PLC) release file
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

%define debug_package %{nil}

%description 
This package contains in /etc/myplc-release the details of the
contents of that release. This is used by the GetPlcRelease API call.

%prep
%setup -q

%build

# fetch the release stamp from the build if any
if [ -f ../../myplc-release ] ; then
  cp ../../myplc-release myplc-release
else
  echo "Cannot find release information." > myplc-release
  date >> myplc-release
  echo "$HeadURL$" >> myplc-release
fi

%install
rm -rf $RPM_BUILD_ROOT
# install it in /etc/myplc-release 
install -D -m 444 myplc-release ${RPM_BUILD_ROOT}/etc/myplc-release

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/myplc-release

%changelog
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

* Fri May 15 2009 Thierry Parmentelat <thierry.parmentelat@sophia.inria.fr> - MyPLC-4.3-10
- tighter right permissions on site_admin's authorized keys for more robustness

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
- plc.d/httpd: only update httpd_conf with /data for chroot'ed MyPLC
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


%define module_current_branch 4.3
