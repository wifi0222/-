import socket
import time
import random

server_ip = "0.0.0.0"
server_port = 12345

# 创建UDP套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 绑定IP和端口
server_socket.bind((server_ip, server_port))

print("UDP服务器已启动，等待客户端连接...")

# 三路握手过程
syn_packet, client_address = server_socket.recvfrom(1024)
if syn_packet == b'SYN':
    print("收到SYN，发送SYN-ACK")
    syn_ack_packet = b'SYN-ACK'
    server_socket.sendto(syn_ack_packet, client_address)

    ack_packet, client_address = server_socket.recvfrom(1024)
    if ack_packet == b'ACK':
        print("收到ACK，握手成功")
    else:
        print("握手失败")
        server_socket.close()
        exit(1)
else:
    print("无效的握手请求")
    server_socket.close()
    exit(1)

# 数据传输阶段
while True:
    # 接收客户端消息
    client_message, client_address = server_socket.recvfrom(2048)

    # 解析消息
    if client_message == b'FIN':
        # 客户端请求断开连接
        break

    seq_no = int.from_bytes(client_message[:2], byteorder='big', signed=False)
    ver = client_message[2]

    if ver == 2:
        # 模拟丢包
        if random.random() > 0.3:  # 70%的概率响应
            # 构造响应数据
            response = seq_no.to_bytes(2, byteorder='big', signed=False) + ver.to_bytes(1, byteorder='big')
            response += time.strftime("%Y-%m-%d %H-%M-%S").encode() + b' ' * (200 - len(time.strftime("%Y-%m-%d %H-%M-%S")))

            # 发送响应
            server_socket.sendto(response, client_address)
        else:
            print(f"丢包：序列号 {seq_no}")

# 挥手阶段
# 第一次挥手：服务器接收客户端的FIN并发送ACK
print("收到客户端的FIN，发送ACK")
ack_packet = b'ACK'
server_socket.sendto(ack_packet, client_address)

# 第二次挥手：服务器发送FIN
print("发送FIN，等待客户端的ACK")
fin_packet = b'FIN'
server_socket.sendto(fin_packet, client_address)

# 等待客户端的ACK
try:
    ack_packet, client_address = server_socket.recvfrom(1024)
    if ack_packet == b'ACK':
        print("收到客户端的ACK，挥手成功，可以关闭连接")
    else:
        print("挥手失败")
except socket.timeout:
    print("挥手超时")

# 关闭套接字
server_socket.close()
