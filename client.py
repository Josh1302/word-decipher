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
            sys.exit(0) 

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
        print(msg["message"], "\n")
    elif msg_type == "join":
        print(f"{msg['username']} has joined the game.\n")
    elif msg_type == "move":
        print(f"{msg['username']} guessed: {msg['move']}\n")  
    elif msg_type == "chat":
        print(f"{msg['username']} says: {msg['message']}\n")
    elif msg_type == "leave" or msg_type == "quit":
        print(f"{msg['username']} has left the game.\n")
    elif msg_type == "win":
        print(f"{msg['username']} won the game by guessing the word! New Game Starting...\n")
    elif msg_type == "error":
        print(f"Error: {msg['message']}\n")
    else:
        print("Unknown message type received from server\n")

def input_thread(data):
    try:
        
        user_input = input("\nEnter command (/move <word>, /chat <message>, /quit): \n").strip()

        while True:
            if user_input.startswith("/move "):
                move_cmd = user_input[6:].strip()
                if len(move_cmd) == 5 and move_cmd.isalpha():
                    move_msg = json.dumps({"type": "move", "move": move_cmd.lower()})
                    data.messages.append(move_msg)
                    print()  # Add a newline for better formatting
                else:
                    print("Invalid move. Please enter a valid 5-letter word.\n")
            
            elif user_input.startswith("/chat "):
                chat_msg_text = user_input[6:].strip()
                if chat_msg_text:
                    chat_msg = json.dumps({"type": "chat", "message": chat_msg_text})
                    data.messages.append(chat_msg)
                    print()  
                else:
                    print("Chat message cannot be empty.\n")

            elif user_input == "/quit":
                quit_msg = json.dumps({"type": "quit"})
                data.messages.append(quit_msg)
                print("Disconnected from server\n")
                sys.exit(0)
            
            else:
                print("Unknown command. Valid commands are: /move <word>, /chat <message>, /quit.\n")

            user_input = input("\nEnter command (/move <word>, /chat <message>, /quit): \n").strip()

    except EOFError:
        print("Exiting input thread.\n")
    except KeyboardInterrupt:
        print("\nClient shutting down.\n")
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
