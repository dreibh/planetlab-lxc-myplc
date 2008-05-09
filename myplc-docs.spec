#
# $Id: myplc-native.spec 9260 2008-05-07 16:20:25Z thierry $
#
%define url $URL: svn+ssh://thierry@svn.planet-lab.org/svn/MyPLC/trunk/myplc-native.spec $

%define name myplc-docs
%define version 4.2
%define taglevel 10

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
This package contains the online documentation for MyPLC. This covers
the overall system itself, together with the reference manuals for the
two APIs provided, namely PLCAPI and NMAPI.

%prep
%setup -q

%build
rm -rf $RPM_BUILD_ROOT

pushd MyPLC
# beware that making the pdf file somehow overwrites the html
make -C doc myplc.pdf 
rm -f doc/myplc.html
make -C doc myplc.html 
popd

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

%install

for ext in pdf html; do
    install -D -m 444 MyPLC/doc/myplc.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/myplc.$ext
    install -D -m 444 PLCAPI/doc/PLCAPI.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.$ext
    install -D -m 444 NodeManager/doc/NMAPI.$ext $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.$ext
done

./MyPLC/doc/docbook2drupal.sh "MyPLC Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/myplc.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/myplc.php 
./MyPLC/doc/docbook2drupal.sh "PLC API Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/PLCAPI.php 
./MyPLC/doc/docbook2drupal.sh "Node Manager API Documentation (%{pldistro})" \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.html \
    $RPM_BUILD_ROOT/var/www/html/planetlab/doc/NMAPI.php 

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/var/www/html/planetlab/doc/

%changelog
