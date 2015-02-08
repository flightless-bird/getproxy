#!/bin/python
#coding=utf-8

import urllib2
import re
import random
import gzip
import StringIO
import threading
import Queue
import time


pageNum = 5
threadNum = 2
ipre = re.compile(r'<script>i0="(.*?)";')
portre = re.compile(r'<script>var p1=(\d{1,}/\d{1,});')
#lock = threading.Lock()
workQueue = Queue.Queue(10)
chkQueue = Queue.Queue(300)
ipDict = {}

class getProxyInfo(threading.Thread):
    def __init__(self,url):
        threading.Thread.__init__(self)
        self.url=url

    def run(self):
		while True:
			if self.url.empty():
				break
			urlDot = self.url.get()
			print '%s now processing the url: %s' % (threading.current_thread().name,urlDot)
			# ipDict = findIp(getWeb(urlDot))
			findIp(getWeb(urlDot))
			time.sleep(1)
			self.url.task_done()



class checkProxyInfo(threading.Thread):
    def __init__(self,addr):
        threading.Thread.__init__(self)
        self.addr=addr

    def run(self):
        while True:
            if self.addr.empty():
                break
            checkAddr = self.addr.get()
            print '%s now processing the: %s' % (threading.current_thread().name,checkAddr)
            chkProxy(checkAddr)
            self.addr.task_done()



def getWeb(urlLink):
	my_head = {
			"GET":urlLink,
			"Accept-encoding":"gzip",
			"Host":"www.haodailiip.com",
			"Referer":"http://www.haodailiip.com/"
			}
	
	######################User-Agent random
	randHead = [
			"Mozilla/5.0 (x11; Ubuntu; Linux i686; rv:10.0 Gecko/20100101 Firefox/10.0",
			"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
			"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
			"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)"
	]
	
	####随机User-Agent
	random_header = random.choice(randHead)
	
	#####################本地连接代理
	# proxy_set = urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
	# opener = urllib2.build_opener(proxy_set)
	# urllib2.install_opener(opener)
	
	
	req = urllib2.Request(urlLink,headers=my_head)
	req.add_header("User-Agent",random_header)
	
	
	#print req.headers.items()
	
	
	
	html = urllib2.urlopen(req)
	isGzip = html.headers.get('Content-Encoding')
	#print isGzip
	
	
	##############gzip的解压
	if isGzip:
		compressedDate = html.read()
		compressedStream = StringIO.StringIO(compressedDate)
		gzipper = gzip.GzipFile(fileobj=compressedStream)
		data = gzipper.read()
	else :
		data = html.read()
	
	#print data
	return data
def findIp(data):
	iplist = re.findall(ipre,data)
	portlist = re.findall(portre,data)
	
	#################把接受到的字符计算更新
	for i in range(len(portlist)):
		sport = portlist[i]
		spstr = sport.split('/')
	#    sToInt = int(spstr[0])/int(spstr[1])
	#    portlist[i] = '%s' % sToInt
		portlist[i] =str(int(spstr[0])/int(spstr[1]))
	
	##################
	
	####################处理ip字符
	ipch = {
			"k":"2",
			"f":"1",
			"j":"5"
			}
	for i in range(len(iplist)):
		for p in ipch.keys():
			iplist[i] = re.sub(p,ipch[p],iplist[i])
	
	
	
	#######################
    # try: 
		# lock.acquire()
		# ipport = dict(zip(iplist,portlist))
		# return ipport
    # finally:
		# lock.release()

	ipport = dict(zip(iplist,portlist))
	ipDict.update(ipport)
		# return ipport


def chkProxy(Addr):
    chProxySet = urllib2.ProxyHandler({'http':'http://%s' % Addr})
    opener = urllib2.build_opener(chProxySet,urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    r = urllib2.Request('http://www.haosou.com')
    r.add_header("Accept-Language","utf-8")
    r.add_header("User-Agent","Mozilla/5.0 (Windows NT 5.1; rv:35.0) Gecko/20100101 Firefox/35.0")
    r.add_header("Content-Type","text/html; charset=utf-8")
        
    trycount=1
    while trycount <= 2:
        try:
            T0=time.time()
            f=opener.open(r)
            da = f.read()
            if 'haosou' in da:
                T=time.time() - T0
                print 'the %s is useable use time is %s' % (Addr,str(T))
                break
            else:
                del ipDict[chAddr]
        except:
            time.sleep(1)
            trycount = trycount + 1
    if trycount > 2:
        del ipDict[chAddr]









#    	htm = urllib2.urlopen(r)
#        if html.getcode() is '200':
#            print 'the %s is useable' % checkProxy
#        else:
#            del ipDict[chAddr]

if __name__ == '__main__':
    print 'begin....'
    for n in range(1,pageNum+1):
        urlitem = "http://www.haodailiip.com/guonei/%s" % n
        workQueue.put(urlitem)
    for x in range(threadNum):
        getProxyInfo(workQueue).start()

    workQueue.join()
    print 'All for get Thread is ended,now start checking...'
    for chAddr in ipDict.keys():
        ProxyAddr = chAddr+':'+ipDict[chAddr]
        chkQueue.put(ProxyAddr)
    for x in range(threadNum+3):
        checkProxyInfo(chkQueue).start()

    chkQueue.join()
	#print the Dict
	# for i in ipDict:
		# print i,ipDict[i]



	#write log
    logFile = open("proxy.log",'a')
    for i in ipDict:
        logFile.write(i+':'+ipDict[i]+'\r\n')	
		# 记事本中只支持\r\n进行换行..
    logFile.close()
    print 'loging is ok. \nfile is proxy.log.'











