#========================================#
__author__="Liang Ma"
__description__='''

'''
import os
from Client.clientAPI.clientConst import STOP_WORDS_LIST,NUM_OF_KEYWORDS,TITLE_FACTOR

#========================================#
class myHTML():
    def __init__(self,chann,filename,wLong):
        self.chann=sorted(chann,key=lambda x: float(x[0]))
        self.name=filename
        self.filename=os.path.splitext(self.name)[0]  
        self.wLong=wLong-1
    def getFreq(self):
        words=[x[1].lower() for x in self.chann if not x[1].lower() in STOP_WORDS_LIST]
        words+=self.filename.split()*TITLE_FACTOR
        dictW={}
        for word in words:
            if not word in dictW:
                dictW[word]=0
            dictW[word]+=1
        wTup=sorted(dictW.items(),key=lambda x: x[1], reverse=True)
        return wTup
    def getHTML(self,numKeyword=NUM_OF_KEYWORDS):
        fstr=''
        for key in self.chann:
            fstr+='<p onclick=changePos(%.2f) style="display:inline">%s</p>'%(float(key[0]),key[1]+' ')
        
        wTup=self.getFreq()
        maxN=wTup[0][1]
        if maxN-1>TITLE_FACTOR:
            maxN-=1
        keyStr=''
        for words in wTup:
            if numKeyword!=0:
                keyStr+=words[0]+'; '
                numKeyword-=1
            elif words[1]>=maxN:
                keyStr+=words[0]+'; '
            else:
                break
          
        return """
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
</head>

<style>
</style>
<body>
<h1>Welcome to the storyteller project.</h1><br>
<h3>%s</h3>
<audio id="audio" controls>
<source src="../%s" type="audio/wav">
Your browser does not support the audio element.
</audio><br><br>
<h3 style="display:inline">Subtitle:</h3>
<p id="lyric" style="display:inline;color:blue;font-size:160%%">Welcome to the storyteller project.</p>
<h4>Keywords:</h4>
<p>           %s</p>
<h3>Whole paragraph:</h3>
%s
<script src="%s"></script>
</body>
</html>
"""%(self.filename,self.filename,self.name,keyStr,fstr,self.name+'.js')

    def getJs(self):
        tStart=[]
        words=[]
        tGroup=0
        jstr=''
        for keys in self.chann:
            if tGroup==0:
                tGroup=self.wLong
                tStart.append(keys[0])
                words.append(jstr)
                jstr=keys[1]
            else:
                tGroup-=1
                jstr+=' '+keys[1]
        words.pop(0)
        words.append(jstr)    
        timeStr='var sArray=%s ;\n var cArray=%s'%(tStart,words)  
       
        return '''
%s
var lyric=document.getElementById("lyric");
var audio=document.getElementById("audio");
var len=sArray.length;
var startTime=0;
lyric.innerHTML = cArray[startTime];

audio.addEventListener("timeupdate", function () {
   setlyric();
    }, false);

function setlyric(){
  var timestop=audio.currentTime;
  if(sArray[startTime]<timestop&&(startTime==len-1 || timestop<sArray[startTime+1]))return;
  var start=0;
  var end=len;
  var midvalue=0;   
  while((end-start)>1){
     midvalue=Math.floor((start+end)/2);
     if(timestop<sArray[midvalue]){end=midvalue}
     else {start=midvalue}
   }
   startTime=start;
   lyric.innerHTML = cArray[startTime];
}

function changePos(time){
  audio.currentTime=time
  audio.play()
}
'''%timeStr