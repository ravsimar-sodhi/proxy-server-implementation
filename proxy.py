from socket import *
import os
import time

def recvResponse(soc):
    response = ""
    while True:
        resp = soc.recv(1024)
        if not resp:
            break
        response += resp
    return response
        
def parseRequest(request):
    url = request.split()[1] # This gives the whole url e.g :http://host:port/filename
    try:
        filename = url.partition("/")[2] # e.g host:port/filename
    # if url is of the form http://host:port , the above will give an index out of bound error
    except:
        filename = url[6:] # host:port
    return filename

def getIMSHeader(ind,val):
    timestamp = val[ind+15:ind+15+29] # Get the cache Last-Modified header to check validity of cache
    tempTime = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z") # Convert to struct_time object
    tempTime = time.localtime(time.mktime(tempTime) + 3600*5.5) # Convert from GMT Time to local time by adding 5:30 hours
    timestamp = time.strftime("%a %b %d %H:%M:%S %Y",tempTime) # Convert to string
    return "If-Modified-Since: " + timestamp # Final header

def addHeader(request, header):
    splitMess = request.split('\n')
    splitMess.insert(3,header)
    modMessage = '\n'.join(splitMess)
    return modMessage
    
cacheData = {}
cacheSize = 0
soc = socket(AF_INET, SOCK_STREAM) 
soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
soc.bind(("", 12345))
soc.listen(5) 
while True:
    print '[Proxy Server]: Listening for client requests ...'
    clientSoc, addr = soc.accept()
    print '[Proxy Server]: Received connection from client at: ', addr
    # message = recvResponse(clientSoc)
    request = clientSoc.recv(1024)
    print request
    # parsing request for filename
    filename = parseRequest(request)
    # Make socket for connection to the final server
    serverSoc = socket(AF_INET, SOCK_STREAM) 
    host,port = filename.split("/")[1].split(":")
    print "[Proxy Server]: Connecting to ",host," at port ",port
    try:
        serverSoc.connect((host,int(port)))
    except:
        print "[Proxy Server]: Error with connection to server"
    try:
        val = cacheData[filename]
        ind = val.find("Last-Modified: ")
        if ind != -1:
            IMSheader = getIMSHeader(ind,val)   
            modMessage = addHeader(request,IMSheader)
            modMessage = modMessage.replace("http://" + host + ":" + port,"")
            serverSoc.send(modMessage)
            response = recvResponse(serverSoc)
            print "Server Response:\n",response
            if response.find("HTTP/1.0 304 Not Modified") != -1:
                clientSoc.send(cacheData[filename])
                print "[Proxy Sever]: Cached data sent!"
            else:
                print "[Proxy Server]: Updating Cached data!"
                cacheData[filename] = response
                clientSoc.send(response)
    except KeyError:
        try:
            request = request.replace("http://" + host + ":" + port,"")
            serverSoc.send(request)
            response = recvResponse(serverSoc)
            print "Server Response:\n",response
            clientSoc.send(response)
            if response.find("Cache-control: no-cache") > 0:
                print "[Proxy Server]: Data not cached!"
            else:
                print "[Proxy Server]: Caching data!"
                if  cacheSize == 3:
                    cacheData.popitem()
                    cacheSize = cacheSize - 1
                cacheData[filename] = response
                cacheSize = cacheSize + 1
                
        except:
            print "[Proxy Server]: Error handling request"
    clientSoc.close() 


