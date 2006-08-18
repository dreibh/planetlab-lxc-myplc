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
<a name="id2703030"></a>MyPLC User's Guide</h1></div>
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
<tr>
<td align="left">Revision 1.2</td>
<td align="left">August 18, 2006</td>
<td align="left">TPT</td>
</tr>
<tr><td align="left" colspan="3">
	<p>Review section on configuration and introduce <span><strong class="command">plc-config-tty</strong></span>.</p>
	<p>Present implementation details last.</p>
	</td></tr>
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
<dt><span class="section"><a href="#id2749839">1. Overview</a></span></dt>
<dd><dl><dt><span class="section"><a href="#id2750165">1.1.  Purpose of the <span class="emphasis"><em> myplc-devel
    </em></span> package </a></span></dt></dl></dd>
<dt><span class="section"><a href="#Requirements">2.  Requirements </a></span></dt>
<dt><span class="section"><a href="#Installation">3. Installating and using MyPLC</a></span></dt>
<dd><dl>
<dt><span class="section"><a href="#id2749479">3.1. Installing MyPLC.</a></span></dt>
<dt><span class="section"><a href="#QuickStart">3.2.  QuickStart </a></span></dt>
<dt><span class="section"><a href="#Configuration">3.3. Changing the configuration</a></span></dt>
<dt><span class="section"><a href="#LoginRealUser">3.4.  Login as a real user </a></span></dt>
<dt><span class="section"><a href="#id2750676">3.5. Installing nodes</a></span></dt>
<dt><span class="section"><a href="#id2801620">3.6. Administering nodes</a></span></dt>
<dt><span class="section"><a href="#id2801720">3.7. Creating a slice</a></span></dt>
<dt><span class="section"><a href="#StartupSequence">3.8. Understanding the startup sequence</a></span></dt>
<dt><span class="section"><a href="#FilesInvolvedRuntime">3.9.  Files and directories
    involved in <span class="emphasis"><em>myplc</em></span></a></span></dt>
</dl></dd>
<dt><span class="section"><a href="#DevelopmentEnvironment">4. Rebuilding and customizing MyPLC</a></span></dt>
<dd><dl>
<dt><span class="section"><a href="#id2802612">4.1. Installation</a></span></dt>
<dt><span class="section"><a href="#id2802667">4.2. Configuration</a></span></dt>
<dt><span class="section"><a href="#FilesInvolvedDevel">4.3.  Files and directories
    involved in <span class="emphasis"><em>myplc-devl</em></span></a></span></dt>
<dt><span class="section"><a href="#id2802931">4.4. Fedora Core 4 mirror requirement</a></span></dt>
<dt><span class="section"><a href="#BuildingMyPLC">4.5. Building MyPLC</a></span></dt>
<dt><span class="section"><a href="#UpdatingCVS">4.6. Updating CVS</a></span></dt>
</dl></dd>
<dt><span class="appendix"><a href="#VariablesRuntime">A. Configuration variables (for <span class="emphasis"><em>myplc</em></span>)</a></span></dt>
<dt><span class="appendix"><a href="#VariablesDevel">B. Development configuration variables (for <span class="emphasis"><em>myplc-devel</em></span>)</a></span></dt>
<dt><span class="bibliography"><a href="#id2806472">Bibliography</a></span></dt>
</dl>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="id2749839"></a>1. Overview</h2></div></div></div>
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
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id2750165"></a>1.1.  Purpose of the <span class="emphasis"><em> myplc-devel
    </em></span> package </h3></div></div></div>
<p> The <span class="emphasis"><em>myplc</em></span> package comes with all
    required node software, rebuilt from the public PlanetLab CVS
    repository. If for any reason you need to implement your own
    customized version of this software, you can use the
    <span class="emphasis"><em>myplc-devel</em></span> package instead, for setting up
    your own development environment, including a local CVS
    repository; you can then freely manage your changes and rebuild
    your customized version of <span class="emphasis"><em>myplc</em></span>. We also
    provide good practices, that will then allow you to resync your local
    CVS repository with any further evolution on the mainstream public
    PlanetLab software. </p>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="Requirements"></a>2.  Requirements </h2></div></div></div>
<p> <span class="emphasis"><em>myplc</em></span> and
  <span class="emphasis"><em>myplc-devel</em></span> were designed as
  <span><strong class="command">chroot</strong></span> jails so as to reduce the requirements on
  your host operating system. So in theory, these distributions should
  work on virtually any Linux 2.6 based distribution, whether it
  supports rpm or not. </p>
<p> However, things are never that simple and there indeed are
  some known limitations to this, so here are a couple notes as a
  recommended reading before you proceed with the installation.</p>
<p> As of 17 August 2006 (i.e <span class="emphasis"><em>myplc-0.5-2</em></span>) :</p>
<div class="itemizedlist"><ul type="disc">
<li><p> The software is vastly based on <span class="emphasis"><em>Fedora
  Core 4</em></span>. Please note that the build server at Princeton
  runs <span class="emphasis"><em>Fedora Core 2</em></span>, togother with a upgraded
  version of yum. 
  </p></li>
<li>
<p> myplc and myplc-devel are known to work on both
  <span class="emphasis"><em>Fedora Core 2</em></span> and <span class="emphasis"><em>Fedora Core
  4</em></span>. Please note however that, on fc4 at least, it is
  highly recommended to use the <span class="application">Security Level
  Configuration</span> utility and to <span class="emphasis"><em>switch off
  SElinux</em></span> on your box because : </p>
<div class="itemizedlist"><ul type="circle">
<li><p>
  myplc requires you to run SElinux as 'Permissive' at most
	</p></li>
<li><p>
  myplc-devel requires you to turn SElinux Off.
	</p></li>
</ul></div>
</li>
<li><p> In addition, as far as myplc is concerned, you
  need to check your firewall configuration since you need, of course,
  to open up the <span class="emphasis"><em>http</em></span> and
  <span class="emphasis"><em>https</em></span> ports, so as to accept connections from
  the managed nodes and from the users desktops. </p></li>
</ul></div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="Installation"></a>3. Installating and using MyPLC</h2></div></div></div>
<p>Though internally composed of commodity software
    subpackages, MyPLC should be treated as a monolithic software
    application. MyPLC is distributed as single RPM package that has
    no external dependencies, allowing it to be installed on
    practically any Linux 2.6 based distribution.</p>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id2749479"></a>3.1. Installing MyPLC.</h3></div></div></div>
<div class="itemizedlist"><ul type="disc">
<li>
<p>If your distribution supports RPM:</p>
<pre class="programlisting"># rpm -U http://build.planet-lab.org/build/myplc-0_4-rc1/RPMS/i386/myplc-0.4-1.planetlab.i386.rpm</pre>
</li>
<li>
<p>If your distribution does not support RPM:</p>
<pre class="programlisting"># cd /tmp
# wget http://build.planet-lab.org/build/myplc-0_4-rc1/RPMS/i386/myplc-0.4-1.planetlab.i386.rpm
# cd /
# rpm2cpio /tmp/myplc-0.4-1.planetlab.i386.rpm | cpio -diu</pre>
</li>
</ul></div>
<p> The <a href="#FilesInvolvedRuntime" title="3.9.  Files and directories
    involved in myplc">Section 3.9, “ Files and directories
    involved in <span class="emphasis"><em>myplc</em></span>”</a> below explains in
    details the installation strategy and the miscellaneous files and
    directories involved.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="QuickStart"></a>3.2.  QuickStart </h3></div></div></div>
<p> On a Red Hat or Fedora host system, it is customary to use
    the <span><strong class="command">service</strong></span> command to invoke System V init
    scripts. As the examples suggest, the service must be started as root:</p>
<div class="example">
<a name="id2749652"></a><p class="title"><b>Example 1. Starting MyPLC:</b></p>
<pre class="programlisting"># service plc start</pre>
</div>
<div class="example">
<a name="id2749665"></a><p class="title"><b>Example 2. Stopping MyPLC:</b></p>
<pre class="programlisting"># service plc stop</pre>
</div>
<p> In <a href="#StartupSequence" title="3.8. Understanding the startup sequence">Section 3.8, “Understanding the startup sequence”</a>, we provide greater
    details that might be helpful in the case where the service does
    not seem to take off correctly.</p>
<p>Like all other registered System V init services, MyPLC is
    started and shut down automatically when your host system boots
    and powers off. You may disable automatic startup by invoking the
    <span><strong class="command">chkconfig</strong></span> command on a Red Hat or Fedora host
    system:</p>
<div class="example">
<a name="id2750316"></a><p class="title"><b>Example 3. Disabling automatic startup of MyPLC.</b></p>
<pre class="programlisting"># chkconfig plc off</pre>
</div>
<div class="example">
<a name="id2750328"></a><p class="title"><b>Example 4. Re-enabling automatic startup of MyPLC.</b></p>
<pre class="programlisting"># chkconfig plc on</pre>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="Configuration"></a>3.3. Changing the configuration</h3></div></div></div>
<p>After verifying that MyPLC is working correctly, shut it
      down and begin changing some of the default variable
      values. Shut down MyPLC with <span><strong class="command">service plc stop</strong></span>
      (see <a href="#QuickStart" title="3.2.  QuickStart ">Section 3.2, “ QuickStart ”</a>). </p>
<p> The preferred option for changing the configuration is to
      use the <span><strong class="command">plc-config-tty</strong></span> tool. This tools comes
      with the root image, so you need to have it mounted first. The
      full set of applicable variables is described in <a href="#VariablesDevel" title="B. Development configuration variables (for myplc-devel)">Appendix B, <i>Development configuration variables (for <span class="emphasis"><em>myplc-devel</em></span>)</i></a>, but using the <span><strong class="command">u</strong></span>
      guides you to the most useful ones. Here is sample session:
      </p>
<div class="example">
<a name="id2750396"></a><p class="title"><b>Example 5. Using plc-config-tty for configuration:</b></p>
<pre class="programlisting"># service plc mount
Mounting PLC:                                              [  OK  ]
# chroot /plc/root su - 
&lt;plc&gt; # plc-config-tty
Config file /etc/planetlab/configs/site.xml located under a non-existing directory
Want to create /etc/planetlab/configs [y]/n ? y
Created directory /etc/planetlab/configs
Enter command (u for usual changes, w to save, ? for help) u
== PLC_NAME : [PlanetLab Test] OneLab
== PLC_ROOT_USER : [root@localhost.localdomain] root@odie.inria.fr
== PLC_ROOT_PASSWORD : [root] plain-passwd
== PLC_MAIL_SUPPORT_ADDRESS : [root+support@localhost.localdomain] support@one-lab.org
== PLC_DB_HOST : [localhost.localdomain] odie.inria.fr
== PLC_API_HOST : [localhost.localdomain] odie.inria.fr
== PLC_WWW_HOST : [localhost.localdomain] odie.inria.fr
== PLC_BOOT_HOST : [localhost.localdomain] odie.inria.fr
== PLC_NET_DNS1 : [127.0.0.1] 138.96.250.248
== PLC_NET_DNS2 : [None] 138.96.250.249
Enter command (u for usual changes, w to save, ? for help) w
Wrote /etc/planetlab/configs/site.xml
Merged
        /etc/planetlab/default_config.xml
and     /etc/planetlab/configs/site.xml
into    /etc/planetlab/plc_config.xml
You might want to type 'r' (restart plc) or 'q' (quit)
Enter command (u for usual changes, w to save, ? for help) r
==================== Stopping plc
...
==================== Starting plc
...
Enter command (u for usual changes, w to save, ? for help) q
&lt;plc&gt; # exit
# 
</pre>
</div>
<p>If you used this method for configuring, you can skip to
      the <a href="#LoginRealUser" title="3.4.  Login as a real user ">Section 3.4, “ Login as a real user ”</a>. As an alternative to using
      <span><strong class="command">plc-config-tty</strong></span>, you may also use a text
      editor, but this requires some understanding on how the
      configuration files are used within myplc. The
      <span class="emphasis"><em>default</em></span> configuration is stored in a file
      named <code class="filename">/etc/planetlab/default_config.xml</code>,
      that is designed to remain intact. You may store your local
      changes in any file located in the <code class="filename">configs/</code>
      sub-directory, that are loaded on top of the defaults. Finally
      the file <code class="filename">/etc/planetlab/plc_config.xml</code> is
      loaded, and the resulting configuration is stored in the latter
      file, that is used as a reference.</p>
<p> Using a separate file for storing local changes only, as
      <span><strong class="command">plc-config-tty</strong></span> does, is not a workable option
      with a text editor because it would involve tedious xml
      re-assembling. So your local changes should go in
      <code class="filename">/etc/planetlab/plc_config.xml</code>. Be warned
      however that any change you might do this way could be lost if
      you use <span><strong class="command">plc-config-tty</strong></span> later on. </p>
<p>This file is a self-documenting configuration file written
      in XML. Variables are divided into categories. Variable
      identifiers must be alphanumeric, plus underscore. A variable is
      referred to canonically as the uppercase concatenation of its
      category identifier, an underscore, and its variable
      identifier. Thus, a variable with an <code class="literal">id</code> of
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
<p> After changing these variables,
      save the file, then restart MyPLC with <span><strong class="command">service plc
      start</strong></span>. You should notice that the password of the
      default administrator account is no longer
      <code class="literal">root</code>, and that the default site name includes
      the name of your PLC installation instead of PlanetLab. As a
      side effect of these changes, the ISO images for the boot CDs
      now have new names, so that you can freely remove the ones names
      after 'PlanetLab Test', which is the default value of
      <code class="envar">PLC_NAME</code> </p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="LoginRealUser"></a>3.4.  Login as a real user </h3></div></div></div>
<p>Now that myplc is up and running, you can connect to the
      web site that by default runs on port 80. You can either
      directly use the default administrator user that you configured
      in <code class="envar">PLC_ROOT_USER</code> and
      <code class="envar">PLC_ROOT_PASSWORD</code>, or create a real user through
      the 'Joining' tab. Do not forget to  select both PI and tech
      roles, and to select the only site created at this stage.
      Login as the administrator to enable this user, then login as
      the real user.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id2750676"></a>3.5. Installing nodes</h3></div></div></div>
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
<a name="id2801620"></a>3.6. Administering nodes</h3></div></div></div>
<p>You may administer nodes as <code class="literal">root</code> by
      using the SSH key stored in
      <code class="filename">/etc/planetlab/root_ssh_key.rsa</code>.</p>
<div class="example">
<a name="id2801642"></a><p class="title"><b>Example 6. Accessing nodes via SSH. Replace
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
<a name="id2801720"></a>3.7. Creating a slice</h3></div></div></div>
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
<a name="id2801783"></a><p class="title"><b>Example 7. Forcing slice creation on a node.</b></p>
<pre class="programlisting"># Update slices.xml immediately
service plc start crond

# Kick the Slice Creation Service on a particular node.
ssh -i /etc/planetlab/root_ssh_key.rsa root@node \
vserver pl_conf exec service pl_conf restart</pre>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="StartupSequence"></a>3.8. Understanding the startup sequence</h3></div></div></div>
<p>During service startup described in <a href="#QuickStart" title="3.2.  QuickStart ">Section 3.2, “ QuickStart ”</a>, observe the output of this command for
    any failures. If no failures occur, you should see output similar
    to the following:</p>
<div class="example">
<a name="id2801822"></a><p class="title"><b>Example 8. A successful MyPLC startup.</b></p>
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
      /plc/root.img</code>, then SELinux may be enabled. See <a href="#Requirements" title="2.  Requirements ">Section 2, “ Requirements ”</a> above for details.</p></li>
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
      <a href="#Configuration" title="3.3. Changing the configuration">Section 3.3, “Changing the configuration”</a>) does not resolve to
      the host on which the API server has been enabled. By default,
      all services, including the API server, are enabled and run on
      the same host, so check that <code class="envar">PLC_API_HOST</code> is
      either <code class="filename">localhost</code> or resolves to a local IP
      address. Also check that <code class="envar">PLC_ROOT_USER</code> looks like
      an e-mail address.</p></li>
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
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="FilesInvolvedRuntime"></a>3.9.  Files and directories
    involved in <span class="emphasis"><em>myplc</em></span></h3></div></div></div>
<p>MyPLC installs the following files and directories:</p>
<div class="orderedlist"><ol type="1">
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
<div class="itemizedlist"><ul type="disc">
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
<li><p><code class="filename">/root</code>: this is the
	  location of the root-user's homedir, and for your
	  convenience is stored under <code class="filename">/data</code> so
	  that your local customizations survive across
	  updates - this feature is inherited from the
	  <span><strong class="command">myplc-devel</strong></span> package, where it is probably
	  more useful. </p></li>
</ul></div>
</li>
<li><p><a name="MyplcInitScripts"></a><code class="filename">/etc/init.d/plc</code>: This file
	is a System V init script installed on your host filesystem,
	that allows you to start up and shut down MyPLC with a single
	command, as described in <a href="#QuickStart" title="3.2.  QuickStart ">Section 3.2, “ QuickStart ”</a>.</p></li>
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
</ol></div>
</div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h2 class="title" style="clear: both">
<a name="DevelopmentEnvironment"></a>4. Rebuilding and customizing MyPLC</h2></div></div></div>
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
<a name="id2802612"></a>4.1. Installation</h3></div></div></div>
<p>Install the MyPLC development environment similarly to how
      you would install MyPLC. You may install both packages on the same
      host system if you wish. As with MyPLC, the MyPLC development
      environment should be treated as a monolithic software
      application, and any files present in the
      <span><strong class="command">chroot</strong></span> jail should not be modified directly, as
      they are subject to upgrade.</p>
<div class="itemizedlist"><ul type="disc">
<li>
<p>If your distribution supports RPM:</p>
<pre class="programlisting"># rpm -U http://build.planet-lab.org/build/myplc-0_4-rc2/RPMS/i386/myplc-devel-0.4-2.planetlab.i386.rpm</pre>
</li>
<li>
<p>If your distribution does not support RPM:</p>
<pre class="programlisting"># cd /tmp
# wget http://build.planet-lab.org/build/myplc-0_4-rc2/RPMS/i386/myplc-devel-0.4-2.planetlab.i386.rpm
# cd /
# rpm2cpio /tmp/myplc-devel-0.4-2.planetlab.i386.rpm | cpio -diu</pre>
</li>
</ul></div>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="id2802667"></a>4.2. Configuration</h3></div></div></div>
<p> The default configuration should work as-is on most
      sites. Configuring the development package can be achieved in a
      similar way as for <span class="emphasis"><em>myplc</em></span>, as described in
      <a href="#Configuration" title="3.3. Changing the configuration">Section 3.3, “Changing the configuration”</a>. <span><strong class="command">plc-config-tty</strong></span> supports a
      <span class="emphasis"><em>-d</em></span> option for supporting the
      <span class="emphasis"><em>myplc-devel</em></span> case, that can be useful in a
      context where it would not guess it by itself.  Refer to <a href="#VariablesDevel" title="B. Development configuration variables (for myplc-devel)">Appendix B, <i>Development configuration variables (for <span class="emphasis"><em>myplc-devel</em></span>)</i></a> for a list of variables.</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="FilesInvolvedDevel"></a>4.3.  Files and directories
    involved in <span class="emphasis"><em>myplc-devl</em></span></h3></div></div></div>
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
	    <code class="filename">myplc-devel</code>. See <a href="#UpdatingCVS" title="4.6. Updating CVS">Section 4.6, “Updating CVS”</a> for more information about updating
	    PlanetLab source code.</p></li>
<li><p><code class="filename">/build</code>:
	    Builds are stored in this directory. This directory is bind
	    mounted onto <code class="filename">/plc/devel/root/build</code> so that
	    it is accessible as <code class="filename">/build</code> from within the
	    <span><strong class="command">chroot</strong></span> jail. The build scripts in this
	    directory are themselves source controlled; see <a href="#BuildingMyPLC" title="4.5. Building MyPLC">Section 4.5, “Building MyPLC”</a> for more information about executing
	    builds.</p></li>
<li><p><code class="filename">/root</code>: this is the
	    location of the root-user's homedir, and for your
	    convenience is stored under <code class="filename">/data</code> so
	    that your local customizations survive across
	    updates. </p></li>
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
<a name="id2802931"></a>4.4. Fedora Core 4 mirror requirement</h3></div></div></div>
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
<a name="id2803072"></a><p class="title"><b>Example 9. Setting up a local Fedora Core 4 repository.</b></p>
<pre class="programlisting"># mkdir -p /plc/devel/data/fedora
# cd /plc/devel/data/fedora

# for repo in core/4/i386/os core/updates/4/i386 extras/4/i386 ; do
&gt;     wget -m -nH --cut-dirs=3 http://coblitz.planet-lab.org/pub/fedora/linux/$repo
&gt; done</pre>
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
<a name="BuildingMyPLC"></a>4.5. Building MyPLC</h3></div></div></div>
<p>All PlanetLab source code modules are built and installed
      as RPMS. A set of build scripts, checked into the
      <code class="filename">build/</code> directory of the PlanetLab CVS
      repository, eases the task of rebuilding PlanetLab source
      code.</p>
<p> Before you try building MyPLC, you might check the
      configuration, in a file named
      <span class="emphasis"><em>plc_config.xml</em></span> that relies on a very
      similar model as MyPLC, located in
      <span class="emphasis"><em>/etc/planetlab</em></span> within the chroot jail, or
      in <span class="emphasis"><em>/plc/devel/data/etc/planetlab</em></span> from the
      root context. The set of applicable variables is described in
      <a href="#VariablesDevel" title="B. Development configuration variables (for myplc-devel)">Appendix B, <i>Development configuration variables (for <span class="emphasis"><em>myplc-devel</em></span>)</i></a>. </p>
<p>To build MyPLC, or any PlanetLab source code module, from
      within the MyPLC development environment, execute the following
      commands as root:</p>
<div class="example">
<a name="id2803174"></a><p class="title"><b>Example 10. Building MyPLC.</b></p>
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
      directory of your MyPLC installation (see <a href="#Installation" title="3. Installating and using MyPLC">Section 3, “Installating and using MyPLC”</a>).</p>
</div>
<div class="section" lang="en">
<div class="titlepage"><div><div><h3 class="title">
<a name="UpdatingCVS"></a>4.6. Updating CVS</h3></div></div></div>
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
      use CVS's support for vendor branches to track changes, as
      described <a href="http://ximbiot.com/cvs/wiki/index.php?title=CVS--Concurrent_Versions_System_v1.12.12.1:_Tracking_third-party_sources" target="_top">here</a>
      and <a href="http://cvsbook.red-bean.com/cvsbook.html#Tracking%20Third-Party%20Sources%20(Vendor%20Branches)" target="_top">here</a>.
      Vendor branches ease the task of merging upstream changes with
      your local modifications. To import a new snapshot into your
      local repository (for example, if you have just upgraded from
      <code class="filename">myplc-devel-0.4-2</code> to
      <code class="filename">myplc-devel-0.4-3</code> and you notice the new
      repository in <code class="filename">/plc/devel/data/cvs-0.4-3</code>),
      execute the following commands as root from within the MyPLC
      development environment:</p>
<div class="example">
<a name="id2803332"></a><p class="title"><b>Example 11. Updating /data/cvs from /data/cvs-0.4-3.</b></p>
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
cvs -d /cvs import -m "Merging myplc-0.4-3" -ko -I ! . planetlab myplc-0_4-3
popd
rm -rf $TMP</pre>
</div>
<p>If there are any merge conflicts, use the command
      suggested by CVS to help the merge. Explaining how to fix merge
      conflicts is beyond the scope of this document; consult the CVS
      documentation for more information on how to use CVS.</p>
</div>
</div>
<div class="appendix" lang="en">
<h2 class="title" style="clear: both">
<a name="VariablesRuntime"></a>A. Configuration variables (for <span class="emphasis"><em>myplc</em></span>)</h2>
<p>Listed below is the set of standard configuration variables
    and their default values, defined in the template
    <code class="filename">/etc/planetlab/default_config.xml</code>. Additional
    variables and their defaults may be defined in site-specific XML
    templates that should be placed in
    <code class="filename">/etc/planetlab/configs/</code>.</p>
<p>This information is available online within
    <span><strong class="command">plc-config-tty</strong></span>, e.g.:</p>
<div class="example">
<a name="id2803414"></a><p class="title"><b>Example A.1. Advanced usage of plc-config-tty</b></p>
<pre class="programlisting">&lt;plc&gt; # plc-config-tty
Enter command (u for usual changes, w to save, ? for help) V plc_dns
========== Category = PLC_DNS
### Enable DNS
# Enable the internal DNS server. The server does not provide reverse
# resolution and is not a production quality or scalable DNS solution.
# Use the internal DNS server only for small deployments or for testing.
PLC_DNS_ENABLED
</pre>
</div>
<p> List of the <span><strong class="command">myplc</strong></span> configuration variables:</p>
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
<a name="VariablesDevel"></a>B. Development configuration variables (for <span class="emphasis"><em>myplc-devel</em></span>)</h2>
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
		  Default: file:///data/fedora</p>
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
<a name="id2806472"></a>Bibliography</h2></div></div></div>
<div class="biblioentry">
<a name="TechsGuide"></a><p>[1] <span class="author"><span class="firstname">Mark</span> <span class="surname">Huang</span>. </span><span class="title"><i><a href="http://www.planet-lab.org/doc/TechsGuide.php" target="_top">PlanetLab
      Technical Contact's Guide</a></i>. </span></p>
</div>
</div>
</div><?php require('footer.php'); ?>
