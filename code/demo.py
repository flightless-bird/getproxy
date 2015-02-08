﻿# -*- coding: utf-8 -*-
import urllib2,re,thread,time
import socket
socket.setdefaulttimeout(10)
#------------------从网上抓取IP地址------------------#
def getcnproxy(name):
    pagenum=0 #页码初始0
    result=[] #结果集
    trycount=0 #失败尝试次数
    while trycount<=3 and pagenum<1: #失败3次就停止抓取并且只抓1页
        pagenum=pagenum+1
        url='http://www.proxycn.com/html_proxy/http-'+str(pagenum)+'.html'
        #http://www.proxycn.com/html_proxy/http-1.html'
        try:
            html=urllib2.urlopen(url) #打开链接
            ip=''
            for line in html:
                if '''onDblClick="clip''' in line: #页面中IP地址这行包含onDblClick="clip，所以当判定到它存在即往下提取出IP地址
                    proxy=line[line.find("clip('")+6:line.find("')")] #clip('和')是网页中IP地址的前后html代码
                    lock.acquire()
                    print(name,'-',proxy)
                    lock.release()
                    result.append(proxy) #将结果放入result[]
        except:
            trycount=trycount+1
            pagenum=pagenum-1
    proxylist[0]=result #proxylist是函数外的一个变量
    return result
 
def getproxycn(name):
    pagenum=0
    result=[]
    getallpages=0
    trycount=0
    while pagenum<=9 and trycount<=2 and pagenum<1:
        pagenum=pagenum+1
        url='http://www.cnproxy.com/proxy'+str(pagenum)+'.html'
        try:
            html=urllib2.urlopen(url)
            for line in html:
                if "HTTP" in line:
                    proxy=line[line.find('<td>')+6:line.find('<SCRIPT type')]
                    lock.acquire()
                    print(name,'-',proxy)
                    lock.release()
                    result.append(proxy)
        except:
            trycount=trycount+1
            pagenum=pagenum-1
    proxylist[1]=result
    return result
#--------------------------------------------------#
#------------------代理验证------------------#
def proxycheckone(proxy):
    url='http://www.google.com/'
    proxy_url = 'http://'+proxy
    proxy_support = urllib2.ProxyHandler({'http': proxy_url}) #设定使用proxy
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    r=urllib2.Request(url)
    r.add_header("Accept-Language","utf-8") #加入头信息,这样可避免403错误
    r.add_header("Content-Type","text/html; charset=utf-8")
    r.add_header("User-Agent","Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)")
    trycount=1
    while trycount<=2: #尝试2次
        try:
            T0=time.time() #开始时间
            f=opener.open(r)
            data=f.read()
            if 'Google' in data: #判断到网页信息中有Google字符,说明通过此proxy连接google可以成功
                T=time.time()-T0 #得出最终连接所用时间
                break
            else:return []
        except:
            time.sleep(1)
            trycount=trycount+1
    if trycount>2:
        return []
    else:
        return '地址:'+proxy+' 连接速度:'+str(T) #此信息会写入一个文本文件
 
def proxycheck(idnum):
    while 1:
        r.acquire()
        try:
            i=proxylist[0]
            del proxylist[0]
            r.release()
        except:
            r.release()
            x[idnum]=1
            break
        b=proxycheckone(i)
        if len(b)>0:
            a.acquire()
            y.append(b) #写入可用代理IP
            a.release()
#-------------------------------------------#
if __name__ == '__main__':
    #------------------将得到的代理IP地址写入文件------------------#
    lock=thread.allocate_lock()
    proxylist=[[],[]] #用于存放下面两函数运行时返回的结果
    thread.start_new(getcnproxy,('cnproxy',)) #开线程运行getcnproxy函数,参数值cnproxy
    thread.start_new(getproxycn,('proxycn',)) #开线程运行getproxycn函数,参数值proxycn
    while [] in proxylist:
        time.sleep(1)
    proxylist=proxylist[0]+proxylist[1]
    w=open('proxies.txt','a') #新建文件
    w.write('\n'.join(proxylist)) #写入抓取到的IP
    w.close()
    del proxylist #清掉数组
    print('get all proxies!\n\n')
    #-----------------------------------------------------------#
    #------------------从文件中取出代理IP并验证------------------#
    w=open('proxies.txt') #打开文件
    proxylist=list(set((re.sub(r'(\t+[^\n]*\n|\n)',',',w.read())).split(','))) #通过正则来得到IP
    while '' in proxylist:
        del proxylist[proxylist.index('')]
    w.close()
 
    lock=thread.allocate_lock()
    r=thread.allocate_lock()
    a=thread.allocate_lock()
    y=[]
    x=[0]*120
 
    for idnum in range(0,100):
        thread.start_new(proxycheck,(idnum,))#线程运行proxycheck函数,参数值idnum 0-100
 
    while 0 in x:
        print("Remain:",len(proxylist)," Finish:",sum(x)," Check OK:",len(y))
        time.sleep(10)
 
    w=open('proxies.txt','w')
    w.write(re.sub('^\n','',re.sub(r'\n+','\n','\n'.join(y)+'\n')))
    w.close()
    #---------------------------------------------------------#
