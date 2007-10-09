Vendor: PlanetLab
Packager: PlanetLab Central <support@planet-lab.org>
Distribution: PlanetLab 4.0
URL: http://svn.planet-lab.org/svn/MyPLC

Summary: PlanetLab Central (PLC) Development Environment
Name: myplc-devel-native
Version: 0.1
Release: 1%{?pldistro:.%{pldistro}}%{?date:.%{date}}
License: PlanetLab
Group: Development/Tools
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
AutoReqProv: no

Requires: beecrypt-devel
Requires: bzip2
Requires: coreutils
Requires: cpio
Requires: createrepo
Requires: curl
Requires: curl-devel
Requires: cvs
Requires: db4-devel
Requires: dev
Requires: diffutils
Requires: dnsmasq
Requires: docbook-utils-pdf
Requires: dosfstools
Requires: doxygen
Requires: expect
Requires: gcc-c++
Requires: gd
Requires: glibc
Requires: glibc-common
Requires: gnupg
Requires: gperf
Requires: gzip
Requires: httpd
Requires: install
Requires: iptables
Requires: less
Requires: libpcap
Requires: libpcap-devel
Requires: libtool
Requires: linuxdoc-tools
Requires: mailx
Requires: make
Requires: metadata
Requires: mkisofs
Requires: mod_python
Requires: mod_ssl
Requires: mysql
Requires: mysql-devel
Requires: mysql-server
Requires: nasm
Requires: ncurses-devel
Requires: openssh
Requires: openssl
Requires: php
Requires: php-devel
Requires: php-gd
Requires: php-pgsql
Requires: postgresql
Requires: postgresql-devel
Requires: postgresql-python
Requires: postgresql-server
Requires: python
Requires: python-devel
Requires: PyXML
Requires: readline-devel
Requires: redhat-rpm-config
Requires: rpm
Requires: rpm-build
Requires: rpm-devel
Requires: rsync
Requires: sendmail
Requires: sendmail-cf
Requires: sharutils
Requires: sudo
Requires: svn
Requires: tar
Requires: tetex-latex
Requires: time
Requires: vconfig
Requires: vixie-cron
Requires: wget
Requires: xmlsec1
Requires: xmlsec1-openssl
Requires: yum

%define debug_package %{nil}

%description
This package installs a complete PlanetLab development
environment. The default installation consists of all the packages
necessary to compile MyPLC.

%prep
%setup -q

%build
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc

%install
touch $RPM_BUILD_ROOT/etc/myplc-devel-native

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

%post

uid=2000
gid=2000

builduser=$(grep "^build" /etc/passwd | wc -l)
if [ $builduser -eq 0 ] ; then
	groupadd -o -g $gid build;
	useradd -o -c 'Automated Build' -u $uid -g $gid -n -M -s /bin/bash build;
fi

# Allow build user to build certain RPMs as root
buildsudo=$(grep "^build.*ALL=(ALL).*NOPASSWD:.*ALL"  /etc/sudoers | wc -l)
if [ $buildsudo -eq 0 ] ; then
	echo "build   ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers
fi


%preun
# 0 = erase, 1 = upgrade
if [ $1 -eq 0 ] ; then
fi

%files
%defattr(-,root,root,-)
/etc/myplc-devel-native

%changelog
* Fri Oct 05 2007 Marc E. Fiuczynski <mef@cs.princeton.edu>
- Initial build.