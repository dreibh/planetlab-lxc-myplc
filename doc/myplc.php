<?php

  // DO NOT EDIT. This file was automatically generated from
  // DocBook XML. See plc_www/doc/README.

  $_title= "MyPLC User's Guide";

  require_once('session.php');
  require_once('header.php');
  require_once('nav.php');

  ?><div class="article" lang="en">
<div class="titlepage">
<div>
<div><h1 class="title">
<a name="id224920"></a>MyPLC User's Guide</h1></div>
<div><div class="author"><h3 class="author"><span class="firstname">Mark Huang</span></h3></div></div>
<div><div class="revhistory"><table border="1" width="100%" summary="Revision history">
<tr><th align="left" valign="top" colspan="3"><b>Revision History</b></th></tr>
<tr>
<td align="left">Revision 1.0</td>
<td align="left">April 7, 2006</td>
<td align="left">MLH</td>
</tr>
<tr><td align="left" colspan="3"><p>Initial draft.</p></td></tr>
<tr>
<td align="left">Revision 1.1</td>
<td align="left">July 19, 2006</td>
<td align="left">MLH</td>
</tr>
<tr><td align="left" colspan="3"><p>Add development environment.</p></td></tr>
</table></div></div>
<div><div class="abstract">
<p class="title"><b>Abstract</b></p>
<p>This document describes the design, installation, and
      administration of MyPLC, a complete PlanetLab Central (PLC)
      portable installation contained within a
      <span><strong class="command">chroot</strong></span> jail. This document assumes advanced
      knowledge of the PlanetLab architecture and Linux system
      administration.</p>
</div></div>
</div>
<hr>
</div>
<div class="toc">
<p><b>Table of Contents</b></p>
<dl>
<dt><span class="section"><a href="#id225375">1. Overview</a></span></dt>
<dt><span class="section"><a href="#Installation">2. Installation</a></span></dt>
<dt><span class="section"><a href="#id267694">3. Quickstart</a></span></dt>
<dd><dl>
<dt><span class="section"><a href="#ChangingTheConfiguration">3.1. Changing the configuration</a></span></dt>
<dt><span class="section"><a href="#id268201">3.2. Installing nodes</a></span></dt>
<dt><span class="section"><a href="#id268275">3.3. Administering nodes</a></span></dt>
<dt><span class="section"><a href="#id268369">3.4. Creating a slice</a></span></dt>
</dl></dd>
<dt><span class="section"><a href="#id268444">4. Rebuilding and customizing MyPLC</a></span></dt>
<dd><dl>
<dt><span class="section"><a href="#id268469">4.1. Installation</a></span></dt>
<dt><span class="section"><a href="#id268676">4.2. Fedora Core 4 mirror requirement</a></span></dt>
<dt><span class="section"><a href="#BuildingMyPLC">4.3. Building MyPLC</a></span></dt>
<dt><span class="section"><a href="#UpdatingCVS">4.4. Updating CVS</a></span></dt>
</dl></dd>
<dt><span class="appendix"><a href="#id269037">A. Configuration variables</a></span></dt>
<dt><span class="appendix"><a href="#id271742">B. Development environment configuration variables</a></span></dt>
<dt><span class="bibliography"><a href="#id271824">Bibliography</a></span></dt>
</dl>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="id225375"></a>1. Overview</h2></div></div></div>
<p>MyPLC is a complete PlanetLab Central (PLC) portable
    installation contained within a <span><strong class="command">chroot</strong></span>
    jail. The default installation consists of a web server, an
    XML-RPC API server, a boot server, and a database server: the core
    components of PLC. The installation is customized through an
    easy-to-use graphical interface. All PLC services are started up
    and shut down through a single script installed on the host
    system. The usually complex process of installing and
    administering the PlanetLab backend is reduced by containing PLC
    services within a virtual filesystem. By packaging it in such a
    manner, MyPLC may also be run on any modern Linux distribution,
    and could conceivably even run in a PlanetLab slice.</p>
<div class="figure">
<a name="Architecture"></a><p class="title"><b>Figure 1. MyPLC architecture</b></p>
<div class="mediaobject" align="center">
<img src="architecture.png" align="middle" width="270" alt="MyPLC architecture"><div class="caption"><p>MyPLC should be viewed as a single application that
          provides multiple functions and can run on any host
          system.</p></div>
</div>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="Installation"></a>2. Installation</h2></div></div></div>
<p>Though internally composed of commodity software
    subpackages, MyPLC should be treated as a monolithic software
    application. MyPLC is distributed as single RPM package that has
    no external dependencies, allowing it to be installed on
    practically any Linux 2.6 based distribution:</p>
<div class="example">
<a name="id225278"></a><p class="title"><b>Example 1. Installing MyPLC.</b></p>
<pre class="programlisting"># If your distribution supports RPM
rpm -U http://build.planet-lab.org/build/myplc-0_4-rc1/RPMS/i386/myplc-0.4-1.planetlab.i386.rpm

# If your distribution does not support RPM
cd /tmp
wget http://build.planet-lab.org/build/myplc-0_4-rc1/RPMS/i386/myplc-0.4-1.planetlab.i386.rpm
cd /
rpm2cpio /tmp/myplc-0.4-1.planetlab.i386.rpm | cpio -diu</pre>
</div>
<p>MyPLC installs the following files and directories:</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="filename">/plc/root.img</code>: The main
      root filesystem of the MyPLC application. This file is an
      uncompressed ext3 filesystem that is loopback mounted on
      <code class="filename">/plc/root</code> when MyPLC starts. This
      filesystem, even when mounted, should be treated as an opaque
      binary that can and will be replaced in its entirety by any
      upgrade of MyPLC.</p></li>
<li><p><code class="filename">/plc/root</code>: The mount point
      for <code class="filename">/plc/root.img</code>. Once the root filesystem
      is mounted, all MyPLC services run in a
      <span><strong class="command">chroot</strong></span> jail based in this
      directory.</p></li>
<li>
<p><code class="filename">/plc/data</code>: The directory where user
	data and generated files are stored. This directory is bind
	mounted onto <code class="filename">/plc/root/data</code> so that it is
	accessible as <code class="filename">/data</code> from within the
	<span><strong class="command">chroot</strong></span> jail. Files in this directory are
	marked with <span><strong class="command">%config(noreplace)</strong></span> in the
	RPM. That is, during an upgrade of MyPLC, if a file has not
	changed since the last installation or upgrade of MyPLC, it is
	subject to upgrade and replacement. If the file has changed,
	the new version of the file will be created with a
	<code class="filename">.rpmnew</code> extension. Symlinks within the
	MyPLC root filesystem ensure that the following directories
	(relative to <code class="filename">/plc/root</code>) are stored
	outside the MyPLC filesystem image:</p>
<div class="itemizedlist"><ul type="circle">
<li><p><code class="filename">/etc/planetlab</code>: This
	  directory contains the configuration files, keys, and
	  certificates that define your MyPLC
	  installation.</p></li>
<li><p><code class="filename">/var/lib/pgsql</code>: This
	  directory contains PostgreSQL database
	  files.</p></li>
<li><p><code class="filename">/var/www/html/alpina-logs</code>: This
	  directory contains node installation logs.</p></li>
<li><p><code class="filename">/var/www/html/boot</code>: This
	  directory contains the Boot Manager, customized for your MyPLC
	  installation, and its data files.</p></li>
<li><p><code class="filename">/var/www/html/download</code>: This
	  directory contains Boot CD images, customized for your MyPLC
	  installation.</p></li>
<li><p><code class="filename">/var/www/html/install-rpms</code>: This
	  directory is where you should install node package updates,
	  if any. By default, nodes are installed from the tarball
	  located at
	  <code class="filename">/var/www/html/boot/PlanetLab-Bootstrap.tar.bz2</code>,
	  which is pre-built from the latest PlanetLab Central
	  sources, and installed as part of your MyPLC
	  installation. However, nodes will attempt to install any
	  newer RPMs located in
	  <code class="filename">/var/www/html/install-rpms/planetlab</code>,
	  after initial installation and periodically thereafter. You
	  must run <span><strong class="command">yum-arch</strong></span> and
	  <span><strong class="command">createrepo</strong></span> to update the
	  <span><strong class="command">yum</strong></span> caches in this directory after
	  installing a new RPM. PlanetLab Central cannot support any
	  changes to this directory.</p></li>
<li><p><code class="filename">/var/www/html/xml</code>: This
	  directory contains various XML files that the Slice Creation
	  Service uses to determine the state of slices. These XML
	  files are refreshed periodically by <span><strong class="command">cron</strong></span>
	  jobs running in the MyPLC root.</p></li>
</ul></div>
</li>
<li>
<p><code class="filename">/etc/init.d/plc</code>: This file
	is a System V init script installed on your host filesystem,
	that allows you to start up and shut down MyPLC with a single
	command. On a Red Hat or Fedora host system, it is customary to
	use the <span><strong class="command">service</strong></span> command to invoke System V
	init scripts:</p>
<div class="example">
<a name="StartingAndStoppingMyPLC"></a><p class="title"><b>Example 2. Starting and stopping MyPLC.</b></p>
<pre class="programlisting"># Starting MyPLC
service plc start

# Stopping MyPLC
service plc stop</pre>
</div>
<p>Like all other registered System V init services, MyPLC is
	started and shut down automatically when your host system boots
	and powers off. You may disable automatic startup by invoking
	the <span><strong class="command">chkconfig</strong></span> command on a Red Hat or Fedora
	host system:</p>
<div class="example">
<a name="id243568"></a><p class="title"><b>Example 3. Disabling automatic startup of MyPLC.</b></p>
<pre class="programlisting"># Disable automatic startup
chkconfig plc off

# Enable automatic startup
chkconfig plc on</pre>
</div>
</li>
<li><p><code class="filename">/etc/sysconfig/plc</code>: This
      file is a shell script fragment that defines the variables
      <code class="envar">PLC_ROOT</code> and <code class="envar">PLC_DATA</code>. By default,
      the values of these variables are <code class="filename">/plc/root</code>
      and <code class="filename">/plc/data</code>, respectively. If you wish,
      you may move your MyPLC installation to another location on your
      host filesystem and edit the values of these variables
      appropriately, but you will break the RPM upgrade
      process. PlanetLab Central cannot support any changes to this
      file.</p></li>
<li><p><code class="filename">/etc/planetlab</code>: This
      symlink to <code class="filename">/plc/data/etc/planetlab</code> is
      installed on the host system for convenience.</p></li>
</ul></div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="id267694"></a>3. Quickstart</h2></div></div></div>
<p>Once installed, start MyPLC (see <a href="#StartingAndStoppingMyPLC" title="Example 2. Starting and stopping MyPLC.">Example 2, “Starting and stopping MyPLC.”</a>). MyPLC must be started as
    root. Observe the output of this command for any failures. If no
    failures occur, you should see output similar to the
    following:</p>
<div class="example">
<a name="id267814"></a><p class="title"><b>Example 4. A successful MyPLC startup.</b></p>
<pre class="programlisting">Mounting PLC:                                              [  OK  ]
PLC: Generating network files:                             [  OK  ]
PLC: Starting system logger:                               [  OK  ]
PLC: Starting database server:                             [  OK  ]
PLC: Generating SSL certificates:                          [  OK  ]
PLC: Configuring the API:                                  [  OK  ]
PLC: Updating GPG keys:                                    [  OK  ]
PLC: Generating SSH keys:                                  [  OK  ]
PLC: Starting web server:                                  [  OK  ]
PLC: Bootstrapping the database:                           [  OK  ]
PLC: Starting DNS server:                                  [  OK  ]
PLC: Starting crond:                                       [  OK  ]
PLC: Rebuilding Boot CD:                                   [  OK  ]
PLC: Rebuilding Boot Manager:                              [  OK  ]
PLC: Signing node packages:                                [  OK  ]
</pre>
</div>
<p>If <code class="filename">/plc/root</code> is mounted successfully, a
    complete log file of the startup process may be found at
    <code class="filename">/plc/root/var/log/boot.log</code>. Possible reasons
    for failure of each step include:</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="literal">Mounting PLC</code>: If this step
      fails, first ensure that you started MyPLC as root. Check
      <code class="filename">/etc/sysconfig/plc</code> to ensure that
      <code class="envar">PLC_ROOT</code> and <code class="envar">PLC_DATA</code> refer to the
      right locations. You may also have too many existing loopback
      mounts, or your kernel may not support loopback mounting, bind
      mounting, or the ext3 filesystem. Try freeing at least one
      loopback device, or re-compiling your kernel to support loopback
      mounting, bind mounting, and the ext3 filesystem. If you see an
      error similar to <code class="literal">Permission denied while trying to open
      /plc/root.img</code>, then SELinux may be enabled. If you
      installed MyPLC on Fedora Core 4 or 5, use the
      <span class="application">Security Level Configuration</span> utility
      to configure SELinux to be
      <code class="literal">Permissive</code>.</p></li>
<li><p><code class="literal">Starting database server</code>: If
      this step fails, check
      <code class="filename">/plc/root/var/log/pgsql</code> and
      <code class="filename">/plc/root/var/log/boot.log</code>. The most common
      reason for failure is that the default PostgreSQL port, TCP port
      5432, is already in use. Check that you are not running a
      PostgreSQL server on the host system.</p></li>
<li><p><code class="literal">Starting web server</code>: If this
      step fails, check
      <code class="filename">/plc/root/var/log/httpd/error_log</code> and
      <code class="filename">/plc/root/var/log/boot.log</code> for obvious
      errors. The most common reason for failure is that the default
      web ports, TCP ports 80 and 443, are already in use. Check that
      you are not running a web server on the host
      system.</p></li>
<li><p><code class="literal">Bootstrapping the database</code>:
      If this step fails, it is likely that the previous step
      (<code class="literal">Starting web server</code>) also failed. Another
      reason that it could fail is if <code class="envar">PLC_API_HOST</code> (see
      <a href="#ChangingTheConfiguration" title="3.1. Changing the configuration">Section 3.1, “Changing the configuration”</a>) does not resolve to
      the host on which the API server has been enabled. By default,
      all services, including the API server, are enabled and run on
      the same host, so check that <code class="envar">PLC_API_HOST</code> is
      either <code class="filename">localhost</code> or resolves to a local IP
      address.</p></li>
<li><p><code class="literal">Starting crond</code>: If this step
      fails, it is likely that the previous steps (<code class="literal">Starting
      web server</code> and <code class="literal">Bootstrapping the
      database</code>) also failed. If not, check
      <code class="filename">/plc/root/var/log/boot.log</code> for obvious
      errors. This step starts the <span><strong class="command">cron</strong></span> service and
      generates the initial set of XML files that the Slice Creation
      Service uses to determine slice state.</p></li>
</ul></div>
<p>If no failures occur, then MyPLC should be active with a
    default configuration. Open a web browser on the host system and
    visit <code class="literal">http://localhost/</code>, which should bring you
    to the front page of your PLC installation. The password of the
    default administrator account
    <code class="literal">root@localhost.localdomain</code> (set by
    <code class="envar">PLC_ROOT_USER</code>) is <code class="literal">root</code> (set by
    <code class="envar">PLC_ROOT_PASSWORD</code>).</p>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="ChangingTheConfiguration"></a>3.1. Changing the configuration</h3></div></div></div>
<p>After verifying that MyPLC is working correctly, shut it
      down and begin changing some of the default variable
      values. Shut down MyPLC with <span><strong class="command">service plc stop</strong></span>
      (see <a href="#StartingAndStoppingMyPLC" title="Example 2. Starting and stopping MyPLC.">Example 2, “Starting and stopping MyPLC.”</a>). With a text
      editor, open the file
      <code class="filename">/etc/planetlab/plc_config.xml</code>. This file is
      a self-documenting configuration file written in XML. Variables
      are divided into categories. Variable identifiers must be
      alphanumeric, plus underscore. A variable is referred to
      canonically as the uppercase concatenation of its category
      identifier, an underscore, and its variable identifier. Thus, a
      variable with an <code class="literal">id</code> of
      <code class="literal">slice_prefix</code> in the <code class="literal">plc</code>
      category is referred to canonically as
      <code class="envar">PLC_SLICE_PREFIX</code>.</p>
<p>The reason for this convention is that during MyPLC
      startup, <code class="filename">plc_config.xml</code> is translated into
      several different languages—shell, PHP, and
      Python—so that scripts written in each of these languages
      can refer to the same underlying configuration. Most MyPLC
      scripts are written in shell, so the convention for shell
      variables predominates.</p>
<p>The variables that you should change immediately are:</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="envar">PLC_NAME</code>: Change this to the
	name of your PLC installation.</p></li>
<li><p><code class="envar">PLC_ROOT_PASSWORD</code>: Change this
	to a more secure password.</p></li>
<li><p><code class="envar">PLC_MAIL_SUPPORT_ADDRESS</code>:
	Change this to the e-mail address at which you would like to
	receive support requests.</p></li>
<li><p><code class="envar">PLC_DB_HOST</code>,
	<code class="envar">PLC_DB_IP</code>, <code class="envar">PLC_API_HOST</code>,
	<code class="envar">PLC_API_IP</code>, <code class="envar">PLC_WWW_HOST</code>,
	<code class="envar">PLC_WWW_IP</code>, <code class="envar">PLC_BOOT_HOST</code>,
	<code class="envar">PLC_BOOT_IP</code>: Change all of these to the
	preferred FQDN and external IP address of your host
	system.</p></li>
</ul></div>
<p>After changing these variables, save the file, then
      restart MyPLC with <span><strong class="command">service plc start</strong></span>. You
      should notice that the password of the default administrator
      account is no longer <code class="literal">root</code>, and that the
      default site name includes the name of your PLC installation
      instead of PlanetLab.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id268201"></a>3.2. Installing nodes</h3></div></div></div>
<p>Install your first node by clicking <code class="literal">Add
      Node</code> under the <code class="literal">Nodes</code> tab. Fill in
      all the appropriate details, then click
      <code class="literal">Add</code>. Download the node's configuration file
      by clicking <code class="literal">Download configuration file</code> on
      the <span class="bold"><strong>Node Details</strong></span> page for the
      node. Save it to a floppy disk or USB key as detailed in [<a href="#TechsGuide" title="[TechsGuide]">1</a>].</p>
<p>Follow the rest of the instructions in [<a href="#TechsGuide" title="[TechsGuide]">1</a>] for creating a Boot CD and installing
      the node, except download the Boot CD image from the
      <code class="filename">/download</code> directory of your PLC
      installation, not from PlanetLab Central. The images located
      here are customized for your installation. If you change the
      hostname of your boot server (<code class="envar">PLC_BOOT_HOST</code>), or
      if the SSL certificate of your boot server expires, MyPLC will
      regenerate it and rebuild the Boot CD with the new
      certificate. If this occurs, you must replace all Boot CDs
      created before the certificate was regenerated.</p>
<p>The installation process for a node has significantly
      improved since PlanetLab 3.3. It should now take only a few
      seconds for a new node to become ready to create slices.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id268275"></a>3.3. Administering nodes</h3></div></div></div>
<p>You may administer nodes as <code class="literal">root</code> by
      using the SSH key stored in
      <code class="filename">/etc/planetlab/root_ssh_key.rsa</code>.</p>
<div class="example">
<a name="id268297"></a><p class="title"><b>Example 5. Accessing nodes via SSH. Replace
	<code class="literal">node</code> with the hostname of the node.</b></p>
<pre class="programlisting">ssh -i /etc/planetlab/root_ssh_key.rsa root@node</pre>
</div>
<p>Besides the standard Linux log files located in
      <code class="filename">/var/log</code>, several other files can give you
      clues about any problems with active processes:</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="filename">/var/log/pl_nm</code>: The log
	file for the Node Manager.</p></li>
<li><p><code class="filename">/vservers/pl_conf/var/log/pl_conf</code>:
	The log file for the Slice Creation Service.</p></li>
<li><p><code class="filename">/var/log/propd</code>: The log
	file for Proper, the service which allows certain slices to
	perform certain privileged operations in the root
	context.</p></li>
<li><p><code class="filename">/vservers/pl_netflow/var/log/netflow.log</code>:
	The log file for PlanetFlow, the network traffic auditing
	service.</p></li>
</ul></div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id268369"></a>3.4. Creating a slice</h3></div></div></div>
<p>Create a slice by clicking <code class="literal">Create Slice</code>
      under the <code class="literal">Slices</code> tab. Fill in all the
      appropriate details, then click <code class="literal">Create</code>. Add
      nodes to the slice by clicking <code class="literal">Manage Nodes</code>
      on the <span class="bold"><strong>Slice Details</strong></span> page for
      the slice.</p>
<p>A <span><strong class="command">cron</strong></span> job runs every five minutes and
      updates the file
      <code class="filename">/plc/data/var/www/html/xml/slices-0.5.xml</code>
      with information about current slice state. The Slice Creation
      Service running on every node polls this file every ten minutes
      to determine if it needs to create or delete any slices. You may
      accelerate this process manually if desired.</p>
<div class="example">
<a name="id268427"></a><p class="title"><b>Example 6. Forcing slice creation on a node.</b></p>
<pre class="programlisting"># Update slices.xml immediately
service plc start crond

# Kick the Slice Creation Service on a particular node.
ssh -i /etc/planetlab/root_ssh_key.rsa root@node \
vserver pl_conf exec service pl_conf restart</pre>
</div>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="id268444"></a>4. Rebuilding and customizing MyPLC</h2></div></div></div>
<p>The MyPLC package, though distributed as an RPM, is not a
    traditional package that can be easily rebuilt from SRPM. The
    requisite build environment is quite extensive and numerous
    assumptions are made throughout the PlanetLab source code base,
    that the build environment is based on Fedora Core 4 and that
    access to a complete Fedora Core 4 mirror is available.</p>
<p>For this reason, it is recommended that you only rebuild
    MyPLC (or any of its components) from within the MyPLC development
    environment. The MyPLC development environment is similar to MyPLC
    itself in that it is a portable filesystem contained within a
    <span><strong class="command">chroot</strong></span> jail. The filesystem contains all the
    necessary tools required to rebuild MyPLC, as well as a snapshot
    of the PlanetLab source code base in the form of a local CVS
    repository.</p>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id268469"></a>4.1. Installation</h3></div></div></div>
<p>Install the MyPLC development environment similarly to how
      you would install MyPLC. You may install both packages on the same
      host system if you wish. As with MyPLC, the MyPLC development
      environment should be treated as a monolithic software
      application, and any files present in the
      <span><strong class="command">chroot</strong></span> jail should not be modified directly, as
      they are subject to upgrade.</p>
<div class="example">
<a name="id268487"></a><p class="title"><b>Example 7. Installing the MyPLC development environment.</b></p>
<pre class="programlisting"># If your distribution supports RPM
rpm -U http://build.planet-lab.org/build/myplc-0_4-rc2/RPMS/i386/myplc-devel-0.4-2.planetlab.i386.rpm

# If your distribution does not support RPM
cd /tmp
wget http://build.planet-lab.org/build/myplc-0_4-rc2/RPMS/i386/myplc-devel-0.4-2.planetlab.i386.rpm
cd /
rpm2cpio /tmp/myplc-devel-0.4-2.planetlab.i386.rpm | cpio -diu</pre>
</div>
<p>The MyPLC development environment installs the following
      files and directories:</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="filename">/plc/devel/root.img</code>: The
	main root filesystem of the MyPLC development environment. This
	file is an uncompressed ext3 filesystem that is loopback mounted
	on <code class="filename">/plc/devel/root</code> when the MyPLC
	development environment is initialized. This filesystem, even
	when mounted, should be treated as an opaque binary that can and
	will be replaced in its entirety by any upgrade of the MyPLC
	development environment.</p></li>
<li><p><code class="filename">/plc/devel/root</code>: The mount
	point for
	<code class="filename">/plc/devel/root.img</code>.</p></li>
<li>
<p><code class="filename">/plc/devel/data</code>: The directory
	  where user data and generated files are stored. This directory
	  is bind mounted onto <code class="filename">/plc/devel/root/data</code>
	  so that it is accessible as <code class="filename">/data</code> from
	  within the <span><strong class="command">chroot</strong></span> jail. Files in this
	  directory are marked with
	  <span><strong class="command">%config(noreplace)</strong></span> in the RPM. Symlinks
	  ensure that the following directories (relative to
	  <code class="filename">/plc/devel/root</code>) are stored outside the
	  root filesystem image:</p>
<div class="itemizedlist"><ul type="circle">
<li><p><code class="filename">/etc/planetlab</code>: This
	    directory contains the configuration files that define your
	    MyPLC development environment.</p></li>
<li><p><code class="filename">/cvs</code>: A
	    snapshot of the PlanetLab source code is stored as a CVS
	    repository in this directory. Files in this directory will
	    <span class="bold"><strong>not</strong></span> be updated by an upgrade of
	    <code class="filename">myplc-devel</code>. See <a href="#UpdatingCVS" title="4.4. Updating CVS">Section 4.4, “Updating CVS”</a> for more information about updating
	    PlanetLab source code.</p></li>
<li><p><code class="filename">/build</code>:
	    Builds are stored in this directory. This directory is bind
	    mounted onto <code class="filename">/plc/devel/root/build</code> so that
	    it is accessible as <code class="filename">/build</code> from within the
	    <span><strong class="command">chroot</strong></span> jail. The build scripts in this
	    directory are themselves source controlled; see <a href="#BuildingMyPLC" title="4.3. Building MyPLC">Section 4.3, “Building MyPLC”</a> for more information about executing
	    builds.</p></li>
</ul></div>
</li>
<li><p><code class="filename">/etc/init.d/plc-devel</code>: This file is
	  a System V init script installed on your host filesystem, that
	  allows you to start up and shut down the MyPLC development
	  environment with a single command.</p></li>
</ul></div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id268676"></a>4.2. Fedora Core 4 mirror requirement</h3></div></div></div>
<p>The MyPLC development environment requires access to a
      complete Fedora Core 4 i386 RPM repository, because several
      different filesystems based upon Fedora Core 4 are constructed
      during the process of building MyPLC. You may configure the
      location of this repository via the
      <code class="envar">PLC_DEVEL_FEDORA_URL</code> variable in
      <code class="filename">/plc/devel/data/etc/planetlab/plc_config.xml</code>. The
      value of the variable should be a URL that points to the top
      level of a Fedora mirror that provides the
      <code class="filename">base</code>, <code class="filename">updates</code>, and
      <code class="filename">extras</code> repositories, e.g.,</p>
<div class="itemizedlist"><ul type="disc">
<li><p><code class="filename">file:///data/fedora</code></p></li>
<li><p><code class="filename">http://coblitz.planet-lab.org/pub/fedora</code></p></li>
<li><p><code class="filename">ftp://mirror.cs.princeton.edu/pub/mirrors/fedora</code></p></li>
<li><p><code class="filename">ftp://mirror.stanford.edu/pub/mirrors/fedora</code></p></li>
<li><p><code class="filename">http://rpmfind.net/linux/fedora</code></p></li>
</ul></div>
<p>As implied by the list, the repository may be located on
      the local filesystem, or it may be located on a remote FTP or
      HTTP server. URLs beginning with <code class="filename">file://</code>
      should exist at the specified location relative to the root of
      the <span><strong class="command">chroot</strong></span> jail. For optimum performance and
      reproducibility, specify
      <code class="envar">PLC_DEVEL_FEDORA_URL=file:///data/fedora</code> and
      download all Fedora Core 4 RPMS into
      <code class="filename">/plc/devel/data/fedora</code> on the host system
      after installing <code class="filename">myplc-devel</code>. Use a tool
      such as <span><strong class="command">wget</strong></span> or <span><strong class="command">rsync</strong></span> to
      download the RPMS from a public mirror:</p>
<div class="example">
<a name="id268807"></a><p class="title"><b>Example 8. Setting up a local Fedora Core 4 repository.</b></p>
<pre class="programlisting">mkdir -p /plc/devel/data/fedora
cd /plc/devel/data/fedora

for repo in core/4/i386/os core/updates/4/i386 extras/4/i386 ; do
    wget -m -nH --cut-dirs=3 http://coblitz.planet-lab.org/pub/fedora/linux/$repo
done</pre>
</div>
<p>Change the repository URI and <span><strong class="command">--cut-dirs</strong></span>
      level as needed to produce a hierarchy that resembles:</p>
<pre class="programlisting">/plc/devel/data/fedora/core/4/i386/os
/plc/devel/data/fedora/core/updates/4/i386
/plc/devel/data/fedora/extras/4/i386</pre>
<p>A list of additional Fedora Core 4 mirrors is available at
      <a href="http://fedora.redhat.com/Download/mirrors.html" target="_top">http://fedora.redhat.com/Download/mirrors.html</a>.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="BuildingMyPLC"></a>4.3. Building MyPLC</h3></div></div></div>
<p>All PlanetLab source code modules are built and installed
      as RPMS. A set of build scripts, checked into the
      <code class="filename">build/</code> directory of the PlanetLab CVS
      repository, eases the task of rebuilding PlanetLab source
      code.</p>
<p>To build MyPLC, or any PlanetLab source code module, from
      within the MyPLC development environment, execute the following
      commands as root:</p>
<div class="example">
<a name="id268873"></a><p class="title"><b>Example 9. Building MyPLC.</b></p>
<pre class="programlisting"># Initialize MyPLC development environment
service plc-devel start

# Enter development environment
chroot /plc/devel/root su -

# Check out build scripts into a directory named after the current
# date. This is simply a convention, it need not be followed
# exactly. See build/build.sh for an example of a build script that
# names build directories after CVS tags.
DATE=$(date +%Y.%m.%d)
cd /build
cvs -d /cvs checkout -d $DATE build

# Build everything
make -C $DATE</pre>
</div>
<p>If the build succeeds, a set of binary RPMS will be
      installed under
      <code class="filename">/plc/devel/data/build/$DATE/RPMS/</code> that you
      may copy to the
      <code class="filename">/var/www/html/install-rpms/planetlab</code>
      directory of your MyPLC installation (see <a href="#Installation" title="2. Installation">Section 2, “Installation”</a>).</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="UpdatingCVS"></a>4.4. Updating CVS</h3></div></div></div>
<p>A complete snapshot of the PlanetLab source code is included
      with the MyPLC development environment as a CVS repository in
      <code class="filename">/plc/devel/data/cvs</code>. This CVS repository may
      be accessed like any other CVS repository. It may be accessed
      using an interface such as <a href="http://www.freebsd.org/projects/cvsweb.html" target="_top">CVSweb</a>,
      and file permissions may be altered to allow for fine-grained
      access control. Although the files are included with the
      <code class="filename">myplc-devel</code> RPM, they are <span class="bold"><strong>not</strong></span> subject to upgrade once installed. New
      versions of the <code class="filename">myplc-devel</code> RPM will install
      updated snapshot repositories in
      <code class="filename">/plc/devel/data/cvs-%{version}-%{release}</code>,
      where <code class="literal">%{version}-%{release}</code> is replaced with
      the version number of the RPM.</p>
<p>Because the CVS repository is not automatically upgraded,
      if you wish to keep your local repository synchronized with the
      public PlanetLab repository, it is highly recommended that you
      use CVS's support for <a href="http://ximbiot.com/cvs/wiki/index.php?title=CVS--Concurrent_Versions_System_v1.12.12.1:_Tracking_third-party_sources" target="_top">vendor
      branches</a> to track changes. Vendor branches ease the task
      of merging upstream changes with your local modifications. To
      import a new snapshot into your local repository (for example,
      if you have just upgraded from
      <code class="filename">myplc-devel-0.4-2</code> to
      <code class="filename">myplc-devel-0.4-3</code> and you notice the new
      repository in <code class="filename">/plc/devel/data/cvs-0.4-3</code>),
      execute the following commands as root from within the MyPLC
      development environment:</p>
<div class="example">
<a name="id269004"></a><p class="title"><b>Example 10. Updating /data/cvs from /data/cvs-0.4-3.</b></p>
<p><span class="bold"><strong>Warning</strong></span>: This may cause
	severe, irreversible changes to be made to your local
	repository. Always tag your local repository before
	importing.</p>
<pre class="programlisting"># Initialize MyPLC development environment
service plc-devel start

# Enter development environment
chroot /plc/devel/root su -

# Tag current state
cvs -d /cvs rtag before-myplc-0_4-3-merge

# Export snapshot
TMP=$(mktemp -d /data/export.XXXXXX)
pushd $TMP
cvs -d /data/cvs-0.4-3 export -r HEAD .
cvs -d /cvs import -m "PlanetLab sources from myplc-0.4-3" -ko -I ! . planetlab myplc-0_4-3
popd
rm -rf $TMP</pre>
</div>
<p>If there any merge conflicts, use the command suggested by
      CVS to help the merge. Explaining how to fix merge conflicts is
      beyond the scope of this document; consult the CVS documentation
      for more information on how to use CVS.</p>
</div>
</div>
<div class="appendix" lang="en">
<h2 class="title" style="clear: both">
<a name="id269037"></a>A. Configuration variables</h2>
<p>Listed below is the set of standard configuration variables
    and their default values, defined in the template
    <code class="filename">/etc/planetlab/default_config.xml</code>. Additional
    variables and their defaults may be defined in site-specific XML
    templates that should be placed in
    <code class="filename">/etc/planetlab/configs/</code>.</p>
<div class="variablelist"><dl>
<dt><span class="term">PLC_NAME</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: PlanetLab Test</p>
<p>The name of this PLC installation. It is used in
	  the name of the default system site (e.g., PlanetLab Central)
	  and in the names of various administrative entities (e.g.,
	  PlanetLab Support).</p>
</dd>
<dt><span class="term">PLC_SLICE_PREFIX</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: pl</p>
<p>The abbreviated name of this PLC
	  installation. It is used as the prefix for system slices
	  (e.g., pl_conf). Warning: Currently, this variable should
	  not be changed.</p>
</dd>
<dt><span class="term">PLC_ROOT_USER</span></dt>
<dd>
<p>
		  Type: email</p>
<p>
		  Default: root@localhost.localdomain</p>
<p>The name of the initial administrative
	  account. We recommend that this account be used only to create
	  additional accounts associated with real
	  administrators, then disabled.</p>
</dd>
<dt><span class="term">PLC_ROOT_PASSWORD</span></dt>
<dd>
<p>
		  Type: password</p>
<p>
		  Default: root</p>
<p>The password of the initial administrative
	  account. Also the password of the root account on the Boot
	  CD.</p>
</dd>
<dt><span class="term">PLC_ROOT_SSH_KEY_PUB</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/root_ssh_key.pub</p>
<p>The SSH public key used to access the root
	  account on your nodes.</p>
</dd>
<dt><span class="term">PLC_ROOT_SSH_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/root_ssh_key.rsa</p>
<p>The SSH private key used to access the root
	  account on your nodes.</p>
</dd>
<dt><span class="term">PLC_DEBUG_SSH_KEY_PUB</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/debug_ssh_key.pub</p>
<p>The SSH public key used to access the root
	  account on your nodes when they are in Debug mode.</p>
</dd>
<dt><span class="term">PLC_DEBUG_SSH_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/debug_ssh_key.rsa</p>
<p>The SSH private key used to access the root
	  account on your nodes when they are in Debug mode.</p>
</dd>
<dt><span class="term">PLC_ROOT_GPG_KEY_PUB</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/pubring.gpg</p>
<p>The GPG public keyring used to sign the Boot
	  Manager and all node packages.</p>
</dd>
<dt><span class="term">PLC_ROOT_GPG_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/secring.gpg</p>
<p>The SSH private key used to access the root
	  account on your nodes.</p>
</dd>
<dt><span class="term">PLC_MA_SA_NAMESPACE</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: test</p>
<p>The namespace of your MA/SA. This should be a
	  globally unique value assigned by PlanetLab
	  Central.</p>
</dd>
<dt><span class="term">PLC_MA_SA_SSL_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/ma_sa_ssl.key</p>
<p>The SSL private key used for signing documents
	  with the signature of your MA/SA. If non-existent, one will
	  be generated.</p>
</dd>
<dt><span class="term">PLC_MA_SA_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/ma_sa_ssl.crt</p>
<p>The corresponding SSL public certificate. By
	  default, this certificate is self-signed. You may replace
	  the certificate later with one signed by the PLC root
	  CA.</p>
</dd>
<dt><span class="term">PLC_MA_SA_CA_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/ma_sa_ca_ssl.crt</p>
<p>If applicable, the certificate of the PLC root
	  CA. If your MA/SA certificate is self-signed, then this file
	  is the same as your MA/SA certificate.</p>
</dd>
<dt><span class="term">PLC_MA_SA_CA_SSL_KEY_PUB</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/ma_sa_ca_ssl.pub</p>
<p>If applicable, the public key of the PLC root
	  CA. If your MA/SA certificate is self-signed, then this file
	  is the same as your MA/SA public key.</p>
</dd>
<dt><span class="term">PLC_MA_SA_API_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/ma_sa_api.xml</p>
<p>The API Certificate is your MA/SA public key
	  embedded in a digitally signed XML document. By default,
	  this document is self-signed. You may replace this
	  certificate later with one signed by the PLC root
	  CA.</p>
</dd>
<dt><span class="term">PLC_NET_DNS1</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: 127.0.0.1</p>
<p>Primary DNS server address.</p>
</dd>
<dt><span class="term">PLC_NET_DNS2</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: </p>
<p>Secondary DNS server address.</p>
</dd>
<dt><span class="term">PLC_DNS_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: true</p>
<p>Enable the internal DNS server. The server does
          not provide reverse resolution and is not a production
          quality or scalable DNS solution. Use the internal DNS
          server only for small deployments or for
          testing.</p>
</dd>
<dt><span class="term">PLC_MAIL_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: false</p>
<p>Set to false to suppress all e-mail notifications
	  and warnings.</p>
</dd>
<dt><span class="term">PLC_MAIL_SUPPORT_ADDRESS</span></dt>
<dd>
<p>
		  Type: email</p>
<p>
		  Default: root+support@localhost.localdomain</p>
<p>This address is used for support
	  requests. Support requests may include traffic complaints,
	  security incident reporting, web site malfunctions, and
	  general requests for information. We recommend that the
	  address be aliased to a ticketing system such as Request
	  Tracker.</p>
</dd>
<dt><span class="term">PLC_MAIL_BOOT_ADDRESS</span></dt>
<dd>
<p>
		  Type: email</p>
<p>
		  Default: root+install-msgs@localhost.localdomain</p>
<p>The API will notify this address when a problem
	  occurs during node installation or boot.</p>
</dd>
<dt><span class="term">PLC_MAIL_SLICE_ADDRESS</span></dt>
<dd>
<p>
		  Type: email</p>
<p>
		  Default: root+SLICE@localhost.localdomain</p>
<p>This address template is used for sending
	  e-mail notifications to slices. SLICE will be replaced with
	  the name of the slice.</p>
</dd>
<dt><span class="term">PLC_DB_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: true</p>
<p>Enable the database server on this
	  machine.</p>
</dd>
<dt><span class="term">PLC_DB_TYPE</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: postgresql</p>
<p>The type of database server. Currently, only
	  postgresql is supported.</p>
</dd>
<dt><span class="term">PLC_DB_HOST</span></dt>
<dd>
<p>
		  Type: hostname</p>
<p>
		  Default: localhost.localdomain</p>
<p>The fully qualified hostname of the database
	  server.</p>
</dd>
<dt><span class="term">PLC_DB_IP</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: 127.0.0.1</p>
<p>The IP address of the database server, if not
          resolvable by the configured DNS servers.</p>
</dd>
<dt><span class="term">PLC_DB_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 5432</p>
<p>The TCP port number through which the database
	  server should be accessed.</p>
</dd>
<dt><span class="term">PLC_DB_NAME</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: planetlab3</p>
<p>The name of the database to access.</p>
</dd>
<dt><span class="term">PLC_DB_USER</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: pgsqluser</p>
<p>The username to use when accessing the
	  database.</p>
</dd>
<dt><span class="term">PLC_DB_PASSWORD</span></dt>
<dd>
<p>
		  Type: password</p>
<p>
		  Default: </p>
<p>The password to use when accessing the
	  database. If left blank, one will be
	  generated.</p>
</dd>
<dt><span class="term">PLC_API_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: true</p>
<p>Enable the API server on this
	  machine.</p>
</dd>
<dt><span class="term">PLC_API_DEBUG</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: false</p>
<p>Enable verbose API debugging. Do not enable on
	  a production system!</p>
</dd>
<dt><span class="term">PLC_API_HOST</span></dt>
<dd>
<p>
		  Type: hostname</p>
<p>
		  Default: localhost.localdomain</p>
<p>The fully qualified hostname of the API
	  server.</p>
</dd>
<dt><span class="term">PLC_API_IP</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: 127.0.0.1</p>
<p>The IP address of the API server, if not
          resolvable by the configured DNS servers.</p>
</dd>
<dt><span class="term">PLC_API_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 80</p>
<p>The TCP port number through which the API
	  should be accessed. Warning: SSL (port 443) access is not
	  fully supported by the website code yet. We recommend that
	  port 80 be used for now and that the API server either run
	  on the same machine as the web server, or that they both be
	  on a secure wired network.</p>
</dd>
<dt><span class="term">PLC_API_PATH</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: /PLCAPI/</p>
<p>The base path of the API URL.</p>
</dd>
<dt><span class="term">PLC_API_MAINTENANCE_USER</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: maint@localhost.localdomain</p>
<p>The username of the maintenance account. This
	  account is used by local scripts that perform automated
	  tasks, and cannot be used for normal logins.</p>
</dd>
<dt><span class="term">PLC_API_MAINTENANCE_PASSWORD</span></dt>
<dd>
<p>
		  Type: password</p>
<p>
		  Default: </p>
<p>The password of the maintenance account. If
	  left blank, one will be generated. We recommend that the
	  password be changed periodically.</p>
</dd>
<dt><span class="term">PLC_API_MAINTENANCE_SOURCES</span></dt>
<dd>
<p>
		  Type: hostname</p>
<p>
		  Default: </p>
<p>A space-separated list of IP addresses allowed
	  to access the API through the maintenance account. The value
	  of this variable is set automatically to allow only the API,
	  web, and boot servers, and should not be
	  changed.</p>
</dd>
<dt><span class="term">PLC_API_SSL_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/api_ssl.key</p>
<p>The SSL private key to use for encrypting HTTPS
	  traffic. If non-existent, one will be
	  generated.</p>
</dd>
<dt><span class="term">PLC_API_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/api_ssl.crt</p>
<p>The corresponding SSL public certificate. By
	  default, this certificate is self-signed. You may replace
	  the certificate later with one signed by a root
	  CA.</p>
</dd>
<dt><span class="term">PLC_API_CA_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/api_ca_ssl.crt</p>
<p>The certificate of the root CA, if any, that
	  signed your server certificate. If your server certificate is
	  self-signed, then this file is the same as your server
	  certificate.</p>
</dd>
<dt><span class="term">PLC_WWW_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: true</p>
<p>Enable the web server on this
	  machine.</p>
</dd>
<dt><span class="term">PLC_WWW_DEBUG</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: false</p>
<p>Enable debugging output on web pages. Do not
	  enable on a production system!</p>
</dd>
<dt><span class="term">PLC_WWW_HOST</span></dt>
<dd>
<p>
		  Type: hostname</p>
<p>
		  Default: localhost.localdomain</p>
<p>The fully qualified hostname of the web
	  server.</p>
</dd>
<dt><span class="term">PLC_WWW_IP</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: 127.0.0.1</p>
<p>The IP address of the web server, if not
          resolvable by the configured DNS servers.</p>
</dd>
<dt><span class="term">PLC_WWW_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 80</p>
<p>The TCP port number through which the
	  unprotected portions of the web site should be
	  accessed.</p>
</dd>
<dt><span class="term">PLC_WWW_SSL_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 443</p>
<p>The TCP port number through which the protected
	  portions of the web site should be accessed.</p>
</dd>
<dt><span class="term">PLC_WWW_SSL_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/www_ssl.key</p>
<p>The SSL private key to use for encrypting HTTPS
	  traffic. If non-existent, one will be
	  generated.</p>
</dd>
<dt><span class="term">PLC_WWW_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/www_ssl.crt</p>
<p>The corresponding SSL public certificate for
	  the HTTP server. By default, this certificate is
	  self-signed. You may replace the certificate later with one
	  signed by a root CA.</p>
</dd>
<dt><span class="term">PLC_WWW_CA_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/www_ca_ssl.crt</p>
<p>The certificate of the root CA, if any, that
	  signed your server certificate. If your server certificate is
	  self-signed, then this file is the same as your server
	  certificate.</p>
</dd>
<dt><span class="term">PLC_BOOT_ENABLED</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: true</p>
<p>Enable the boot server on this
	  machine.</p>
</dd>
<dt><span class="term">PLC_BOOT_HOST</span></dt>
<dd>
<p>
		  Type: hostname</p>
<p>
		  Default: localhost.localdomain</p>
<p>The fully qualified hostname of the boot
	  server.</p>
</dd>
<dt><span class="term">PLC_BOOT_IP</span></dt>
<dd>
<p>
		  Type: ip</p>
<p>
		  Default: 127.0.0.1</p>
<p>The IP address of the boot server, if not
          resolvable by the configured DNS servers.</p>
</dd>
<dt><span class="term">PLC_BOOT_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 80</p>
<p>The TCP port number through which the
	  unprotected portions of the boot server should be
	  accessed.</p>
</dd>
<dt><span class="term">PLC_BOOT_SSL_PORT</span></dt>
<dd>
<p>
		  Type: int</p>
<p>
		  Default: 443</p>
<p>The TCP port number through which the protected
	  portions of the boot server should be
	  accessed.</p>
</dd>
<dt><span class="term">PLC_BOOT_SSL_KEY</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/boot_ssl.key</p>
<p>The SSL private key to use for encrypting HTTPS
	  traffic.</p>
</dd>
<dt><span class="term">PLC_BOOT_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/boot_ssl.crt</p>
<p>The corresponding SSL public certificate for
	  the HTTP server. By default, this certificate is
	  self-signed. You may replace the certificate later with one
	  signed by a root CA.</p>
</dd>
<dt><span class="term">PLC_BOOT_CA_SSL_CRT</span></dt>
<dd>
<p>
		  Type: file</p>
<p>
		  Default: /etc/planetlab/boot_ca_ssl.crt</p>
<p>The certificate of the root CA, if any, that
	  signed your server certificate. If your server certificate is
	  self-signed, then this file is the same as your server
	  certificate.</p>
</dd>
</dl></div>
</div>
<div class="appendix" lang="en">
<h2 class="title" style="clear: both">
<a name="id271742"></a>B. Development environment configuration variables</h2>
<div class="variablelist"><dl>
<dt><span class="term">PLC_DEVEL_FEDORA_RELEASE</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: 4</p>
<p>Version number of Fedora Core upon which to
	  base the build environment. Warning: Currently, only Fedora
	  Core 4 is supported.</p>
</dd>
<dt><span class="term">PLC_DEVEL_FEDORA_ARCH</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: i386</p>
<p>Base architecture of the build
	  environment. Warning: Currently, only i386 is
	  supported.</p>
</dd>
<dt><span class="term">PLC_DEVEL_FEDORA_URL</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: file:///usr/share/mirrors/fedora</p>
<p>Fedora Core mirror from which to install
	  filesystems.</p>
</dd>
<dt><span class="term">PLC_DEVEL_CVSROOT</span></dt>
<dd>
<p>
		  Type: string</p>
<p>
		  Default: /cvs</p>
<p>CVSROOT to use when checking out code.</p>
</dd>
<dt><span class="term">PLC_DEVEL_BOOTSTRAP</span></dt>
<dd>
<p>
		  Type: boolean</p>
<p>
		  Default: false</p>
<p>Controls whether MyPLC should be built inside
	  of its own development environment.</p>
</dd>
</dl></div>
</div>
<div class="bibliography">
<div class="titlepage"><div><div><h2 class="title">
<a name="id271824"></a>Bibliography</h2></div></div></div>
<div class="biblioentry">
<a name="TechsGuide"></a><p>[1] <span class="author"><span class="firstname">Mark</span> <span class="surname">Huang</span>. </span><span class="title"><i><a href="http://www.planet-lab.org/doc/TechsGuide.php" target="_top">PlanetLab
      Technical Contact's Guide</a></i>. </span></p>
</div>
</div>
</div><?php require('footer.php'); ?>
