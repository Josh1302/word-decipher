#!/usr/bin/env python3

import sys
import socket
import selectors
import threading
import json
import types

sel = selectors.DefaultSelector()

def start_connection(host, port, username):
    server_addr = (host, port)
    print("Starting connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        sock.connect_ex(server_addr)
    except OSError as e:
        print(f"Connection error: {e}")
        sys.exit(1)
    data = types.SimpleNamespace(
        sock=sock,
        username=username,
        messages=[],
        outb=b"",  
        inb=b"",   
    )
    sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
   
    join_msg = json.dumps({"type": "join", "username": username})
    data.messages.append(join_msg)
    return data

def network_thread(data):
    sock = data.sock
    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                service_connection(key, mask)
    except Exception as e:
        print(f"Network error: {e}")
    finally:
        sel.unregister(sock)
        sock.close()

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.inb += recv_data
           
            while b'\n' in data.inb:
                message, data.inb = data.inb.split(b'\n', 1)
                try:
                    msg = json.loads(message.decode())
                    handle_server_message(msg)
                except json.JSONDecodeError:
                    print("Received invalid JSON message from server")
        else:
            print("Server closed connection")
            sel.unregister(sock)
            sock.close()
            sys.exit(0)  # Exit the program

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            
            data.outb = (data.messages.pop(0) + '\n').encode()
        if data.outb:
            try:
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
            except OSError as e:
                print(f"Error sending data: {e}")
                sel.unregister(sock)
                sock.close()
                sys.exit(0)  # Exit the program

def handle_server_message(msg):
    msg_type = msg.get("type")

    if msg_type == "join_ack":
        print(msg["message"])
    elif msg_type == "join":
        print(f"{msg['username']} has joined the game.")
    elif msg_type == "move":
        print(f"{msg['username']} made a move: {msg['move']}")
    elif msg_type == "chat":
        print(f"{msg['username']} says: {msg['message']}")
    elif msg_type == "leave" or msg_type == "quit":
        print(f"{msg['username']} has left the game.")
    else:
        print("Unknown message type received from server")

def input_thread(data):
    try:
        while True:
            user_input = input()
            if user_input.startswith("/move "):
                move_cmd = user_input.split("/move ", 1)[1]
                move_msg = json.dumps({"type": "move", "move": move_cmd})
                data.messages.append(move_msg)
            elif user_input.startswith("/chat"):
                if user_input == "/chat":
                    print("Please provide a message to send. Usage: /chat <message>")
                elif user_input.startswith("/chat "):
                    chat_msg_text = user_input.split("/chat ", 1)[1]
                    chat_msg = json.dumps({"type": "chat", "message": chat_msg_text})
                    data.messages.append(chat_msg)
                else:
                    print("Unknown command. Use /move, /chat, or /quit.")
            elif user_input == "/quit":
                quit_msg = json.dumps({"type": "quit"})
                data.messages.append(quit_msg)
                print("Disconnected from server")
                sys.exit(0)
            else:
                print("Unknown command. Use /move, /chat, or /quit.")
    except EOFError:
        pass
    except KeyboardInterrupt:
        sys.exit(0)

def main():
    if len(sys.argv) != 4:
        print("Usage:", sys.argv[0], "<host> <port> <username>")
        sys.exit(1)

    host, port, username = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    data = start_connection(host, port, username)

    
    net_thread = threading.Thread(target=network_thread, args=(data,), daemon=True)
    net_thread.start()

    
    input_thread(data)

if __name__ == "__main__":
    main()
