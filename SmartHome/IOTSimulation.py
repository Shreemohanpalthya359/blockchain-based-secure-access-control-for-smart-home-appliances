import tkinter
from tkinter import *
import math
import random
from threading import Thread 
from collections import defaultdict
from tkinter import ttk
import numpy as np
import random
import pyaes, pbkdf2, binascii, os, secrets
import json
from web3 import Web3, HTTPProvider
import time
import socket 
from threading import Thread 
from socketserver import ThreadingMixIn
import json
import hashlib
import base64

global mobile, labels, mobile_x, mobile_y
global text
global canvas
global p1,p2,p3
global line1,line2,line3
option = 0
global root
global commandList, userList

#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:9545'
    try:
        web3 = Web3(HTTPProvider(blockchain_address))
        # Get the first account from ganache/truffle
        accounts = web3.eth.accounts
        if not accounts:
            print("WARNING: No blockchain accounts found. Make sure Truffle Develop is running on port 9545!")
            return None
        default_account = accounts[0] if accounts else None
        web3.eth.default_account = default_account
        compiled_contract_path = 'SmartHome.json' #SmartHome contract file
        deployed_contract_address = '0xA8A0603d86E2cf15B7988d44B7685f6009Dc81D0' #contract address
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        file.close()
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        # Test if contract is accessible
        try:
            contract.functions.getCommandCount().call()
        except Exception as ce:
            print("WARNING: Contract not accessible at address", deployed_contract_address, "-", str(ce))
            print("Please run 'migrate' in Truffle Develop to deploy the contract!")
            return None
        print("Blockchain contract connected successfully!")
        return contract
    except Exception as e:
        print("WARNING: Could not connect to blockchain:", str(e))
        return None

contract = getContract()
if contract is None:
    print("\n=== BLOCKCHAIN WARNING ===")
    print("Blockchain not connected. The GUI will still launch.")
    print("To connect blockchain:")
    print("  1. Start Truffle Develop: cd hello-eth && npx truffle develop")
    print("  2. In Truffle console, run: migrate")
    print("  3. Restart this simulation")
    print("==========================\n")

def getCommandList():
    global commandList, contract
    commandList = []
    if contract is None:
        return
    try:
        count = contract.functions.getCommandCount().call()
        for i in range(0, count):
            user = contract.functions.getUserid(i).call()
            sensor = contract.functions.getSensor(i).call()
            value = contract.functions.getCommandValue(i).call()
            dd = contract.functions.getCommandDate(i).call()
            commandList.append([user, sensor, value, dd])
    except Exception as e:
        print("ERROR loading commands:", str(e))

def getUserList():
    global userList, contract
    userList = []
    if contract is None:
        return
    try:
        count = contract.functions.getUserCount().call()
        for i in range(0, count):
            name = contract.functions.getUsername(i).call()
            password = contract.functions.getPassword(i).call()
            phone = contract.functions.getPhone(i).call()
            email = contract.functions.getEmail(i).call()
            address = contract.functions.getAddress(i).call()
            userList.append([name, password, phone, email, address])
    except Exception as e:
        print("ERROR loading users:", str(e))

getCommandList()
getUserList()

def autheticateUser(uid):
    global userList
    # If no blockchain connection, userList is empty — allow all users in simulation mode
    if len(userList) == 0:
        print("No blockchain userList — allowing user in simulation mode:", uid)
        return 1
    flag = 0
    for i in range(len(userList)):
        user = userList[i]
        if uid == user[0]:
            flag = 1
            break
    return flag    

def encryptAES(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR("abcd5643abcd5643abcd5643abcd5643".encode(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decryptAES(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR("abcd5643abcd5643abcd5643abcd5643".encode(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted

def getDistance(iot_x,iot_y,x1,y1):
    flag = False
    for i in range(len(iot_x)):
        dist = math.sqrt((iot_x[i] - x1)**2 + (iot_y[i] - y1)**2)
        if dist < 80:
            flag = True
            break
    return flag

def generateNetwork():
    global mobile
    global labels
    global mobile_x
    global mobile_y
    global source_list, dest_list
    mobile = []
    mobile_x = []
    mobile_y = []
    labels = []
    canvas.update()

    x = 5
    y = 350
    mobile_x.append(x)
    mobile_y.append(y)
    name = canvas.create_oval(x,y,x+40,y+40, fill="blue")
    lbl = canvas.create_text(x+20,y-10,fill="darkblue",font="Times 7 italic bold",text="SN")
    labels.append(lbl)
    mobile.append(name)
    for i in range(1,21):
        run = True
        while run == True:
            x = random.randint(100, 450)
            y = random.randint(50, 600)
            flag = getDistance(mobile_x,mobile_y,x,y)
            if flag == False:
                mobile_x.append(x)
                mobile_y.append(y)
                run = False
                name = canvas.create_oval(x,y,x+40,y+40, fill="red")
                lbl = canvas.create_text(x+20,y-10,fill="darkblue",font="Times 8 italic bold",text="SEN"+str(i))
                labels.append(lbl)
                mobile.append(name)
    startServer()
    
def highlightSensor(sensor_idx, original_color="red"):
    """Flash the target sensor green to show it received the command."""
    if sensor_idx >= len(mobile):
        return
    oval_id = mobile[sensor_idx]
    def flash(n=0):
        if n >= 6:
            canvas.itemconfig(oval_id, fill=original_color)
            return
        color = "green" if n % 2 == 0 else original_color
        canvas.itemconfig(oval_id, fill=color)
        root.after(400, lambda: flash(n+1))
    flash()

def startDataTransferSimulation(line1, line2, x1, y1, x2, y2, x3, y3):
    """Animate data transfer: blink lines from source→hop→SN."""
    drawn = [line1, line2]
    def animate(n=0):
        if n >= 6:
            # Leave lines permanently drawn instead of deleting them
            canvas.itemconfig(drawn[0], fill="blue")
            canvas.itemconfig(drawn[1], fill="blue")
            return
        color = "blue" if n % 2 == 0 else "green"
        for lid in drawn:
            try:
                canvas.delete(lid)
            except:
                pass
        new_l1 = canvas.create_line(x1, y1, x2, y2, fill=color, width=4)
        new_l2 = canvas.create_line(x2, y2, x3, y3, fill=color, width=4)
        drawn[0] = new_l1
        drawn[1] = new_l2
        root.after(500, lambda: animate(n+1))
    animate()

def sendRequest(source):
    """Draw animated connection from SN blue node → hop → target sensor.
    Always runs in the main Tkinter thread (called via root.after)."""
    global mobile_x, mobile_y
    if not mobile_x or source >= len(mobile_x):
        text.insert(END, "[Info] Click 'Generate Sensor Networks' to see animation.\n")
        return

    src_x = mobile_x[source] + 20  # centre of source oval
    src_y = mobile_y[source] + 20
    sn_x, sn_y = 25, 370           # centre of SN (blue) oval

    # Build neighbours: ALL nodes within 200px of the source (except itself)
    RADIUS = 250
    neighbours = []
    for i in range(1, len(mobile_x)):
        if i == source:
            continue
        dx = mobile_x[i] - mobile_x[source]
        dy = mobile_y[i] - mobile_y[source]
        if math.sqrt(dx*dx + dy*dy) < RADIUS:
            neighbours.append(i)

    # If no neighbours in radius, use all other nodes
    if not neighbours:
        neighbours = [i for i in range(1, len(mobile_x)) if i != source]

    # Pick the hop closest to SN
    hop = min(neighbours, key=lambda i: math.sqrt(
        (mobile_x[i] - 5)**2 + (mobile_y[i] - 350)**2))

    hop_x = mobile_x[hop] + 20
    hop_y = mobile_y[hop] + 20

    text.insert(END, f"Routing: SEN{source} -> SEN{hop} -> SN\n")

    # Draw initial lines (will be animated by startDataTransferSimulation)
    line1 = canvas.create_line(src_x, src_y, hop_x, hop_y, fill="blue", width=4)
    line2 = canvas.create_line(hop_x, hop_y, sn_x, sn_y, fill="blue", width=4)

    # Flash green on target sensor
    highlightSensor(source)

    # Animate the data transfer path
    startDataTransferSimulation(line1, line2, src_x, src_y, hop_x, hop_y, sn_x, sn_y)



def startApplicationServer():
    class ClientThread(Thread):  
        def __init__(self, ip, port, conn): 
            Thread.__init__(self) 
            self.ip = ip 
            self.port = port
            self.conn = conn
 
        def run(self):
            try:
                data = self.conn.recv(10000)
                data = json.loads(data.decode())
                name = str(data.get("hashcode"))
                fdata = data.get("fdata")
                enc = fdata.encode('utf-8')
                enc = base64.b64decode(enc)
                decrypted = decryptAES(enc).decode()
                print("Decrypted:", decrypted)
                arr = decrypted.split("#")
                hashcode = hashlib.sha256(decrypted.encode()).hexdigest()
                getUserList()
                print("Hash match:", hashcode == name, "| User auth:", autheticateUser(arr[0]))
                if hashcode == name and autheticateUser(arr[0]) == 1:
                    # *** Send response FIRST before any Tkinter calls ***
                    self.conn.send("Command successfully executed".encode())
                    self.conn.close()
                    # Now schedule all UI + blockchain work in main thread
                    captured = list(arr)
                    def do_work():
                        text.insert(END, "User: "+captured[0]+" authenticated\n")
                        text.insert(END, "Command: "+captured[2]+"\n")
                        if contract is not None:
                            try:
                                msg = contract.functions.createCommand(captured[0], captured[1], captured[2], hashcode+"#"+captured[3]).transact({'from': web3.eth.default_account})
                                web3.eth.wait_for_transaction_receipt(msg)
                                getCommandList()
                                text.insert(END, "Saved to blockchain\n")
                            except Exception as bc_err:
                                text.insert(END, "Blockchain warning: "+str(bc_err)+"\n")
                        try:
                            sendRequest(int(captured[1]))
                        except Exception as sr_err:
                            text.insert(END, "Animation error: "+str(sr_err)+"\n")
                    root.after(0, do_work)
                    return  # conn already closed above
                else:
                    self.conn.send("Authentication Failed".encode())
                    root.after(0, lambda: text.insert(END, "Auth failed for: "+arr[0]+"\n"))
            except Exception as e:
                print("Client thread error:", str(e))
                try:
                    self.conn.send(("Error: "+str(e)).encode())
                except:
                    pass
            finally:
                try:
                    self.conn.close()
                except:
                    pass

    try:
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        tcpServer.bind(('localhost', 2222))
        tcpServer.listen(10)  # Call listen ONCE before the loop, with backlog of 10
        threads = []
        root.after(0, lambda: text.insert(END, "Simulation Server Started on port 2222\n\n"))
        print("Socket server listening on port 2222...")
        while True:
            try:
                (conn, (ip, port)) = tcpServer.accept()
                print(f"New connection from {ip}:{port}")
                newthread = ClientThread(ip, port, conn) 
                newthread.start() 
                threads.append(newthread)
            except OSError as accept_err:
                print("Accept error (server may have been closed):", accept_err)
                break
            except Exception as loop_err:
                print("Loop error (continuing):", loop_err)
                continue
    except Exception as e:
        print("Server startup error:", str(e))
        root.after(0, lambda: text.insert(END, "Server error: "+str(e)+"\n"))

def startServer():
    print("Called")
    Thread(target=startApplicationServer).start()        
        
def Main():
    global root
    global tf1
    global text
    global canvas
    global source_list, dest_list, tf1
    root = tkinter.Tk()
    root.geometry("1300x1200")
    root.title("Smart Home Simulation Networks")
    root.resizable(True,True)
    font1 = ('times', 12, 'bold')

    canvas = Canvas(root, width = 800, height = 700)
    canvas.pack()

    l1 = Label(root, text='IOT Sensor ID:')
    l1.config(font=font1)
    l1.place(x=820,y=10)

    mid = []
    for i in range(1,20):
        mid.append(str(i))
    source_list = ttk.Combobox(root,values=mid,postcommand=lambda: source_list.configure(values=mid))
    source_list.place(x=970,y=10)
    source_list.current(0)
    source_list.config(font=font1)

    createButton = Button(root, text="Generate Sensor Networks", command=generateNetwork)
    createButton.place(x=820,y=60)
    createButton.config(font=font1)

    restartBtn = Button(root, text="Restart Server", command=startServer, bg="orange")
    restartBtn.place(x=1080,y=60)
    restartBtn.config(font=font1)

    text=Text(root,height=25,width=60)
    scroll=Scrollbar(text)
    text.configure(yscrollcommand=scroll.set)
    text.place(x=800,y=110)

    # Auto-start the socket server as soon as the GUI loads (don't wait for Generate button)
    root.after(500, startServer)
    
    
    root.mainloop()
   
 
if __name__== '__main__' :
    Main ()
    
