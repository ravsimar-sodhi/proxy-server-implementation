from socket import *
import os

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
    print message.split()[1]
    filename = message.split()[1].partition("/")[2]
    print "filename:",filename
    fileExist = "false"
    filetouse = "/" + filename
    print "filetouse:",filetouse

    try: #Check whether the file exists in the cache
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = "true"
        #ProxyServer finds a cache hit and generates a response message
        clientSoc.send("HTTP/1.0 200 OK\r\n")
        clientSoc.send("Content-Type:text/html\r\n")
        for data in outputdata:
            clientSoc.send(data)
        print 'Read from cache'
    except IOError: #Error handling for file not found in cache
        if fileExist == "false":

            serverSoc = socket(AF_INET, SOCK_STREAM) #Create a socket on the proxyserver
            # hostn = filename.replace("127.0.0.1","",1)
            hostn = "127.0.0.1" 
            print "hostn:",hostn
            try:
                serverSoc.connect((hostn, 20000)) #https://docs.python.org/2/library/socket.html
                message = message.replace("http://127.0.0.1:20000","")
                serverSoc.send(message)
                # c.send("GET " + "/" + filename + " HTTP/1.1\r\n")
                while True:
                    resp = serverSoc.recv(1024)
                    if not resp:
                        break
                    clientSoc.send(resp)
                    print resp
                # Create a temporary file on this socket and ask port 80 for
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


