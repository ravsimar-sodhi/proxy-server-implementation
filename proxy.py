from socket import *
import os
import time
import thread
class Proxy():
    cacheData = {}
    cacheSize = 0
    def recvResponse(self, soc):
        response = ""
        while True:
            resp = soc.recv(1024)
            if not resp:
                break
            response += resp
        return response
            
    def parseRequest(self, request):
        url = request.split()[1] # This gives the whole url e.g :http://host:port/filename
        try:
            filename = url.partition("/")[2] # e.g host:port/filename
        # if url is of the form http://host:port , the above will give an index out of bound error
        except:
            filename = url[6:] # host:port
        return filename

    def getIMSHeader(self, ind,val):
        timestamp = val[ind+15:ind+15+29] # Get the cache Last-Modified header to check validity of cache
        tempTime = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z") # Convert to struct_time object
        tempTime = time.localtime(time.mktime(tempTime) + 3600*5.5) # Convert from GMT Time to local time by adding 5:30 hours
        timestamp = time.strftime("%a %b %d %H:%M:%S %Y",tempTime) # Convert to string
        return "If-Modified-Since: " + timestamp # Final header

    def addHeader(self, request, header):
        splitMess = request.split('\n')
        splitMess.insert(3,header)
        modMessage = '\n'.join(splitMess)
        return modMessage
        

    def serveClient(self,addr,clientSoc):
        print '[Proxy Server]: Received connection from client at: ', addr
        request = clientSoc.recv(1024)
        # print request
        # parsing request for filename
        filename = self.parseRequest(request)
        # Make socket for connection to the final server
        serverSoc = socket(AF_INET, SOCK_STREAM) 
        host,port = filename.split("/")[1].split(":")
        print "[Proxy Server]: Connecting to ",host," at port ",port
        try:
            serverSoc.connect((host,int(port)))
        except:
            print "[Proxy Server]: Error with connection to server"
        try:
            val = Proxy.cacheData[filename]
            ind = val.find("Last-Modified: ")
            if ind != -1:
                IMSheader = self.getIMSHeader(ind,val)   
                modMessage = self.addHeader(request,IMSheader)
                modMessage = modMessage.replace("http://" + host + ":" + port,"")
                serverSoc.send(modMessage)
                response = self.recvResponse(serverSoc)
                # print "Server Response:\n",response
                if response.find("HTTP/1.0 304 Not Modified") != -1:
                    clientSoc.send(Proxy.cacheData[filename])
                    print "[Proxy Sever]: Cached data sent!"
                else:
                    print "[Proxy Server]: Updating Cached data!"
                    Proxy.cacheData[filename] = response
                    clientSoc.send(response)
        except KeyError:
            try:
                request = request.replace("http://" + host + ":" + port,"")
                serverSoc.send(request)
                response = self.recvResponse(serverSoc)
                # print "Server Response:\n",response
                clientSoc.send(response)
                if response.find("Cache-control: no-cache") > 0:
                    print "[Proxy Server]: Data not cached!"
                elif response.find("HTTP/1.0 200 OK") >= 0:
                    print "[Proxy Server]: Caching data!"
                    if  Proxy.cacheSize == 3:
                        Proxy.cacheData.popitem()
                        Proxy.cacheSize = Proxy.cacheSize - 1
                    Proxy.cacheData[filename] = response
                    Proxy.cacheSize = Proxy.cacheSize + 1
                    
            except:
                print "[Proxy Server]: Error handling request"
        clientSoc.close() 

soc = socket(AF_INET, SOCK_STREAM) 
soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
soc.bind(("", 12345))
soc.listen(5) 
p = Proxy()
while True:
    print '[Proxy Server]: Listening for client requests ...'
    clientSoc, addr = soc.accept()
    thread.start_new_thread(p.serveClient,(addr,clientSoc))