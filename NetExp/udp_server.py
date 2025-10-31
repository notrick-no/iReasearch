# udp_server.py
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('0.0.0.0', 9876))
print("[SERVER] UDP 服务器启动，监听端口 9876...")

while True:
    data, addr = server.recvfrom(1024)
    print(f"[SERVER] 收到来自 {addr} 的消息: {data.decode()}")
    server.sendto(f"[UDP回显] {data.decode()}".encode(), addr)