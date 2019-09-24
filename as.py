# Alexsandr Vobornov
import threading
import sys
import socket


# Make sure port entered is valid
def test_port(port):
    try:
        port = int(port)
        if 1 <= int(port) <= 65535:
            return port
        else:
            raise ValueError
    except ValueError:
        print("Error: Illegal port number")
        exit()


def process_data(data):
    temp_line = data.split()
    challenge = temp_line[0].lower()
    digest = temp_line[1].lower()
    formatted = [challenge, digest]
    return formatted


def server():
    as_port = test_port(sys.argv[1])
    ts1_hostname = sys.argv[2]
    ts1_port = test_port(sys.argv[3])
    ts2_hostname = sys.argv[4]
    ts2_port = test_port(sys.argv[5])

    # connect to Client
    try:
        clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[AS]: Server socket created")
        server_binding = ('', as_port)
        clientsock.bind(server_binding)
        clientsock.listen(1)
        host = socket.gethostname()
        print("[AS]: Server host name is: {}".format(host))
        host_ip = (socket.gethostbyname(host))
        print("[AS]: Server IP address is: {}".format(host_ip))
    except socket.error as err:
        print('socket open error: {}\n'.format(err))
        exit()

    # connect to TS1
    try:
        ts1sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[AS-TS1]: Client socket to TS1 created")
        ts1_addr = socket.gethostbyname(ts1_hostname)
        ts1_binding = (ts1_addr, ts1_port)
        print("[AS-TS1]: Connecting to TS1 host: {} {}".format(ts1_hostname, ts1_binding))
        ts1sock.connect(ts1_binding)
    except socket.error as err:
        print("[AS-TS1]: socket open error: {} \n".format(err))
        exit()

    # connect to TS2
    try:
        ts2sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[AS-TS2]: Client socket to TS2 created")
        ts2_addr = socket.gethostbyname(ts2_hostname)
        ts2_binding = (ts2_addr, ts2_port)
        print("[AS-TS2]: Connecting to TS1 host: {} {}".format(ts2_hostname, ts2_binding))
        ts2sock.connect(ts2_binding)
    except socket.error as err:
        print("[AS-TS2]: socket open error: {} \n".format(err))
        exit()

    while True:
        client, address = clientsock.accept()
        print("[AS]: Got a connection request from a client at: {}".format(address))
        try:
            # Receive data/hostname from the client
            data_from_client = client.recv(200).decode('utf-8')
            # Continuous processing of data from client
            while data_from_client or 0:
                # Data from client, but formatted
                data = process_data(data_from_client)
                challenge = data[0]
                digest = data[1]
                print("[AS]: Received {}, {} from client".format(challenge, digest))

                # we're going to send challenge to both servers then match up digest
                # Send TS challenge to resolve
                print("[AS]: Sending {} to TS1,TS2".format(challenge))
                ts1sock.send(challenge.encode('utf-8'))
                ts2sock.send(challenge.encode('utf-8'))

                # Receive data from TS
                data_from_ts = dict()
                data_from_ts['ts1'] = ts1sock.recv(200).decode('utf-8')
                data_from_ts['ts2'] = ts2sock.recv(200).decode('utf-8')
                print("[AS]: Received {} from TS1, \n Received {} from TS2".format(data_from_ts['ts1'],
                                                                                   data_from_ts['ts2']))
                # Match digest to proper TS
                # send proper TS hostname to client
                if data_from_ts['ts1'] == digest:
                    print("[AS]: Server sending {} to client {}".format(ts1_hostname, address))
                    msg = ts1_hostname + " 1"
                elif data_from_ts['ts2'] == digest:
                    print("[AS]: Server sending {} to client {}".format(ts2_hostname, address))
                    msg = ts1_hostname + " 2"

                client.send(msg.encode('utf-8'))
                # Wait for more data from client
                data_from_client = client.recv(200).decode('utf-8')
            else:
                # Close the server-client socket
                #ts1sock.close()
                #ts2sock.close()
                client.close()
        except socket.error as err:
            ts1sock.close()
            ts2sock.close()
            client.close()
            print(err.args, err.message)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Error.\n Syntax: python as.py asListenPort ts1Hostname ts1ListenPort_a ts2Hostname ts2ListenPort_a")
        exit()

    t1 = threading.Thread(name='server', target=server)

    t1.start()
