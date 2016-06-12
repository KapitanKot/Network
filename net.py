#!/usr/bin/env python

import socket
import sys
import getopt
import threading
import subprocess

listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0

def manual():

    print "Sposób użycia: net.py -t tatget -p port"
    print "-l --listen"
    print "-e --execute=file"
    print "-u --upload=destination"
    print
    print "Przykład:"
    print "net.py -t 192.168.0.1 -p 5555 -l -c"
    sys.exit(0)

def main():

    global listen, port, target, execute, command, upload_destination

    if not len(sys.argv[1:]):
        manual()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
        ["help","listen","execute","target","port","command","upload"])

    except getopt.GetoptEror as err:
        print str(err)
        manual()

    for o,a in opts:
        if o in ("-h","--help"):
            manual()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--command"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False, "Nieobsługiwana opcja"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        sender(buffer)

    if listen:
        server_loop()
        
def sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if(len(buffer)):
            client.send(buffer)
        while True:

            recv_len = 1
            response = ""

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            buffer = raw_input("")
            buffer += "\n"

            client.send(buffer)

    except:
        print "[*] Błąd!"
        client.close()
    
def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_command():

    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Nie bangla"

    return output

def client_handler():

    global upload, execute, command

    if len(upload_destination):

        file_buffer = ""

        while True:

            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_desc = open(upload_destination, "wb")
            file_desc.write(flie_buffer)
            file_desc.close()

            client_socket.send("Zapisano plik w %s\r\n" % upload_destination)
        except:
            client_socket.send("Nie udało się zapisać pliku w %s\r\n" % upload_destination)

    if len(execute):

        output = run_command(execute)
        client_socket.send(output)

    if command:

        while True:
            client_socket.send("<NET:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)
            client_socket.send(response)

main()
