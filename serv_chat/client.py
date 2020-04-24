import os
import socket
import sys
import select
import signal
import json

MAXBYTES = 4096



def handler(sig,ign):
    global s
    s.sendall(b"")
    sys.exit(130)



def emoji(msg):
    emojis = {}
    with open('emojis.json') as outfile:
        emojis = json.load(outfile)

    for emoji,short in emojis.items():
        msg = msg.replace(short, emoji)
    
    return msg





if len(sys.argv) != 3:
    print('Usage:', sys.argv[0], 'hote port')
    sys.exit(1)
    
HOST = sys.argv[1]
PORT = int(sys.argv[2])

sockaddr = (HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
s.connect(sockaddr)
socketlist = [s, 0]

signal.signal(signal.SIGINT,handler)
print('connected to:', sockaddr)
print("Pour vous connecter entrez un pseudo,\nle pseudo doit faire maximum 8 caracteres :")
pseudo = 1 
while True: 
    readable, _, _ = select.select(socketlist, [], [])
    for socs in readable:
        if socs == 0:
            if pseudo == 1:
                line = os.read(0, MAXBYTES)
                #print(len(line))
                #print(line[len(line)-1])
                if len(line)>9 or len(line)==1:
                    print("pseudo invalide reessayez:")
                    continue
                pseudo = 0
                name = line.decode('utf8')
                name = name.replace('\n','')
                if(name == "Laurent" )or(name == "laurent"):
                    print("quel beau prénom 😍😍")
                name = f"\033[35m{name}\033[0m"
                print("bievenue",name,":\nVous pouvez mentionner des gens en utilisant @ \net utiliser des commandes avec /\n pour plus d'info faites /help")
                
            else:
                line = os.read(0, MAXBYTES)
                if len(line) > 1: 
                    line = emoji((line.decode('utf8').replace('\n',''))).encode('utf8')
            if len(line) == 0:
                print("deconexion")
                s.shutdown(socket.SHUT_WR)
           
            s.send(line)
        if socs == s:
            data = s.recv(MAXBYTES) # attention, si le serveur n'envoie rien on est bloqué.
            if data.decode('utf8') == "pseudo déjà utilisé\nRessaisissez un pseudo différent svp\n":
                pseudo = 1
    
            if len(data) == 0 or (data.decode('utf8') == "server closing goodbye"):
                if len(data) > 0:
                    os.write(1, data)
                s.close
                sys.exit(0)
            os.write(1, data)
            print("")
s.close()


