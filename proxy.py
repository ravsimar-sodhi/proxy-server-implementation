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
    print "message:",message

    #Extract the filename from the given message
    url = message.split()[1]
    print url
    filename = url.partition("/")[2]
    print "filename:",filename
    # fileExist = "false"
    filetouse = "/" + filename
    print "filetouse:",filetouse
    
    serverSoc = socket(AF_INET, SOCK_STREAM) #Create a socket on the proxyserver
    host,port = filename.split("/")[1].split(":")
    serverSoc.connect((host,int(port)))
    try: #Check whether the file exists in the cache
        # f = open(filetouse[1:], "r")
        # f = open(filename, "r")
        val = cacheData[filename]
        # outputdata = f.readlines()
        fileExist = "true"
        ind = val.find("Last-Modified: ")
        if ind != -1:
            timestamp = val[ind+15:ind+15+29]
            tempTime = time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
            timestamp = time.strftime("%a %b  %d %H:%M:%S %Z %Y",tempTime)
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
                clientSoc.send(resp)
                response += resp
                print resp
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
            while True:
                resp = serverSoc.recv(1024)
                if not resp:
                    break
                clientSoc.send(resp)
                response += resp
                print resp
            cacheData[filename] = response                # Create a temporary file on this socket and ask port 80 for
                # the file requested by the client
                # fileobj = c.makefile('r', 0)
                # fileobj.write("GET " + "http://" + filename + "HTTP/1.0\r\n")
                # Read the response into buffer
                # buffr = fileobj.readlines()
                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the
                # corresponding file in the cache
                # tmpFile = open(filename,"wb")
                # for data in buffr:
                    # tmpFile.write(data)
                    # clientSoc.send(data)
                    # print data
        except:
            print "Illegal request"
    else: #File not found
        print "404: File Not Found"
    clientSoc.close() #Close the client and the server sockets


