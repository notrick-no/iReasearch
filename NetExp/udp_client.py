# udp_client.py
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
msg = input("请输入要发送的文本: ")
client.sendto(msg.encode(), ('127.0.0.1', 9876))
data, _ = client.recvfrom(1024)
print("服务器回复:", data.decode())