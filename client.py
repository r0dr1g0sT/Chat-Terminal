import socket
import threading
import sys
import os
import random
from colorama import Fore, Style, init

init(autoreset=True)

HOST = '127.0.0.1'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

mensagens = []
cores_usuarios = {}
meu_nome = None
sala_atual = "Nenhuma"

cores_disponiveis = [
    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE
]

def colorir_nome(msg):
    if msg.startswith("[") and "]" in msg:
        inicio = msg.find("[")
        fim = msg.find("]") + 1
        nome_bruto = msg[inicio:fim]
        usuario = nome_bruto.strip("[]")
        if usuario not in cores_usuarios:
            cor = random.choice(cores_disponiveis)
            cores_usuarios[usuario] = cor
        msg_colorido = msg.replace(nome_bruto, f"{cores_usuarios[usuario]}[{usuario}]{Style.RESET_ALL}")
        return msg_colorido
    return msg

def mostrar_interface():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.YELLOW + "====== CHAT EM TEMPO REAL ======" + Style.RESET_ALL)

    print(Fore.CYAN + "╔══════════════════════════════════════════╗")
    print("║           Mensagens recebidas            ║")
    print("╚══════════════════════════════════════════╝" + Style.RESET_ALL)

    for msg in mensagens[-50:]:
        print(colorir_nome(msg))

    print(Fore.YELLOW + "\n╔══════════════════════════════════════════╗")
    print(f"║ Sala Atual: {sala_atual or 'Nenhuma':<32}║")
    print("╚══════════════════════════════════════════╝" + Style.RESET_ALL)

    print(Fore.YELLOW + "\n╔══════════════════════════════════════════╗")
    print("║ Digite sua mensagem abaixo (ou /ajuda):  ║")
    print("╚══════════════════════════════════════════╝" + Style.RESET_ALL)

def receber_mensagem_esperada(prompt_final):
    buffer = ""
    while True:
        parte = client.recv(1024).decode('utf-8')
        buffer += parte
        print(parte, end='')
        if prompt_final in parte or parte.endswith(': ') or parte.endswith(':\n'):
            break

def autenticar():
    global meu_nome
    receber_mensagem_esperada(": ")
    client.send(input().strip().encode('utf-8'))

    receber_mensagem_esperada("Usuário: ")
    usuario = input().strip()
    client.send(usuario.encode('utf-8'))

    receber_mensagem_esperada("Senha: ")
    senha = input().strip()
    client.send(senha.encode('utf-8'))

    resposta = client.recv(1024).decode('utf-8')
    print(resposta)
    if "Login bem-sucedido" not in resposta and "Conta criada com sucesso" not in resposta:
        return autenticar()

    meu_nome = usuario  # CORRIGIDO: pega o nome do login!

def receive():
    global sala_atual
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                for linha in msg.split('\n'):
                    if linha.strip():
                        mensagens.append(linha)
                        if "entrou na sala" in linha:
                            partes = linha.split("entrou na sala")
                            if len(partes) > 1:
                                nova_sala = partes[1].strip()
                                sala_atual = nova_sala
                mostrar_interface()
        except:
            print("[ERRO] Conexão encerrada.")
            client.close()
            break

def write():
    global sala_atual
    while True:
        print(Fore.YELLOW + "╔══════════════════════════════════════════╗")
        msg = input("║ > ")
        print("╚══════════════════════════════════════════╝" + Style.RESET_ALL)
        
        if msg == "/ajuda":
            print("\nComandos disponíveis:")
            print("  /ajuda          - Lista os comandos")
            print("  /sair           - Sai do chat")
            print("  /salas          - Lista as salas disponíveis")
            print("  /entrar <sala>  - Entra em uma sala específica\n")
        elif msg == "/sair":
            client.send(msg.encode('utf-8'))
            client.close()
            print("Você saiu do chat.")
            sys.exit()
        elif msg == "/salas":
            client.send(msg.encode('utf-8'))
        elif msg.startswith("/entrar "):
            nova_sala = msg.split(" ", 1)[1].strip()
            client.send(f"/entrar {nova_sala}".encode('utf-8'))
            sala_atual = nova_sala
        else:
            client.send(msg.encode('utf-8'))
            mensagens.append(f"[{meu_nome}] {msg}")
            mostrar_interface()

def start_chat():
    global sala_atual
    autenticar()
    print("Digite o nome da sala para entrar/criar: ", end="")
    sala = input().strip()
    sala_atual = sala
    client.send(sala.encode('utf-8'))
    threading.Thread(target=receive, daemon=True).start()
    write()

if __name__ == '__main__':
    start_chat()
