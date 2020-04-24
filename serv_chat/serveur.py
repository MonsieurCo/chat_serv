import os
import select
import socket
import sys
import signal


socketlist = []
serversocket = []
n = 0
def hanlder(s,ign):
    global socketlist
    global serversocket 
    for client in socketlist[2:]: # on ferme tout les clients connectes
        client.sendall("server closing goodbye".encode('utf8'))
        client.close()
        serversocket.close()
    print("Server closed")
    sys.exit(130)



def shutdown(sig,ign):
    print("will shutdown")
    global socketlist
    global serversocket 
    for client in socketlist[2:]: # on ferme tout les clients connectes
        client.close()
        serversocket.close()
    print("Server closed")
    sys.exit(0)




HOST = '127.0.0.1' # or 'localhost' or '' - Standard loopback interface address
PORT = 2003 # Port to listen on (non-privileged ports are > 1023)
MAXBYTES = 4096


def check_serv(s,data,users,talker,admin,socketlist):
    data = data.split(' ')
    #print(data)
    if data[0][0] == "@":# nous avons affaire aune mention
        id_interloc = data[0][1:]
        #print(id_interloc)
        message = " ".join(data[1:])
        if id_interloc == "everyone" or id_interloc == "tous" :
            for i in users.values():
                if not(admin) and(i == users[talker]):
                    continue
                message = " ".join(data)
                talkercolored = f"\033[35m{talker}\033[0m"
                message = "from : " + talkercolored + "\n" + message
                message = message.encode('utf8')
                i.sendall(message)
        else:
            
            if id_interloc in users:
                message = " ".join(data)
                talkercolored = f"\033[35m{talker}\033[0m"
                message = "from : " + talkercolored + "\n" + message
                message = message.encode('utf8')
                users[id_interloc].sendall(message)

    elif data[0][0] == '/': #nous avons affaire a une commande
        if data[0] == '/help':
            message = "Commandes:\n\t/userlist->renvoie la liste des utilisateur actif\n\t/kick@user (necessite permission administrateur)\n\t/wall envoie un message a tout les utilisateurs(admin)\n\t/shutdown n arrete le serveur apres n secondes (admin)\ndes emoji son disponible pour plus d'info faites /emoji\nMentions:\n\t@user -> mentionne un utilisateur\n\t@everyone -> mentionne tout le monde\n\t@tous -> mentionne tout le monde"
            if admin == False:
                message = ("cmd:\n" + message).encode('utf8')
                s.sendall(message)
            else:
                print(message)
        if data[0] == '/emoji':
            message = "liste d'emoji:\n😂: :joy:\t😍: :heart_eyes:\t😭: :sob:\n😊: :blush:\t😘: : kissing_heart:\t😉: :wink:\nIl exite plus d'emoji pour les voir tous renseignez vous dans le json\n"
            if admin == False:
                message = ("cmd:\n" + message).encode('utf8')
                s.sendall(message)
            else:
                print(message)
        
        if data[0] == "/userlist":
            message = "cmd:\nUsers list:\n" + "\n".join(users.keys())+"\n"
            message = message.encode('utf8')
            if admin == False:
                s.sendall(message) 
            else:
                print(message)

        if (data[0][0:6] == "/kick@") and admin == True:
            print("kick demand for ",data[0][6:])
            id_to_kick = data[0][6:]
            print(id_to_kick)
            if (id_to_kick in users):
                users[id_to_kick].sendall("you have been kicked by \033[31mAdmin\033[0m\n".encode('utf8'))
                users[id_to_kick].close()
                socketlist.remove(users[id_to_kick])
                del users[id_to_kick]
                print(id_to_kick,"has been kicked")
                #on previent les utilisateur du kick
                id_to_kick = f"\033[35m{id_to_kick}\033[0m"

                for i in users.values():
                    message = id_to_kick +" has been kicked by \033[31mAdmin\033[0m\n"
                    message = "from : \033[31mAdmin\033[0m"+"\n" + message
                    message = message.encode('utf8')
                    i.sendall(message)

        if (data[0] == "/shutdown") and admin == True:
            try:
                n = int(data[1])
                for i in users.values():
                        message = f"\033[31mWARNING \nServer Shutting Down in {data[1]} seconds\033[0m\n"
                        message = "from : \033[31mAdmin\033[0m"+"\n" + message
                        message = message.encode('utf8')
                        i.sendall(message)
                        signal.alarm(n)
            except:
                print("wrong argument")
        if (data[0] == "/wall") and admin == True:
             for i in users.values():
                message = " ".join(data[1:])
                talkercolored = f"\033[35m{talker}\033[0m"
                message = "from : " + talkercolored + "\n" + message
                message = message.encode('utf8')
                i.sendall(message)


    else:
        data = " ".join(data)
        if admin ==False:
            print('retour à l envoyeur ',data)
            s.sendall(data.encode('utf8'))
        else:
            print(data)



def server():
    global socketlist
    global serversocket 
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((HOST, PORT))
    serversocket.listen()
    socketlist = [serversocket, 0]
    users = dict()
    
    while len(socketlist) > 0:
        readable, _, _ = select.select(socketlist, [], [])
        for s in readable:
            try:
                for usr in users.keys():
                    if  users[usr] == s :
                        current_talker = usr
            except:
                pass

            if s == 0: # si c'est l'entree standart
                buffer = os.read(0, MAXBYTES)
                data = buffer.decode("utf8")
                if len(data) > 1:
                    data = data.replace('\n','')
                    check_serv(s,data,users,"admin",True,socketlist)
                if buffer == b"\n": # si on a la touche entree donc \n on close le serveur et on quitte
                    for client in socketlist[2:]: # on ferme tout les clients connectes
                        client.close()
                    serversocket.close()
                    print("Server closed")
                    sys.exit(0)
                else:
                    break
            if s == serversocket: # serversocket receives a connection
                clientsocket, (addr, port) = s.accept()
                socketlist.append(clientsocket)
                connexion = 1
                
                
            else: # data is sent from given client
                if connexion == 1:
                    data = s.recv(MAXBYTES)
                    data = data.decode('utf-8')
                    data = data.replace('\n','')
                    #print(data,s)
                    if not(data in users):
                        users[data]= clientsocket
                        connexion = 0
                    else:
                        warning = "pseudo déjà utilisé\nRessaisissez un pseudo différent svp\n".encode('utf8')
                        s.sendall(warning)
                    
                else:
                    data = s.recv(MAXBYTES)
                    data = data.decode('utf8')
                    
                    if len(data) > 0:
                        check_serv(s,data,users,current_talker,False,socketlist)
                    
                    else: # client has disconnected
                        print("deconexion client")
                        for i in users.keys():
                            if users[i] == s:
                                acc = i
                                break
                        del users[acc]     
                        socketlist.remove(s)
                        s.close()
                        for i in users.values():
                            message = "client "+ f"\033[31m{acc}\033[0m" + " has disconnected"
                            message = message.encode('utf8')
                            i.sendall(message)
                        
        #print(users)
    serversocket.close()
signal.signal(signal.SIGINT,hanlder)   
print("for connection, host: {}/localhost & port: {}".format(HOST, PORT))
server()
