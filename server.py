#!/usr/bin/env python3

import sys
import socket
import selectors
import types
import json
import logging

sel = selectors.DefaultSelector()


clients = {}

def log_tcp_connection(client_address):
    logging.info(f"Connection from {client_address}")

def broadcast(sender_sock, message):
    print(f"Broadcasting message: {message}")
    for sock in clients:
        if sock != sender_sock:
            data = clients[sock]
            data.outb += (message + '\n').encode()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print("Accepted connection from", addr)
    log_tcp_connection(addr)
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
                data.inb += recv_data
                # Process messages (assuming newline-delimited JSON)
                while b'\n' in data.inb:
                    message, data.inb = data.inb.split(b'\n', 1)
                    try:
                        msg = json.loads(message.decode())
                        handle_message(sock, msg)
                    except json.JSONDecodeError as e:
                        print(f"Received invalid JSON message from {data.addr}: {e}")
            else:
                print("Closing connection to", data.addr)
                sel.unregister(sock)
                sock.close()
                if sock in clients:
                    username = data.username
                    del clients[sock]
                    # Notify others
                    if username:
                        leave_msg = json.dumps({"type": "leave", "username": username})
                        broadcast(sock, leave_msg)
        except Exception as e:
            print(f"Error reading from socket {data.addr}: {e}")
            sel.unregister(sock)
            sock.close()
            if sock in clients:
                del clients[sock]

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            try:
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]
            except Exception as e:
                print(f"Error writing to socket {data.addr}: {e}")
                sel.unregister(sock)
                sock.close()
                if sock in clients:
                    del clients[sock]

def handle_message(sock, msg):
    data = clients[sock]
    msg_type = msg.get("type")

    if msg_type == "join":
        username = msg.get("username", "Anonymous")
        data.username = username
        print(f"User '{username}' joined from {sock.getpeername()}")
       
        join_ack = json.dumps({"type": "join_ack", "message": f"Welcome, {username}"})
        data.outb += (join_ack + '\n').encode()
        
        join_msg = json.dumps({"type": "join", "username": username})
        broadcast(sock, join_msg)
    elif msg_type == "move":
        move = msg.get("move", "")
        username = data.username
        print(f"User '{username}' made a move: {move}")
        
        move_msg = json.dumps({"type": "move", "username": username, "move": move})
        broadcast(sock, move_msg)
    elif msg_type == "chat":
        chat_message = msg.get("message", "")
        username = data.username
        print(f"User '{username}' says: {chat_message}")
        
        chat_msg = json.dumps({"type": "chat", "username": username, "message": chat_message})
        broadcast(sock, chat_msg)
    elif msg_type == "quit":
        username = data.username
        print(f"User '{username}' quit")
       
        quit_msg = json.dumps({"type": "quit", "username": username})
        broadcast(sock, quit_msg)
        sel.unregister(sock)
        sock.close()
        del clients[sock]
    else:
        print(f"Unknown message type received from {data.addr}: {msg_type}")

def main():
    host = '0.0.0.0'  
    port = 12345

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print("Server listening on", (host, port))
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
