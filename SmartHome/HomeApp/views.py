from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import json
from web3 import Web3, HTTPProvider
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import timeit
import pyaes, pbkdf2, binascii, os, secrets
import hashlib
import socket
import pickle
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

global username
global contract, web3
global commandList, userList, propose, extension
response_time = []

#encrypt file using ring signature
def encrypt(plaintext):
    aes = pyaes.AESModeOfOperationCTR("abcd5643abcd5643abcd5643abcd5643".encode(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

#decrypt file using ring signature
def decrypt(enc, key): 
    aes = pyaes.AESModeOfOperationCTR("abcd5643abcd5643abcd5643abcd5643".encode(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted

#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:9545'
    try:
        web3 = Web3(HTTPProvider(blockchain_address))
        # Get the first account from ganache/truffle
        accounts = web3.eth.accounts
        default_account = accounts[0] if accounts else None
        web3.eth.default_account = default_account
        compiled_contract_path = '../hello-eth/build/contracts/SmartHome.json' #SmartHome contract file
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
            
            # Dynamically get the contract address from the most recent network deployment
            networks = contract_json.get('networks', {})
            if networks:
                # get the highest network ID (usually the most recent deployment)
                latest_network_id = max(networks.keys())
                deployed_contract_address = networks[latest_network_id]['address']
            else:
                raise Exception("No network deployment found in SmartHome.json")

        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    except Exception as e:
        contract = None
        print("Blockchain not connected yet:", e)

getContract()

def getCommandList():
    global commandList, contract
    commandList = []
    if contract is None:
        getContract()
    try:
        count = contract.functions.getCommandCount().call()
        for i in range(0, count):
            user = contract.functions.getUserid(i).call()
            sensor = contract.functions.getSensor(i).call()
            value = contract.functions.getCommandValue(i).call()
            dd = contract.functions.getCommandDate(i).call()
            commandList.append([user, sensor, value, dd])
    except Exception as e:
        print("Could not get command list:", e)

def getUserList():
    global userList, contract
    userList = []
    if contract is None:
        getContract()
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
        print("Could not get user list:", e)
        
getCommandList()
getUserList()

def getChaKey():
    cha_key = get_random_bytes(32)
    return cha_key

def CHACHAEncrypt(plain_data, cha_cipher):
    chacha_encrypt = cha_cipher.encrypt(plain_data)
    return chacha_encrypt

def ExtensionGraph(request):
    if request.method == 'GET':
        test_msg = "testing smart home iot message".encode()
        start = timeit.default_timer()
        encrypt(test_msg)
        aes_time = timeit.default_timer() - start
        start = timeit.default_timer()
        cha_key = getChaKey()
        cha_cipher = ChaCha20.new(key=cha_key)
        cha_encrypt = CHACHAEncrypt(test_msg, cha_cipher)
        cha_time = timeit.default_timer() - start

        height = [aes_time, cha_time]
        bars = ('AES Latency','CHACHA Latency')
        y_pos = np.arange(len(bars))
        plt.figure(figsize=(6,3))
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.xlabel("Algorithm Names")
        plt.ylabel("Computation Time")
        plt.title("Propose AES & Extension CHACHA20 Computation Time Graph")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':'Propose AES & Extension CHACHA20 Computation Time Graph', 'img': img_b64}
        return render(request, 'UserScreen.html', context)

def Graph(request):
    if request.method == 'GET':
        global response_time, commandList, contract
        # Refresh commandList from blockchain
        getCommandList()
        values = np.asarray(response_time)
        index = []
        for i in range(len(values)):
            index.append(i+1)
        plt.figure(figsize=(6,3))
        if len(values) == 0:
            plt.text(0.5, 0.5, 'No commands sent yet.\nPlease Send Command first.', 
                     horizontalalignment='center', verticalalignment='center')
        else:
            plt.plot(index, values, marker='o', linestyle='-', color='b', label="Response Time")
            plt.legend()
        plt.title("Response Time Graph for each Transaction")
        plt.xlabel("Number of Request")
        plt.ylabel("Response Time (seconds)")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':'Response Time Graph for each Transaction', 'img': img_b64}
        return render(request, 'UserScreen.html', context)

def ViewHistory(request):
    if request.method == 'GET':
        global username, commandList, contract
        # Refresh commandList from blockchain before displaying
        getCommandList()
        output = '<table border=1 align=center width=100%><tr><th><font size="3" color="black">Username</th><th><font size="3" color="black">Sensor</th>'
        output+='<th><font size="3" color="black">Processed Command</th><th><font size="3" color="black">Hashcode</th><th><font size="3" color="black">Date</th></tr>'
        has_records = False
        for i in range(len(commandList)):
            clist = commandList[i]
            arr = clist[3].split("#")
            if username == clist[0]:
                has_records = True
                output += '<tr><td><font size="3" color="black">'+str(clist[0])+'</td><td><font size="3" color="black">'+str(clist[1])+'</td>'
                output += '<td><font size="3" color="black">'+str(clist[2])+'</td>'
                output += '<td><font size="3" color="black">'+str(arr[0])+'</td>'
                output += '<td><font size="3" color="black">'+str(arr[1])+'</td></tr>'
        if not has_records:
            output += '<tr><td colspan="5" align="center"><font size="3" color="black">No command history found</td></tr>'
        output += "</table><br/><br/><br/><br/>"    
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def SendCommandAction(request):
    if request.method == 'POST':
        global username, response_time, commandList, contract
        sensor = request.POST.get('t1', False)
        command = request.POST.get('t2', False)
        dd = str(date.today())
        msg = username+"#"+sensor+"#"+command+"#"+dd
        start_time = timeit.default_timer()
        hashcode = hashlib.sha256(msg.encode()).hexdigest()
        encrypted = encrypt(msg.encode())
        encrypted = base64.b64encode(encrypted).decode('utf-8')
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            client.settimeout(30)  # Add timeout
            client.connect(('localhost', 2222))
            jsondata = json.dumps({"hashcode": hashcode, "fdata": encrypted})
            client.send(jsondata.encode())
            data = client.recv(300)
            data = data.decode()
            client.close()
            end_time = timeit.default_timer()
            response_time.append(end_time - start_time)
            # Refresh commandList from blockchain after command
            getCommandList()
            print("Command sent successfully:", username, sensor, command)
            context= {'data':'<font size=3 color=blue>Response received from Sensor : '+data+"</font>"}
        except socket.timeout:
            context= {'data':'<font size=3 color=red>Error: Connection timed out. Make sure IOT Simulation is running and click Generate Networks!</font>'}
        except Exception as e:
            print("Error sending command:", str(e))
            context= {'data':'<font size=3 color=red>Error: '+str(e)+'. Make sure IOT Simulation is running!</font>'}
        return render(request, 'SendCommand.html', context)

def SendCommand(request):
    if request.method == 'GET':
       return render(request, 'SendCommand.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})    

def AddUser(request):
    if request.method == 'GET':
       return render(request, 'AddUser.html', {})

def AddUserAction(request):
    if request.method == 'POST':
        global userList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        phone = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        for i in range(len(userList)):
            user = userList[i]
            if username == user[0]:
                status = "exists"
                break
        if status == "none":
            msg = contract.functions.createUser(username, password, phone, email, address).transact({'from': web3.eth.default_account})
            tx_receipt = web3.eth.wait_for_transaction_receipt(msg)
            userList.append([username, password, phone, email, address])
            context= {'data':'New User Details Added to Blockchain with below verification hashcode & transaction details <br/>'+str(tx_receipt)}
            return render(request, 'AddUser.html', context)
        else:
            context= {'data':'Given username already exists'}
            return render(request, 'AddUser.html', context)    

def UserLoginAction(request):
    if request.method == 'POST':
        global username, contract, userList
        # Refresh userList from blockchain before authentication
        getUserList()
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "UserLogin.html"
        output = 'Invalid login details'
        print("User list:", userList)
        for i in range(len(userList)):
            ulist = userList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            if user1 == username and pass1 == password:
                status = "UserScreen.html"
                output = 'Welcome '+username
                break           
        context= {'data':output}
        return render(request, status, context)

def AdminLoginAction(request):
    if request.method == 'POST':
        global username, contract, mdaList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "AdminLogin.html"
        output = 'Invalid login details'
        if username == "admin" and password == "admin":
            status = "AdminScreen.html"
            output = 'Welcome '+username
        context= {'data':output}
        return render(request, status, context)





