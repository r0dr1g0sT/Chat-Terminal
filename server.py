import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}
salas = {}
senhas = {}

def broadcast(msg, sala=None, cliente_atual=None):
    for client in clients:
        if salas.get(client) == sala and client != cliente_atual:
            try:
                client.send(msg.encode('utf-8'))
            except:
                remover_cliente(client)

def remover_cliente(client):
    if client in clients:
        clients.remove(client)
    if client in salas:
        del salas[client]
    if client in usernames:
        del usernames[client]
    client.close()

def handle(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                remover_cliente(client)
                break

            if msg == "/sair":
                remover_cliente(client)
                break

            if msg == "/salas":
                lista_salas = list(set(salas.values()))
                client.send(f"Salas disponíveis: {', '.join(lista_salas)}\n".encode('utf-8'))
                continue

            if msg.startswith("/entrar "):
                nova_sala = msg.split(" ", 1)[1]
                salas[client] = nova_sala
                client.send(f"Você entrou na sala {nova_sala}\n".encode('utf-8'))
                broadcast(f"[{usernames[client]}] entrou na sala {nova_sala}\n", nova_sala)
                continue

            if client in usernames:
                sala = salas.get(client)
                mensagem_formatada = f"[{usernames[client]}] {msg}"
                broadcast(mensagem_formatada, sala, cliente_atual=client)

        except:
            remover_cliente(client)
            break

def autenticar(client):
    client.send("Digite [1] para login ou [2] para criar conta: ".encode('utf-8'))
    escolha = client.recv(1024).decode('utf-8').strip()

    client.send("Usuário: ".encode('utf-8'))
    username = client.recv(1024).decode('utf-8').strip()

    client.send("Senha: ".encode('utf-8'))
    senha = client.recv(1024).decode('utf-8').strip()

    if escolha == "1":
        if username in senhas and senhas[username] == senha:
            client.send("Login bem-sucedido!\n".encode('utf-8'))
        else:
            client.send("Falha no login. Tente novamente.\n".encode('utf-8'))
            autenticar(client)
            return
    elif escolha == "2":
        if username in senhas:
            client.send("Usuário já existe. Tente novamente.\n".encode('utf-8'))
            autenticar(client)
            return
        else:
            senhas[username] = senha
            client.send("Conta criada com sucesso!\n".encode('utf-8'))
    else:
        client.send("Opção inválida. Tente novamente.\n".encode('utf-8'))
        autenticar(client)
        return

    usernames[client] = username

def receive():
    print(f"Servidor escutando em {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"Conectado a {address}")

        autenticar(client)

        client.send("Digite o nome da sala para entrar/criar: ".encode('utf-8'))
        sala = client.recv(1024).decode('utf-8').strip()

        salas[client] = sala
        clients.append(client)

        print(f"Usuário [{usernames[client]}] entrou na sala [{sala}]")

        broadcast(f"[{usernames[client]}] entrou no chat!\n", sala)
        broadcast(f"[{usernames[client]}] entrou na sala {sala}\n", sala)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
