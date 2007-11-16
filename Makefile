# 
# $Id$
#

BINARIES = plc-config plc-config-tty db-config dns-config refresh-peer.py plc-map.py clean-empty-dirs.py mtail.py
INIT_SCRIPTS = api bootcd bootmanager crond db dns functions gpg httpd mail network packages postgresql ssh ssl syslog

INITS=$(addprefix plc.d/,$(INIT_SCRIPTS))

########## make sync PLCHOST=hostname
ifdef PLCHOST
PLCSSH:=root@$(PLCHOST)
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude CVS --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(PLCSSH))
	echo "sync: You must define target host as PLCHOST on the command line"
	echo " e.g. make sync PLCHOST=private.one-lab.org" ; exit 1
else
	+$(RSYNC) host.init $(PLCSSH):/etc/init.d/plc
	+$(RSYNC) guest.init $(PLCSSH):/plc/root/etc/init.d/plc
	+$(RSYNC) $(BINARIES) $(PLCSSH):/plc/root/usr/bin
	+$(RSYNC) $(INITS) $(PLCSSH):/plc/root/etc/plc.d
	+$(RSYNC) plc_config.py $(PLCSSH):/plc/root/usr/lib/python2.4/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(PLCSSH):/plc/data/etc/planetlab/default_config.xml
	@echo XXXXXXXX You might consider running the following command
	@echo ssh $(PLCSSH) chroot /plc/root service plc start 
endif


tags:
	find . -type f | egrep -v '.svn/|~$$' | xargs etags
