"""
author : Nishaohsan
email : 790016602@qq.com
time : 2020-6-21
env : Python3.6
socket,select,webserver,服务器端
"""
import re
from socket import *
from select import *


class WebServer:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.create_socket()
        self.bind()
        self.mapfd = {}

    def create_socket(self):
        self.sock = socket()

    def bind(self):
        self.sock.bind((self.host, self.port))

    def start(self):
        self.sock.listen(5)
        self.sock.setblocking(False)
        ep = epoll()
        ep.register(self.sock, EPOLLIN)
        self.mapfd[self.sock.fileno()] = self.sock
        while True:
            print("开始监控")
            events = ep.poll()
            print("监控到IO：", events)
            for fd, event in events:
                if fd == self.sock.fileno():
                    connfd, addr = self.sock.accept()
                    print("connect from", addr)
                    connfd.setblocking(False)
                    ep.register(connfd, EPOLLIN)
                    self.mapfd[connfd.fileno()] = connfd
                    continue
                else:
                    self.handle(self.mapfd[fd], ep)

    def handle(self, connfd, ep):
        request = connfd.recv(1024).decode()
        print("接收到请求信息：", request)
        pattern = "[A-Z]+\s(?P<info>/\S*)"
        result = re.match(pattern, request)
        if result:
            msg = result.group("info")
            print("请求详细内容：", msg)
            self.send_html(connfd, msg)
        else:
            del self.mapfd[connfd.fileno()]
            ep.unregister(connfd)
            connfd.close()
            print("链接套接字已删除")

    def send_html(self, connfd, msg):
        if msg == "/":
            filename = "./static/index.html"
        else:
            filename = "./static" + msg
        try:
            f = open(filename, "rb")
        except:
            print("请求不存在")
            response = "HTTP/1.1 404 Not Fount\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += "sorry not find"
            response = response.encode()
        else:
            data = f.read()
            print("链接成功，已发送", filename)
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "Content-Length:%d\r\n" % len(data)
            response += "\r\n"
            response = response.encode() + data
        finally:
            connfd.send(response)
