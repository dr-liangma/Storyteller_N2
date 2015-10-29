'''
Created on Oct 21, 2015

@author: d038395
'''

import http.server
import json
import os
import subprocess
import time


from Server.serverAPI.serverConst import * # @UnusedWildImport
from commonAPI.constValue import * # @UnusedWildImport
from commonAPI.netOp import httpPOST, httpGET


class CALL_BACK():
    def __init__(self,url,packetList):
        if type(url) is str:
            ulist=url.split(':')
            self.url=(ulist[0],int(ulist[1]))
        elif type(url) is tuple and type(url[1]) is int:
            self.url=url
        else:
            raise TypeError('The data type of ip address or port of a server is not correct.')
        self.server=None
        self.packetList=packetList

    def startServer(self):  
        self.server = http.server.HTTPServer(self.url, httpHandler(self.packetList))
        print('Server Call Back starts @%s:%s at time'%self.url,time.asctime())
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.server_close()
            print('Server Call Back is stopped at time',time.asctime())
        

class httpHandler(http.server.BaseHTTPRequestHandler):
    
    def __init__(self,packetList):
        super().__init__(self)
        self.packetList=packetList
    
    def do_HEAD(self,content):
        self.send_response(content)
        self.send_header("Content-type", "text/html")
        self.end_headers()


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        auid=self.headers['id']
#        portBias=int(self.headers['portBias'])
        audioname=self.headers['audioname']
        language=self.headers['language']
        operating_mode=self.headers['mode']
        

        rPort=ENGINE_PORT
        URL_Server='%s:%s'%(ENGINE_HOST_IP,rPort)
        try:
            response=httpGET(URL_Server,r'/langpackdetails')
            jstr=''
            if response.status==200:
                jbyte=response.read()
                jstr=jbyte.decode('utf-8')
            else:
                self.do_HEAD(404)
            jdict=json.loads(jstr)
        except:
            self.do_HEAD(404)
            return
        if jdict['baseLanguage'].lower()!=language or jdict['modes'][0].lower()!=operating_mode:
            self.do_HEAD(400)
            return
        
        post_data = self.rfile.read(content_length)
    
        audioDir=os.path.join(WORKING_DIRECTORY,str(auid))
        if not os.path.exists(audioDir):
            os.mkdir(audioDir)
        audiopathOrg=os.path.join(audioDir,audioname)
        audiopath=os.path.join(audioDir,'%s.wav'%str(auid))
        with open(audiopathOrg,'wb') as fw:
            fw.write(post_data)
    
        command=[FFMPEG_PROG_PATH,'-i',audiopathOrg,
                           '-ar','16000',audiopath]
    
        try:
            p=subprocess.Popen(command)
            p.wait(20)
        except subprocess.TimeoutExpired:
            self.do_HEAD(406)
            return
    
        if not os.path.exists(audiopath):
            self.do_HEAD(406)
            return
    
#        rPort=ENGINE_PORT+ENGINE_PORT_STEP*(portBias%NUMBER_OF_ENGINES)
        rPort=ENGINE_PORT
        URL_Server='%s:%s'%(ENGINE_HOST_IP,rPort)
        hrs={'Content-type':'application/json'}
        
        model={"name":language}
        firstChannel={'url':audiopath,'format':'wave'}
        channels={'firstChannelLabel':firstChannel}
        data={'reference':auid,'operating_mode':operating_mode,
                                              'model':model,'channels':channels}
        uData=json.dumps(data)
        binary_data = uData.encode('utf-8')
        print("POST on %s"%URL_Server)
        response = httpPOST(URL_Server,binary_data,hrs)
        try:
            self.do_HEAD(response.status)
        except AttributeError:
            self.do_HEAD(404)
        except ConnectionRefusedError:
            self.do_HEAD()


    def do_GET(self):
        #portBias=int(self.headers['portBias'])
        #rPort=ENGINE_PORT+ENGINE_PORT_STEP*(portBias%NUMBER_OF_ENGINES)
        rPort=ENGINE_PORT
        URL_Server='%s:%s'%(ENGINE_HOST_IP,rPort)
        response=httpGET(URL_Server,self.path)
        jstr=''
        try:
            if response.status==200:
                self.do_HEAD(200)
                jstr=response.read()
                self.wfile.write(jstr)
            else:
                self.do_HEAD(404)
        except AttributeError:
            self.do_HEAD(404)
        except TimeoutError:
            self.do_HEAD(404)
        except ConnectionRefusedError:
            self.do_HEAD(404)



if __name__ == '__main__':
    pass