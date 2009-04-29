#
# $Id$
#
%define url $URL$

%define name myplc-release
%define version 4.3
%define taglevel 6

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

