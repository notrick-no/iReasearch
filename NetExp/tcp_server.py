# tcp_server.py
import socket
import threading

def handle_client(conn, addr):
    print(f"[SERVER] 连接来自 {addr}")
    conn.send("请输入用户名: ".encode())
    username = conn.recv(1024).decode().strip()
    conn.send("请输入密码: ".encode())
    password = conn.recv(1024).decode().strip()

    # 简单验证（用户名=abc，密码=123）
    if username == "abc" and password == "123":
        conn.send("登录成功！请输入要发送的文本: ".encode())
        text = conn.recv(1024).decode()
        print(f"[SERVER] 收到文本: {text}")
        conn.send(f"[服务器回显] {text}".encode())
    else:
        conn.send("登录失败！".encode())

    conn.close()
    print(f"[SERVER] 连接 {addr} 已关闭")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 6789))  # 监听所有接口，端口6789
    server.listen(5)
    print("[SERVER] TCP 服务器启动，监听端口 6789...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()