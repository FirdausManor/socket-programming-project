import socket
 
HOST = 'localhost'
PORT = 8080
 
# สร้าง socket object
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# client ทำการเชื่อมต่อไปยัง server
socket.connect((HOST, PORT))
 
# 3 ส่งข้อมูลไปหา server
socket.sendall(b'6309651005:1111')
 
# รับข้อมูลที่ส่งมาจาก server
data = socket.recv(1024)
print(data.decode('utf-8'))

# decode data ที่ได้กลับมาจาก server
token_msg = data.decode('utf-8')
token_back = token_msg[6:]

# 7.2 ส่งข้อมูลไปหา server อีกครั้ง โดย message = request secret number
socket.sendall(token_back.encode('utf-8') + b':request secret number:5:221')
data = socket.recv(1024)
print(data.decode('utf-8'))

# 7.3 ส่งข้อมูลไปหา server อีกครั้ง โดย message = check secret number
socket.sendall(token_back.encode('utf-8') + b':check secret number:35')
data = socket.recv(1024)
print(data.decode('utf-8'))

# 7.4 ส่งข้อมูลไปหา server อีกครั้ง โดย message = quit
socket.sendall(token_back.encode('utf-8') + b':quit')
data = socket.recv(1024)
print(data.decode('utf-8'))

socket.close()