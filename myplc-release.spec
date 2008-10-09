#
# $Id$
#
%define url $URL$

%define name myplc-release
%define version 5.0
%define taglevel 1

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
rm -rf $RPM_BUILD_ROOT

# fetch the release stamp from the build if any
if [ -f ../../../myplc-release ] ; then
  cp ../../../myplc-release myplc-release
else
  echo "Cannot find release information." > myplc-release
  date >> myplc-release
  echo "$HeadURL$" >> myplc-release
fi
# install it in /etc/myplc-release 
install -m 444 myplc-release ${RPM_BUILD_ROOT}/etc/myplc-release

%install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/myplc-release

%changelog
