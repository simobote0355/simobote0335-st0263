import socket
import threading
import pickle
import sys
import hashlib
import time
import json
import os
from collections import OrderedDict

# Valores por defecto
IP = "127.0.0.1"
PORT = 5000
buffer = 4096

# Carpeta para guardar config y archivos de cada nodo
config_directory = "config"
files_directory = "files"

# Bits para la hash table
MAX_BITS = 10        
MAX_NODES = 2 ** MAX_BITS

# Función hash que crea ID por cada nodo instanciado
def getHash(key):
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES

# Clase nodo
class Node:
    def __init__(self, ip, port):
        # Info del nodo
        self.ip = ip
        self.port = port
        self.address = (ip, port)
        self.id = getHash(ip + ":" + str(port))

        # Info del predecesor
        self.pred = (ip, port)
        self.predID = self.id

        # Info del sucesor
        self.succ = (ip, port)            
        self.succID = self.id

        # Finger Table
        self.fingerTable = OrderedDict()         

        # Crear carpeta de config y files
        self.node_directory = os.path.join(files_directory, f"node_{self.port}")
        self.config_path = os.path.join(config_directory, f"node_{self.port}.json")
        self.create_node_directory()
        self.save_node_config()
        
        # Crear el socket
        try:
            self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ServerSocket.bind((IP, PORT))
            self.ServerSocket.listen()
        except socket.error:
            print("Socket not opened")

    # Verfica si ya existe un carpeta files asociada
    def create_node_directory(self):
        if not os.path.exists(self.node_directory):
            os.makedirs(self.node_directory)    

    # Crea json y lo guarda en la carpeta config
    def save_node_config(self):
        config_data = {
            "ip": self.ip,
            "port": self.port,
            "directory": self.node_directory,
        }
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)
        with open(self.config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)

    # Escuchar nuevas conexiones de nodos    
    def listenThread(self):
        while True:
            try:
                connection, address = self.ServerSocket.accept()
                connection.settimeout(120)
                threading.Thread(target=self.connectionThread, args=(connection, address)).start()
            except socket.error:
                pass

    # Thread for each peer connection
    def connectionThread(self, connection, address):
        rDataList = pickle.loads(connection.recv(buffer))
        # 5 Types of connections
        # type 0: peer connect, type 1: client, type 2: ping, type 3: lookupID, type 4: updateSucc/Pred
        connectionType = rDataList[0]
        if connectionType == 0:
            print("Connection with:", address[0], ":", address[1])
            print("Join network request received")
            self.joinNode(connection, address, rDataList)
            self.printMenu()
        elif connectionType == 1:
            print("Connection with:", address[0], ":", address[1])
            print("Upload/Download request received")
            # Transfer file logic is handled by REST API now
            self.printMenu()
        elif connectionType == 2:
            connection.sendall(pickle.dumps(self.pred))
        elif connectionType == 3:
            self.lookupID(connection, address, rDataList)
        elif connectionType == 4:
            if rDataList[1] == 1:
                self.updateSucc(rDataList)
            else:
                self.updatePred(rDataList)
        elif connectionType == 5:
            self.updateFTable()
            connection.sendall(pickle.dumps(self.succ))
        else:
            print("Problem with connection type")

    def joinNode(self, connection, address, rDataList):
        if rDataList:
            peerIPport = rDataList[1]
            peerID = getHash(peerIPport[0] + ":" + str(peerIPport[1]))
            oldPred = self.pred
            self.pred = peerIPport
            self.predID = peerID
            sDataList = [oldPred]
            connection.sendall(pickle.dumps(sDataList))
            time.sleep(0.1)
            self.updateFTable()
            self.updateOtherFTables()

    # Buscar ID de un nodo en especifico
    def lookupID(self, connection, address, rDataList):
        keyID = rDataList[1]
        sDataList = []
        if self.id == keyID:
            sDataList = [0, self.address]
        elif self.succID == self.id:
            sDataList = [0, self.address]
        elif self.id > keyID:
            if self.predID < keyID:
                sDataList = [0, self.address]
            elif self.predID > self.id:
                sDataList = [0, self.address]
            else:
                sDataList = [1, self.pred]
        else:
            if self.id > self.succID:
                sDataList = [0, self.succ]
            else:
                value = ()
                for key, value in self.fingerTable.items():
                    if key >= keyID:
                        break
                value = self.succ
                sDataList = [1, value]
        connection.sendall(pickle.dumps(sDataList))

    # Actualizar sucesor
    def updateSucc(self, rDataList):
        newSucc = rDataList[2]
        self.succ = newSucc
        self.succID = getHash(newSucc[0] + ":" + str(newSucc[1]))

    # Actualziar predecesor
    def updatePred(self, rDataList):
        newPred = rDataList[2]
        self.pred = newPred
        self.predID = getHash(newPred[0] + ":" + str(newPred[1]))
        
    # Inicia el nodo
    def start(self):
        threading.Thread(target=self.listenThread, args=()).start()
        while True:
            print("Listening to other clients")   
            self.asAClientThread()

    # Interacción del cliente con la red (solo para añadir, quitar o pedir predecesor y sucesor de los nodos) 
    def asAClientThread(self):
        self.printMenu()
        userChoice = input()
        if userChoice == "1":
            ip = input("Enter IP to connect: ")
            port = input("Enter port: ")
            self.connect_to_node(ip, int(port))
        elif userChoice == "2":
            self.leaveNetwork()
        elif userChoice == "3":
            print("My ID:", self.id, "Predecessor:", self.predID, "Successor:", self.succID)
        elif userChoice == "4":
            self.show_files()
        else:
            print("Not valid option")

    # Conectar a un nodo ya existente
    def connect_to_node(self, ip, port):
        try:
            recvIPPort = self.getSuccessor((ip, port), self.id)
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerSocket.connect(recvIPPort)
            sDataList = [0, self.address]
            peerSocket.sendall(pickle.dumps(sDataList))
            rDataList = pickle.loads(peerSocket.recv(buffer))
            self.pred = rDataList[0]
            self.predID = getHash(self.pred[0] + ":" + str(self.pred[1]))
            self.succ = recvIPPort
            self.succID = getHash(recvIPPort[0] + ":" + str(recvIPPort[1]))
            sDataList = [4, 1, self.address]
            pSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket2.connect(self.pred)
            pSocket2.sendall(pickle.dumps(sDataList))
            pSocket2.close()
            peerSocket.close()
        except socket.error:
            print("Socket error. Recheck IP/Port.")

    # Abandonar la red
    def leaveNetwork(self):
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.succ)
        pSocket.sendall(pickle.dumps([4, 0, self.pred]))
        pSocket.close()
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.pred)
        pSocket.sendall(pickle.dumps([4, 1, self.succ]))
        pSocket.close()
        print("I had files:", os.listdir(self.node_directory))
        print("Replicating files to other nodes before leaving")
        for filename in os.listdir(self.node_directory):
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket.connect(self.succ)
            sDataList = [1, 1, filename]
            pSocket.sendall(pickle.dumps(sDataList))
            with open(filename, 'rb') as file:
                pSocket.recv(buffer)
                self.sendFile(pSocket, filename)
                pSocket.close()
                print("File replicated")
            pSocket.close()
        self.updateOtherFTables()
        self.pred = (self.ip, self.port)
        self.predID = self.id
        self.succ = (self.ip, self.port)
        self.succID = self.id
        self.fingerTable.clear()
        print(self.address, "has left the network")

    # Obtener sucesor
    def getSuccessor(self, address, keyID):
        rDataList = [1, address]
        recvIPPort = rDataList[1]
        while rDataList[0] == 1:
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                peerSocket.connect(recvIPPort)
                sDataList = [3, keyID]
                peerSocket.sendall(pickle.dumps(sDataList))
                rDataList = pickle.loads(peerSocket.recv(buffer))
                recvIPPort = rDataList[1]
            except socket.error:
                print("Node at", recvIPPort[0], ":", recvIPPort[1], "not reachable")
                break
        return recvIPPort

    # Actualizar finger table si se conecta un nuevo nodo o deja la red
    def updateFTable(self):
        if self.succID != self.id:
            for i in range(MAX_BITS):
                j = (self.id + 2 ** i) % MAX_NODES
                if j == self.id:
                    self.fingerTable[j] = (self.ip, self.port)
                else:
                    sDataList = [3, j]
                    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        peerSocket.connect(self.succ)
                        peerSocket.sendall(pickle.dumps(sDataList))
                        rDataList = pickle.loads(peerSocket.recv(buffer))
                        self.fingerTable[j] = rDataList[1]
                    except socket.error:
                        print("Socket error. Node not reachable")

    # Actualizar otras finger table si se conecta un nuevo nodo o deja la red
    def updateOtherFTables(self):
        for key, value in self.fingerTable.items():
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket.connect(value)
            sDataList = [5]
            pSocket.sendall(pickle.dumps(sDataList))
            pSocket.close()

    def printMenu(self):
        print("1. Connect to a node")
        print("2. Leave Network")
        print("3. Show Network Info")
        print("4. Show files")
        print("Enter your choice:")

    def sendFile(self, connection, filename):
        try:
            with open(filename, 'rb') as f:
                connection.sendfile(f)
        except Exception as e:
            print("Error sending file:", e)

    def show_files(self):
        files = os.listdir(self.node_directory) 
        print(files)

    def find_file(self, file_name):
    # Verificar si el archivo está en el nodo actual
        if file_name in os.listdir(self.node_directory):
            return self.id  # Archivo encontrado en el nodo actual

        # Si el archivo no está en el nodo actual, buscar en los sucesores
        successor = self.getSuccessor(self.address, self.id)  # Obtén el sucesor del nodo actual
        return self.find_file_in_successor(successor, file_name)
    
    def find_file_in_successor(self, successor, file_name):
    # Búsqueda en el sucesor
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(successor)
                request = pickle.dumps([3, file_name])  # Tipo 3 para búsqueda de archivo
                sock.sendall(request)

                # Recibe los datos
                response_data = sock.recv(buffer)
                response = pickle.loads(response_data)

                # Depuración
                print(f"Received response from {successor[0]}:{successor[1]}: {response}")

                if response[0] == 1:  # Archivo encontrado
                    return response[1]  # Retorna el ID del nodo que tiene el archivo
                elif response[0] == 0:  # Archivo no encontrado en este sucesor
                    next_successor = self.get_next_successor(successor)
                    if next_successor:
                        return self.find_file_in_successor(next_successor, file_name)
                    else:
                        return None  # Archivo no encontrado en la red
        except socket.error as e:
            print(f"Node at {successor[0]}:{successor[1]} not reachable. Error: {e}")
            return None

if __name__ == "__main__":
    if len(sys.argv) == 3:
        IP = sys.argv[1]
        PORT = int(sys.argv[2])
        
    node = Node(IP, PORT)
    node.start()
