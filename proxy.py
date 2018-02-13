from socket import *
import os
import time

cacheData = {}
#Create a server socket, bind it to a port and start listening
soc = socket(AF_INET, SOCK_STREAM) #Initializing socket
soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
soc.bind(("", 12345)) #Binding socket to port
soc.listen(5) #Listening for page requests
while True:
    #Start receiving data from the client
    print 'Listening ...'
    clientSoc, addr = soc.accept()
    print 'Received connection from: ', addr
    message = clientSoc.recv(1024)
    # print "message:",message

    #Extract the filename from the given message
    url = message.split()[1]
    print url
    filename = url.partition("/")[2]
    # print "filename:",filename
    # fileExist = "false"
    filetouse = "/" + filename
    # print "filetouse:",filetouse
    
    serverSoc = socket(AF_INET, SOCK_STREAM) #Create a socket on the proxyserver
    host,port = filename.split("/")[1].split(":")
    serverSoc.connect((host,int(port)))
    try: #Check whether the file exists in the cache
        # f = open(filetouse[1:], "r")
        # f = open(filename, "r")
        val = cacheData[filename]
        # outputdata = f.readlines()
        ind = val.find("Last-Modified: ")
        if ind != -1:
            timestamp = val[ind+15:ind+15+29]
            tempTime = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
            tempTime = time.localtime(time.mktime(tempTime) + 3600*5.5)
            timestamp = time.strftime("%a %b %d %H:%M:%S %Y",tempTime)
            IMSheader = "If-Modified-Since: " + timestamp
            splitMess = message.split('\n')
            splitMess.insert(3,IMSheader)
            modMessage = '\n'.join(splitMess)
            modMessage = modMessage.replace("http://127.0.0.1:20000","")
            serverSoc.send(modMessage)
            response = ""
            while True:
                resp = serverSoc.recv(1024)
                if not resp:
                    break
                response += resp
                print resp
            print "ethe"
            if response.find("HTTP/1.0 304 Not Modified") != -1:
                cData = cacheData[filename]
                clientSoc.send(cData)
                print "Cached data sent"
            else:
                print "Caching data"
                cacheData[filename] = response
                clientSoc.send(response)
        #ProxyServer finds a cache hit and generates a response message
        # clientSoc.send("HTTP/1.0 200 OK\r\n")
        # clientSoc.send("Content-Type:text/html\r\n")
        # for data in outputdata:
        #     clientSoc.send(data)
        # print 'Read from cache'
    except KeyError: #Error handling for file not found in cache
        try:
            message = message.replace("http://127.0.0.1:20000","")
            serverSoc.send(message)
            # c.send("GET " + "/" + filename + " HTTP/1.1\r\n")
            response = ""
            print "ehte vi"
            while True:
                resp = serverSoc.recv(1024)
                if not resp:
                    break
                clientSoc.send(resp)
                response += resp
            print response
            if response.find("Cache-control: no-cache") > 0:
                print "file not cached"
            else:
                cacheData[filename] = response
        except:
            print "Illegal request"
    clientSoc.close() #Close the client and the server sockets


