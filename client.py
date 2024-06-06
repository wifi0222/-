import socket
import time
import statistics

timeout = 0.1  # 超时时间100ms
server_ip = input("请输入服务器IP: ")
server_port = int(input("请输入服务器端口: "))

# 创建UDP套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(timeout)

# 三路握手过程
syn_packet = b'SYN'
client_socket.sendto(syn_packet, (server_ip, server_port))

try:
    syn_ack_packet, server_address = client_socket.recvfrom(1024)
    if syn_ack_packet == b'SYN-ACK':
        print("收到SYN-ACK，发送ACK")
        ack_packet = b'ACK'
        client_socket.sendto(ack_packet, (server_ip, server_port))
        print("握手成功，可以开始数据传输")
    else:
        print("握手失败")
        client_socket.close()
        exit(1)
except socket.timeout:
    print("握手超时")
    client_socket.close()
    exit(1)

# 数据传输阶段
rtts = []
packets_sent = 0
packets_received = 0

for seq_no in range(1, 13):
    transmission_count = 1  # 初始化传输次数
    while transmission_count <= 3:  # 最多重传两次
        packets_sent += 1
        # 构造请求数据
        request = seq_no.to_bytes(2, byteorder='big', signed=False) + int(2).to_bytes(1, byteorder='big')
        request += b'WANGFEI' + transmission_count.to_bytes(1, byteorder='big')  # 添加传输次数
        request += b'A' * (200 - len(b'WANGFEI') - 1)  # 填充内容

        send_time = time.time()

        try:
            # 发送请求
            client_socket.sendto(request, (server_ip, server_port))

            # 接收响应
            response, server_address = client_socket.recvfrom(2048)

            # 计算RTT
            rtt = (time.time() - send_time) * 1000  # 换算为毫秒
            rtts.append(rtt)

            packets_received += 1
            print(f"序列号 {seq_no}, 传输次数 {transmission_count}, 服务器IP:Port {server_address}, RTT {rtt:.2f}ms")
            break  # 成功接收到响应，跳出重传循环
        except socket.timeout:
            print(f"序列号 {seq_no}, 传输次数 {transmission_count}, 请求超时，重传")
            transmission_count += 1
            if transmission_count > 3:
                print(f"序列号 {seq_no}, 重传失败，放弃本次重传")
                break  # 重传两次后仍未收到响应，放弃重传

# 打印汇总信息
print("\n【汇总】")
print(f"发送的UDP包数目：{packets_sent}")
print(f"接收到的UDP包数目：{packets_received}")
print(f"丢包率：{((packets_sent - packets_received) / packets_sent) * 100:.2f}%")
if rtts:
    print(
        f"最大RTT：{max(rtts):.2f}ms，最小RTT：{min(rtts):.2f}ms，平均RTT：{sum(rtts) / len(rtts):.2f}ms，RTT标准差：{statistics.stdev(rtts):.2f}ms")

# 第一次挥手：客户端发送FIN
fin_packet = b'FIN'
client_socket.sendto(fin_packet, (server_ip, server_port))

# 等待服务器的ACK
try:
    ack_packet, server_address = client_socket.recvfrom(1024)
    if ack_packet == b'ACK':
        print("收到服务器的ACK，挥手成功")
    else:
        print("挥手失败")
except socket.timeout:
    print("挥手超时")

# 第二次挥手：客户端等待服务器的FIN
try:
    fin_packet, server_address = client_socket.recvfrom(1024)
    if fin_packet == b'FIN':
        print("收到服务器的FIN，发送ACK")
        ack_packet = b'ACK'
        client_socket.sendto(ack_packet, server_address)
        print("挥手成功，可以关闭连接")
    else:
        print("挥手失败")
except socket.timeout:
    print("挥手超时")

# 关闭套接字
client_socket.close()
