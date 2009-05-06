#
# $Id$
#
%define url $URL$

%define name myplc-docs
%define version 4.3
%define taglevel 9

%define release %{taglevel}%{?pldistro:.%{pldistro}}%{?date:.%{date}}

Summary: PlanetLab Central (PLC) online documentation
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

BuildRequires: docbook-dtds, docbook-utils-pdf

%define debug_package %{nil}

%description
This package contains the online documentation for MyPLC, i.e. the
reference manuals for the two APIs provided: PLCAPI and NMAPI. A
more general introduction to the MyPLC system can be found at
http://svn.planet-lab.org/wiki/MyPLCUserGuide

%prep
%setup -q

%build
rm -rf $RPM_BUILD_ROOT

pushd PLCAPI
# beware that making the pdf file somehow overwrites the html
make -C doc PLCAPI.pdf 
rm -f doc/PLCAPI.html
make -C doc PLCAPI.html 
popd

pushd NodeManager
# beware that making the pdf file somehow overwrites the html
make -C doc NMAPI.pdf 
rm -f doc/NMAPI.html
make -C doc NMAPI.html 
popd

pushd Monitor
# beware that making the pdf file somehow overwrites the html
make -C docs Monitor.pdf 
rm -f docs/Monitor.html
make -C docs Monitor.html 
popd

%install

for ext in pdf html; do
    install -D -m 444 PLCAPI/doc/PLCAPI.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.$ext
    install -D -m 444 NodeManager/doc/NMAPI.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.$ext
    install -D -m 444 Monitor/docs/Monitor.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/Monitor.$ext
done

./MyPLC/docbook2drupal.sh "PLC API Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.php 
./MyPLC/docbook2drupal.sh "Node Manager API Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.php 
./MyPLC/docbook2drupal.sh "Monitor API Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/Monitor.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/Monitor.php 

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/var/www/html/planetlab/doc/

%changelog
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


%define module_current_branch 4.2
