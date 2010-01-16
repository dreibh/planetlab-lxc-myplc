# 
# $Id$
#

BINARIES = plc-config plc-config-tty db-config dns-config \
	clean-empty-dirs.py mtail.py \
	plc-check-ssl-peering.py plc-map.py plc-kml.py plc-orphan-accounts.py \
	support-scripts/renew_reminder.py support-scripts/gen_aliases.py 
INIT_SCRIPTS = api bootcd db dns functions gpg httpd mail network packages postgresql ssh ssl

INITS=$(addprefix plc.d/,$(INIT_SCRIPTS))

##########
tags:
	find . -type f | egrep -v '.svn/|~$$' | xargs etags

.PHONY: tags

########## sync
# 2 forms are supported
# (*) if your plc root context has direct ssh access:
# make sync PLC=private.one-lab.org
# (*) otherwise, entering through the root context
# make sync PLCHOST=testbox1.inria.fr GUEST=vplc03.inria.fr

ifdef GUEST
ifdef PLCHOST
SSHURL:=root@$(PLCHOST):/vservers/$(GUEST)
SSHCOMMAND:=ssh root@$(PLCHOST) vserver $(GUEST)
endif
endif
ifdef PLC
SSHURL:=root@$(PLC):/
SSHCOMMAND:=ssh root@$(PLC)
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc' 
RSYNC_EXCLUDES		:= --exclude .svn --exclude CVS --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -a -v $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(SSHURL))
	@echo "sync: You must define, either PLC, or PLCHOST & GUEST, on the command line"
	@echo "  e.g. make sync PLC=private.one-lab.org"
	@echo "  or   make sync PLCHOST=testbox1.inria.fr GUEST=vplc03.inria.fr"
	@exit 1
else
	+$(RSYNC) plc.init $(SSHURL)/etc/init.d/plc
	+$(RSYNC) $(BINARIES) $(SSHURL)/usr/bin
	+$(RSYNC) $(INITS) $(SSHURL)/etc/plc.d
	+$(RSYNC) plc_config.py $(SSHURL)/usr/lib/python2.5/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(SSHURL)/etc/planetlab/default_config.xml
	@echo XXXXXXXX you might need to run ssh root@$(PLC) service plc start 
endif

#################### convenience, for debugging only
# make +foo : prints the value of $(foo)
# make ++foo : idem but verbose, i.e. foo=$(foo)
++%: varname=$(subst +,,$@)
++%:
	@echo "$(varname)=$($(varname))"
+%: varname=$(subst +,,$@)
+%:
	@echo "$($(varname))"

