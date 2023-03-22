from itertools import count
from posixpath import split
from quopri import encodestring
import re
import socket
import csv
import base64
from turtle import st

# open and read config file
with open('server.config') as f:
        contents = f.read()
        server_port = int(contents.split("\n")[0].split(" = ")[1])
        secret_key = contents.split("\n")[1].split(" = ")[1]

print(f"server_port = {server_port}")
print(f"secret_key = {secret_key}")

HOST = 'localhost'  # IP's server
PORT = server_port  # port

# open and read csv file
def load_user_account():
    file = open("user_pass.csv")
    csvreader = csv.reader(file)
    header = next(csvreader)
    user = []
    for row in csvreader:
        user.append(row)
    return user

# เขียนฟังก์ชันตรวจสอบการยันยันตัวตนด้วย username, password
def authen_user(user_accounts, username, password):
    for user_account in user_accounts:
        if user_account[0] == username and user_account[1] == password:
            return True
    return False

user_accounts = load_user_account()
authenFailTimes = 0

# create socket object
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# กำหนดข้อมูลพื้นฐานให้กับ socket object
socket.bind((HOST, PORT))
 
# สั่งให้รอการเชื่อมต่อจาก client
socket.listen()
 
while True:
    # รอการเชื่อมต่อจาก client
    print("\n")
    print("waiting for connection...")
 
    # รับการเชื่อมต่อจาก client
    connection, client_address = socket.accept()
    try:
        print("\n")
        print("connection from", client_address)
 
        # รับข้อมูลจาก client
        while True:
            # กำหนดขนาดข้อมูลที่จะรับใน recv()
            data = connection.recv(1024)
            print("received: ", data)
            print("\n")

            if not data or data == '':
                print("Invalid Action.")
                connection.sendall(b'Connection refused !! Invalid Action.')
                connection.close()
                continue

            data = data.decode('utf-8')

            user_account = data.split(":")
            print("Username and Password:", user_account)

            # 4    
            # ตรวจสอบการยืนยันตัวตน
            if authen_user(user_accounts, user_account[0], user_account[1]):
                authenFailTimes = 0
                # ยืนยันตัวตนสำเร็จ
                print("Authen Success")

                # แปลงให้เป็น base64
                message = user_account[0] + "." + user_account[1] + "." + secret_key
                print("message = ", message)
                message_bytes = message.encode()

                base64_bytes = base64.b64encode(message_bytes)
                base64_string = base64_bytes.decode()

                print(f"Encoded string: {base64_string}")
                connection.sendall(f"token:{base64_string}".encode("ascii"))
                break

            else:
                # 5
                # ยืนยันตัวตนไม่สำเร็จ
                print("Authen Fail!!!")
                authenFailTimes += 1
                print(str(authenFailTimes) + "/3 times")
                
                if authenFailTimes < 3:
                    errorMsg = f"Invalid username or password {authenFailTimes}/3 times"
                    connection.sendall(errorMsg.encode('ascii'))
                else:
                    authenFailTimes = 0
                    print(str(authenFailTimes) + "/3 times")
                    connection.sendall(b'Connection refused!! you have exceeded maximum number of attempts')
                    connection.close()
                
                continue

        # รับข้อมูลจาก client กลับมาเป็น token:messange
        while True:
            # กำหนดขนาดข้อมูลที่จะรับใน recv()
            data = connection.recv(1024)
            print("\n")
            print("received token back:", data)

            data = data.decode('utf-8')

            user_account = data.split(":")
            message = user_account[0]

            # 7.1
            # แปลงให้เป็น username, password
            message = str(base64.b64decode(message), 'utf-8')
            print("Decoded string: ", message)
 
            user_pass = message[:15]
            user_pass = user_pass.split(".")
            print("Username and Password", user_pass)

            if authen_user(user_accounts, user_pass[0], user_pass[1]):
                authenFailTimes = 0
                # ยืนยันตัวตนสำเร็จ
                print("Authenticated : true")

                # calculate secret number
                x = [int(a) for a in str(user_pass[0])]
                print("split username:", x)

                secret_number = sum(x)
                print("calculate username:", secret_number)

                # 7.2 กรณี message = request secret number
                if user_account[1] == "request secret number":
                    e = int(user_account[2]) # 5
                    n = int(user_account[3]) # 221
                    print("7.2: " + data)    

                    # calculate Encrypted Secret Number
                    encryp_secret_num = (secret_number ** e) % n
                    print("Encrypted Secret Number:", encryp_secret_num)

                    # ส่ง Encrypted Secret Number กลับไปยัง client
                    encryp = f"Encrypted Secret Number: {encryp_secret_num}"
                    connection.sendall(encryp.encode('ascii'))
                    continue
            
                # 7.3 กรณี message = check secret number
                if user_account[1] == "check secret number":
                    print("\n")
                    print("7.3: " + data)

                    if int(user_account[2]) == secret_number:
                        connection.sendall(b'Secret Number Verification: true')
                    else:
                        connection.sendall(b'Secret Number Verification: false')

                    continue

                # 7.4 กรณี message = quit
                if user_account[1] == "quit":
                    print("\n")
                    print("7.4: " + data)
                    connection.sendall(b'Session is closed.')
                    connection.close()
                else:
                    connection.sendall(b'Connection refused !! Invalid Action.')
                    connection.close()

                    continue
            else:
                # ยืนยันตัวตนไม่สำเร็จ
                print("Authenticated : false")
                authenFailTimes += 1
                print(str(authenFailTimes) + "/3 times")
                
                if authenFailTimes < 3:
                    errorMsg = f"Invalid username or password {authenFailTimes}/3 times"
                    connection.sendall(errorMsg.encode('ascii'))
                else:
                    authenFailTimes = 0
                    print(str(authenFailTimes) + "/3 times")
                    connection.sendall(b'Connection refused!! you have provided wrong tokens 3 times in a row')
                    connection.close()
                
                continue
            break

    except OSError as msg:
        connection = None
        continue
    
    # รับข้อมูลเสร็จแล้วทำการปิดการเชื่อมต่อ
    finally:
        print("--------------")