#!/usr/bin/env python3


import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

def create_message():
    message = ""
    if len(sys.argv) < 2:
        print("usage:", sys.argv[0], "<message>")
        sys.exit(1)
    message = sys.argv[1]
    return message

messages = create_message()

# this routine is called to create each of the many ECHO CLIENTs we want to create

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print("starting connection", connid, "to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages,
            outb=b"",
        )
        sel.register(sock, events, data=data)

# this routine is called when a client triggers a read or write event

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection 1")
            data.recv_total = data.msg_total
        if not recv_data or data.recv_total == data.msg_total:
            print("closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages
        if data.outb:
            print("sending", repr(data.outb), "to connection 1")
            sent = sock.send(bytes(data.outb,'utf-8')) # Should be ready to write
            data.outb = data.outb[sent:]



# main program

host = '0.0.0.0'   # localhost; use 0.0.0.0 if you want to communicate across machines in a real network
port = 12358         # I just love fibonacci numbers
num_conns = 2       # you can change this to however many clients you want to create


start_connections(host, port, num_conns)

# the event loop

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
                sel.get_map()
                break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()