# Alexsandr Vobornov
import threading
import time
import random
import sys
import socket
import hmac

# Table loaded from DNSTS2 file
dns_table = dict()
key = ""


# Make sure port entered is valid
def test_port(port):
    try:
        port = int(port)
        if 1 <= port <= 65535:
            return port
        else:
            raise ValueError
    except ValueError:
        print("Error: Illegal port number")
        exit()


# Populate dns_table and key
def populate_dns_key():
    global dns_table, key
    try:
        file_names = ["PROJ3-DNSTS2.txt", "PROJ3-KEY2.txt"]
        file = open(file_names[0], "r")
        for line in file:
            temp_line = line.split()
            hostname = temp_line[0].lower()
            ip = temp_line[1]
            flag = temp_line[2]
            dns_table[hostname] = [ip, flag]
        file.close()

        file = open(file_names[1], "r")
        key = file.readline().lower().rstrip()
    except IOError:
        print("[TS2]: Error. File {} not found".format(file.name))
        exit()
    finally:
        file.close()


# Check to see if host is in DNS table and respond accordingly
def process_dns_query(hostname):
    if hostname in dns_table:
        ip = dns_table[hostname][0]
        flag = dns_table[hostname][1]
        return hostname + " " + ip + " " + flag
    else:
        return hostname + " - " + "Error:HOSTNOTFOUND"


# Process the challenge sent by AS server and use key to return digest
def process_AS_query(data):
    print(key, str(data.rstrip()))
    digest = hmac.new(key.encode('utf-8'), str(data.rstrip()).encode('utf-8'))
    print(digest.hexdigest())
    return digest.hexdigest()


# Run server that connects to authentication server
def server_AS(port):
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[TS2_AS]: TS Server socket for AS created")
        server_binding = ('', port)
        ss.bind(server_binding)
        ss.listen(1)
        host = socket.gethostname()
        print("[TS2_AS]: Server host name is: {}".format(host))
        host_ip = (socket.gethostbyname(host))
        print("[TS2_AS]: Server IP address is: {}".format(host_ip))
        print("[TS2_AS]: Server port is: {}".format(port))
    except socket.error as err:
        print('[TS2_AS]: Socket open error: {}\n'.format(err))
        exit()

    while True:
        as_server, address = ss.accept()
        print("[TS2_AS]: Got a connection request from as_server {}".format(address))
        try:
            # Receive challenge + digest from the as_server
            data_from_as_server = as_server.recv(200).decode('utf-8')
            # Continous processing of data from as_server
            while data_from_as_server or 0:
                # Send data to as_server
                data = process_AS_query(data_from_as_server)
                print("[TS2_AS]: as_server sent {} | Sending {} to as_server {}".format(data_from_as_server, data,
                                                                                        address))
                as_server.send(data.encode('utf-8'))
                # Wait for more data from as_server
                data_from_as_server = as_server.recv(200).decode('utf-8')
            else:
                as_server.close()
        except socket.error as err:
            as_server.close()
            print(err.args, err.message)


# Run server that connects to client
def server_client(port):
    # connect to Client
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[TS2_C]: TS Server socket for Client created")
        server_binding = ('localhost', port)
        ss.bind(server_binding)
        ss.listen(1)
        host = socket.gethostname()
        print("[TS2_C]: Server host name is: {}".format(host))
        host_ip = (socket.gethostbyname(host))
        print("[TS2_C]: Server IP address is: {}".format(host_ip))
        print("[TS2_C]: Server port is: {}".format(port))
    except socket.error as err:
        print('[TS2_C]: Socket open error: {}\n'.format(err))
        exit()

    while True:
        client, address = ss.accept()
        print("[TS2_C]: Got a connection request from client {}".format(address))
        try:
            # Receive data/hostname from the client
            data_from_client = client.recv(200).decode('utf-8')
            # Continous processing of data from client
            while data_from_client or 0:
                # Send data to client
                data = process_dns_query(data_from_client)
                print("[TS2_C]: client sent {} | Sending {} to client {}".format(data_from_client, data, address))
                client.send(data.encode('utf-8'))
                # Wait for more data from client
                data_from_client = client.recv(200).decode('utf-8')
            else:
                client.close()
        except socket.error as err:
            client.close()
            ss.close()
            print(err.args, err.message)


if __name__ == "__main__":
    populate_dns_key()

    if len(sys.argv) != 3:
        print("Error.\n Syntax: python ts2.py ts2ListenPort_a ts2ListenPort_c")
        exit()

    ts2ListenPort_a = test_port(sys.argv[1])
    ts2ListenPort_c = test_port(sys.argv[2])

    populate_dns_key()

    t1 = threading.Thread(name='server_AS', target=server_AS, args=(ts2ListenPort_a,))
    t1.start()
    t2 = threading.Thread(name='server_client', target=server_client, args=(ts2ListenPort_c,))
    t2.start()
