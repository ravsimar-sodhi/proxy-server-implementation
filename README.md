
HTTP Proxy Server
==============================
Assignment 2 of Computer Networks

Karandeep Singh Juneja-20161119
Ravsimar Singh Sodhi-20161117

Starting Servers
--------------------------
```
python proxy.py
cd server/
python sever.py
```

Curl Requests
--------------------------
```
curl -x http://localhost:12345 http://127.0.0.1:20000/<filename>
```

Libraries Used
--------------------------
- os
- socket
- time
- thread

Features Implemented
--------------------------
- Only handles HTTP GET requests
- Caching using the "If Modified Since" header
- Caching depends on Cache-Control header
- Cached data stored in python dictionary
- Cache Size: 3
- Bonus: Non blocking server
