import sys
import socket
import selectors
import types
import json
import random

sel = selectors.DefaultSelector()
game_active = True
WORDS = []
clients = {}

def generate_word_bank(file):
    f = open(file, "r")
    for word in f:
      WORDS.append(str(word.strip()))
    return WORDS

WORDS = generate_word_bank("/s/chopin/g/under/josh1302/cs457labs/word-decipher/5_letters.txt")
target_word = random.choice(WORDS)
print(target_word)

def reset_game():   
    global target_word, game_active
    target_word = random.choice(WORDS)
    game_active = True
    print(f"New target word: {target_word}")

def generate_feedback(target, guess):
    
    feedback = []
    for i, char in enumerate(guess):
        if char == target[i]:
            feedback.append("+")
        elif char in target:
            feedback.append("*")
        else:
            feedback.append("-")
    feedback = "".join(feedback) 
    return f"{guess}\nFeedback: {feedback}"

def broadcast(message):
    print(f"DEBUG: Broadcasting message: {message}")
    for sock in clients:
        data = clients[sock]
        data.outb += (message + '\n').encode()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", username=None)
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
    clients[conn] = data

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  
            if recv_data:
                print(f"DEBUG: Received raw data from {data.addr}: {recv_data.decode()}") 
                data.inb += recv_data
                while b'\n' in data.inb:  
                    message, data.inb = data.inb.split(b'\n', 1)
                    try:
                        msg = json.loads(message.decode())
                        handle_message(sock, msg)  
                    except json.JSONDecodeError:
                        print(f"DEBUG: Received invalid JSON message from {data.addr}")
            else:
                print(f"DEBUG: Connection closed by client {data.addr}")
                close_connection(sock)
                  
        except Exception as e:
            print(f"DEBUG: Error reading from {data.addr}: {e}")
            close_connection(sock)

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            try:
                sent = sock.send(data.outb)  
                print(f"DEBUG: Sent data to {data.addr}: {data.outb[:sent].decode()}")  
                data.outb = data.outb[sent:]  
            except Exception as e:
                print(f"DEBUG: Error writing to {data.addr}: {e}")
                close_connection(sock)

def handle_message(sock, msg):
    global game_active
    data = clients[sock]
    msg_type = msg.get("type")

    if msg_type == "join":
        username = msg.get("username", "Anonymous")
        data.username = username
        print(f"User '{username}' joined from {sock.getpeername()}")

        join_ack = json.dumps({"type": "join_ack", "message": f"Welcome, {username}"})
        data.outb += (join_ack + '\n').encode()

        join_msg = json.dumps({"type": "join", "username": username})
        broadcast(join_msg)

    elif msg_type == "move" and game_active:
        move = msg.get("move", "").lower()
        username = data.username

        if len(move) != 5:
            error_msg = json.dumps({"type": "error", "message": "Your guess must be a 5-letter word."})
            data.outb += (error_msg + '\n').encode()
            return

        print(f"DEBUG: Received move from {username}: {move}")
        feedback = generate_feedback(target_word, move)
        print(f"DEBUG: Feedback for '{move}': {feedback}")

        move_msg = json.dumps({"type": "move", "username": username, "move": feedback})
        broadcast(move_msg)

        if move == target_word:
            game_active = False
            win_msg = json.dumps({"type": "win", "username": username, "message": f"{username} guessed the word!"})
            broadcast(win_msg)
            reset_game()

    elif msg_type == "chat":
        chat_message = msg.get("message", "")
        username = data.username
        print(f"DEBUG: Chat from {username}: {chat_message}")

        chat_msg = json.dumps({"type": "chat", "username": username, "message": chat_message})
        broadcast(chat_msg)

    elif msg_type == "quit":
        username = data.username
        print(f"User '{username}' quit")

        quit_msg = json.dumps({"type": "quit", "username": username})
        broadcast(quit_msg)
        close_connection(sock)
    else:
        print(f"Unknown message type received from {data.addr}: {msg_type}")

def close_connection(sock):
    try:
        if sock.fileno()!=-1:
            sel.unregister(sock)
    except Exception as e:
        print(f"Unexpected error durring unregistration: {e}")
    finally:
        sock.close()
        if sock in clients:
            del clients[sock]
            
def main():
    host =  "0.0.0.0"
    port =  int(sys.argv[2])

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Server listening on {host}:{port}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Server shutting down")
    finally:
        sel.close()

if __name__ == "__main__":
    main()
