##########
tags:
	find . -type f | egrep -v '\.git/|~$$' | xargs etags

.PHONY: tags

########## sync
# 2 forms are supported
# (*) if your plc root context has direct ssh access:
# make sync PLC=private.one-lab.org
# (*) otherwise, for test deployments, use on your testmaster
# $ run export
# and cut'n paste the export lines before you run make sync

ifdef PLC
SSHURL:=root@$(PLC):/
SSHCOMMAND:=ssh root@$(PLC)
else
SSHURL:=root@$(PLCHOSTLXC):/vservers/$(GUESTNAME)/
SSHCOMMAND:=ssh root@$(PLCHOSTLXC) ssh $(GUESTHOSTNAME)
endif

LOCAL_RSYNC_EXCLUDES	:= --exclude '*.pyc'
RSYNC_EXCLUDES		:= --exclude '*~' --exclude TAGS $(LOCAL_RSYNC_EXCLUDES)
RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC			:= rsync -ai $(RSYNC_COND_DRY_RUN) $(RSYNC_EXCLUDES)

sync:
ifeq (,$(SSHURL))
	@echo "sync: I need more info from the command line, e.g."
	@echo "  make sync PLC=boot.planetlab.eu"
	@echo "  make sync PLCHOSTVS=.. GUESTNAME=.."
	@echo "  make sync PLCHOSTLXC=.. GUESTNAME=.. GUESTHOSTNAME=.."
	@exit 1
else
	+$(RSYNC) systemd/plc-ctl $(SSHURL)/usr/bin/plc-ctl
	+$(RSYNC) systemd/plc.service $(SSHURL)/usr/lib/systemd/system/plc.service
	+$(RSYNC) bin/ $(SSHURL)/usr/bin/
	+$(RSYNC) plc.d/ $(SSHURL)/etc/plc.d/
	+$(RSYNC) db-config.d/ $(SSHURL)/etc/planetlab/db-config.d/
	+$(RSYNC) plc_config.py $(SSHURL)/usr/lib\*/python3.\*/site-packages/plc_config.py
	+$(RSYNC) default_config.xml $(SSHURL)/etc/planetlab/default_config.xml
	@echo XXXXXXXX you might need to run $(SSHCOMMAND) service plc start
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
