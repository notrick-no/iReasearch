# tcp_client.py
import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 6789))  # 连接本机服务器

    while True:
        msg = client.recv(1024).decode()
        print(msg, end='')
        if "用户名" in msg:
            user = input()
            client.send(user.encode())
        elif "密码" in msg:
            pwd = input()
            client.send(pwd.encode())
        elif "文本" in msg:
            text = input()
            client.send(text.encode())
        else:
            print(client.recv(1024).decode())
            break

    client.close()

if __name__ == "__main__":
    main()