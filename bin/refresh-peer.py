#!/usr/bin/env plcsh

import sys,time,os,os.path

logdir="/var/log/peers"

#
# WARNING: the bulk of this output now goes into
# /var/log/plcapi.log 
#

def Run (peername):
    timestring=time.strftime("%Y-%m-%d-%H-%M-%S")
    print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',peername
    print 'RefreshPeer on %s - starting on %s'%(peername,timestring)
    print 'xxxxxxxxxx'
    sys.stdout.flush()
    start=time.time()
    result=RefreshPeer(peername)
    finish=time.time()

    print 'Total duration',finish-start
    print 'xxxxxxxxxx timers:'
    keys=result.keys()
    keys.sort()
    for key in keys:
        print key,result[key]
    sys.stdout.flush()
    sys.stderr.flush()

def RunInLog (peername):
    monthstring=time.strftime("%Y-%m")
    if not os.path.isdir(logdir):
        os.mkdir(logdir)
    logname="%s/refresh-peer-%s-%s.log"%(logdir,peername,monthstring)
    sys.stdout=open(logname,'a')
    sys.stderr=sys.stdout
    Run(peername)
    sys.stderr.close()
    sys.stdout.close()

if __name__ == "__main__":
    
    for peername in sys.argv[1:]:
        RunInLog (peername)


