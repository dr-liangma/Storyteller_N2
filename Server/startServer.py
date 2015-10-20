#========================================#
__author__="Liang Ma"
__version__='3.2'
__description__='''
- start the server ver8.0
'''
#========================================#


import time
import sys

from Server.serverAPI.server import Server
from Server.serverAPI.serverConst import *
from Server.serverAPI.uEngine import Engine

def main():
    engineList=[]
    argv=sys.argv[1:]
    for lang in argv:
        if lang in ENGINE_LANGUAGE:
            engineList.append(Engine(ENGINE_DIRECTORY,
                             ENGINE_PORT,lang,js=r'storyteller_v1.0.js'))
            time.sleep(SECS_STARTENGINE)
            break
    
    s=Server((SERVER_HOST,SERVER_PORT),WORKING_DIRECTORY)
    s.startServer()

if __name__=='__main__':
    main()
