#!/usr/bin/env plcsh
# checking ssl connection
# mimicks what PyCurl does

import sys
import pycurl

class check_ssl:

    def getpeername_post_request (self,local_peername) :
        methodname="GetPeerName"
        from PLC.GPG import gpg_sign
        signature = gpg_sign((),
                             self.options.PLC_ROOT_GPG_KEY,
                             self.options.PLC_ROOT_GPG_KEY_PUB,
                         methodname)
        post="""<?xml version='1.0'?>
<methodCall>
<methodName>GetPeerName</methodName>
<params>
<param>
<value><struct>
<member>
<name>AuthMethod</name>
<value><string>gpg</string></value>
</member>
<member>
<name>name</name>
<value><string>%s</string></value>
</member>
<member>
<name>signature</name>
<value><string>%s
</string></value>
</member>
</struct></value>
</param>
</params>
</methodCall>"""%(local_peername,signature)
        return post

    def check_url (self,url,local_peername,remote_peername,cert,timeout=10,verbose=1):
        curl=pycurl.Curl()
        curl.setopt(pycurl.NOSIGNAL, 1)
        
        # Follow redirections
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.URL, str(url))
        cert_path = str(cert)
        curl.setopt(pycurl.CAINFO, cert_path)
        curl.setopt(pycurl.SSL_VERIFYPEER, 2)

   # Set connection timeout
        if timeout:
            curl.setopt(pycurl.CONNECTTIMEOUT, timeout)
            curl.setopt(pycurl.TIMEOUT, timeout)

        curl.setopt(pycurl.VERBOSE, verbose)

    # Post request
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, self.getpeername_post_request(local_peername))

        import StringIO
        b = StringIO.StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)

        try:
            curl.perform()
            errcode = curl.getinfo(pycurl.HTTP_CODE)
            response = b.getvalue()
            print 'xmlrpc answer',response
            if response.find('Failed') >= 0:
                print 'FAILURE : failed to authenticate ?'
                return False
            elif response.find(remote_peername) <0:
                print 'FAILURE : xmlrpc round trip OK but peername does not match'
                return False
            else:
                print 'SUCCESS'
                return True

        except pycurl.error, err:
            (errcode, errmsg) = err
            if errcode == 60:
                print 'FAILURE', "SSL certificate validation failed, %r"%(errmsg)
            elif errcode != 200:
                print 'FAILURE', "HTTP error %d, errmsg %r" % (errcode,errmsg)
            return False

    def main (self):
        from optparse import OptionParser
        usage="%prog [options] local-peername remote-peername cacert hostname [ .. hostname ]"
        parser=OptionParser(usage=usage)
        parser.add_option('-s','--secret',default='/etc/planetlab/secring.gpg',
                          dest='PLC_ROOT_GPG_KEY',
                          help='local GPG secret ring')
        parser.add_option('-p','--public',default='/etc/planetlab/pubring.gpg',
                          dest='PLC_ROOT_GPG_KEY_PUB',
                          help='local GPG public ring')
        (self.options, args) = parser.parse_args()

        if len(args) < 4:
            parser.print_help()
            sys.exit(2)
        arg=0
        local_peername=args[arg] ; arg+=1
        remote_peername=args[arg] ; arg+=1
        cacert=args[arg]; arg+=1
        ok=False
        for hostname in args[arg:]:
# this does not seem to make any difference
#            for url_format in [ 'https://%s:443/PLCAPI/' , 'https://%s/PLCAPI/' ]:
            for url_format in [ 'https://%s/PLCAPI/' ]:
                url=url_format%hostname
                print '============================== Checking url=',url
                if self.check_url(url,local_peername,remote_peername,cacert):
                    ok=True
        if ok:
            return 0
        else:
            return 1
            
if __name__ == '__main__':
    sys.exit(check_ssl().main())
