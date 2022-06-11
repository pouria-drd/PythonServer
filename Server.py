import socket
import threading

print("**************\n  Made by Pd\n**************\n")

Host = "188.121.111.58"
Port = 14120
Format = "utf-8"
Bytes = 2048

clients = []
nicknames = []

online_clients = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((Host, Port))
server.listen()


def broadcast(message):
    for client in clients:
        client.send(message)


def kick_user(name):
    global online_clients
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("\n**************\nYou were kicked by admin !\n**************\n".encode(Format))
        client_to_kick.close()
        nicknames.remove(name)
        online_clients -= 1
        broadcast(f"\n**************\n{name} was kicked by admin !\nonline :{online_clients}\n**************\n".encode(Format))


def ban_user(name):
    global online_clients
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("\n**************\nYou were banned by admin !\n**************\n".encode(Format))
        client_to_kick.close()
        online_clients -= 1
        nicknames.remove(name)
        broadcast(f"\n**************\n{name} was banned by admin !\nonline :{online_clients}\n**************\n".encode(Format))


def private_message(sender_name, message, receiver_name):
    if receiver_name in nicknames:
        private_name_index = nicknames.index(receiver_name)
        private_name = clients[private_name_index]
        private_name.send(f"\n**************\nPRIVATE MESSAGE FROM <{sender_name}> : {message}\n**************\n".encode(Format))


def handle(client):
    global online_clients
    while True:
        try:
            msg = message = client.recv(Bytes)
            msg = f"{msg.decode(Format)}"

            if msg.startswith("__xKICKx__"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_kick = message.decode(Format)[11:]
                    kick_user(name_to_kick)
                    print(f"{name_to_kick} was banned !")
                else:
                    client.send("Command was refused !".encode(Format))

            elif msg.startswith("__xBANx__"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_ban = message.decode(Format)[10:]
                    ban_user(name_to_ban)
                    with open("Bans.txt", "a") as ban_list:
                        ban_list.write(f"{name_to_ban}\n")

                    print(f"{name_to_ban} was banned !")
                else:
                    client.send("Command was refused !".encode(Format))

            elif msg.startswith("__xPRIVATEx__"):
                xpx, sender_name, receiver_name, prv_msg = msg.split("|")
                private_message(sender_name, prv_msg, receiver_name)
                print(f"Private message !! => sender: {sender_name}; message: {prv_msg}; receiver: {receiver_name}")
            else:
                broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                online_clients -= 1
                broadcast(f"\n**************\n{nickname} left the chat !\nonline :{online_clients}\n**************\n"
                          .encode(Format))
                nicknames.remove(nickname)
                break


def receive():
    global online_clients
    while True:
        client, address = server.accept()
        print(f"\n**************\nclient: {client}  --|||--  address :{address} connected !\n**************")

        client.send("__xNICKx__".encode(Format))
        nickname = client.recv(Bytes).decode(Format)

        with open("Bans.txt", "r") as f:
            bans = f.readlines()

        if nickname + "\n" in bans:
            client.send("__xBANx__".encode(Format))
            client.close()
            continue

        if nickname == "admin":
            client.send("__xPASSx__".encode(Format))
            password = client.recv(Bytes).decode(Format)

            if password != "1234":
                client.send("__xREFUSEDx__".encode(Format))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname of this client is :{nickname} !")

        online_clients += 1

        client.send(f"\n**************\nWelcome {nickname} !, Happy chatting !\n**************\n".encode(Format))
        broadcast(f"\n**************\n{nickname} joined the chat !\nOnline :{online_clients}\n**************\n"
                  .encode(Format))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("\n**************\nServer is online...\nWaiting for connections...\n**************\n")
receive()
