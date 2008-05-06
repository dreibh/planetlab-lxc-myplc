# 
# $Id$
#

BINARIES = plc-config plc-config-tty db-config dns-config plc-map.py clean-empty-dirs.py mtail.py \
	support-scripts/renew_reminder.py support-scripts/gen_aliases.py
INIT_SCRIPTS = api bootcd bootmanager crond db dns functions gpg httpd mail network packages postgresql ssh ssl syslog

INITS=$(addprefix plc.d/,$(INIT_SCRIPTS))

########## make sync PLCHOST=hostname
ifdef PLCHOST
ifdef VSERVER
PLCSSH:=root@$(PLCHOST):/vservers/$(VSERVER)
endif
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude CVS --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(PLCSSH))
	echo "sync: You must define PLCHOST and VSERVER on the command line"
	echo " e.g. make sync PLCHOST=private.one-lab.org VSERVER=myplc01" ; exit 1
else
	+$(RSYNC) guest.init $(PLCSSH)/etc/init.d/plc
	+$(RSYNC) $(BINARIES) $(PLCSSH)/usr/bin
	+$(RSYNC) $(INITS) $(PLCSSH)/etc/plc.d
	+$(RSYNC) plc_config.py $(PLCSSH)/usr/lib/python2.5/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(PLCSSH)/etc/planetlab/default_config.xml
	@echo XXXXXXXX You might consider running the following command
	@echo ssh $(PLCHOST) service plc start 
endif


tags:
	find . -type f | egrep -v '.svn/|~$$' | xargs etags
