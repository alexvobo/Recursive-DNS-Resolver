# Alexsandr Vobornov
import threading
import socket
import sys
import hmac


# Make sure port entered is valid
def test_port(port):
    try:
        port = int(port)
        if 1 <= int(port) <= 65535:
            return port
        else:
            raise ValueError
    except ValueError:
        print("Illegal port number")
        exit()


# Gather list of hostname strings to send to server(s)
def hns_list():
    hostnames = []
    file = open("PROJ3-HNS.txt", "r")
    for line in file:
        temp_line = line.split()
        key = temp_line[0].lower()
        challenge = temp_line[1].lower()
        query = temp_line[2].lower()
        formatted = [key, challenge, query]
        hostnames.append(formatted)
    return hostnames


# Takes string from server(s) and formats for easy access
def process_data(data):
    temp_line = str(data).split()
    hostname = temp_line[0].lower()
    ip = temp_line[1]
    flag = temp_line[2]
    if flag == "Error:HOSTNOTFOUND":
        flag = "Error:HOST NOT FOUND"
    formatted = hostname + " " + ip + " " + flag
    return formatted


# Writes resolved hosts to file_name
def output_hosts(hosts):
    try:
        file_name = "./RESOLVED.txt"
        file = open(file_name, 'w+')
        for host in hosts:
            file.write("{}\n".format(host))
        file.close()
    except IOError:
        print("[C]: Error writing to {}".format(file_name))
    finally:
        file.close()


# Run Client
def client():
    # Gather fields from terminal
    as_hostname = sys.argv[1]
    as_port = test_port(sys.argv[2])
    ts1_port = test_port(sys.argv[3])
    ts2_port = test_port(sys.argv[4])
    try:
        AS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[C]: Client socket to AS created")
        # Connect to the Authentication Server
        as_addr = socket.gethostbyname(as_hostname)
        as_binding = (as_addr, as_port)
        print("[C]: Connecting to AS host: {} {}".format(as_hostname, as_binding))
        AS.connect(as_binding)
    except socket.error as err:
        print("[C]: Socket open error: {} \n".format(err))
        exit()

    hostnames = hns_list()
    resolved_hosts = []
    # Send message(s) to Authentication Server
    # Host[i][j]: i = line#
    # j = 0: key, j = 1: challenge, j = 2: query
    for host in hostnames:
        digest = hmac.new(host[0].encode("utf-8"), host[1].encode("utf-8"))
        send_to_AS = host[1] + " " + digest.hexdigest()
        print("[C]: Sending {} to AS".format(send_to_AS))
        AS.send(send_to_AS.encode('utf-8'))

        try:
            # Receive hostname and port ID (1 for TS1, 2 for TS2)
            data = AS.recv(200).decode('utf-8')
            print("[C]: Received {} from AS".format(data))

            hostname_portID = data.split()
            ts_hostname = hostname_portID[0]
            if hostname_portID[1] == "1":
                ts_port = ts1_port
            elif hostname_portID[1] == "2":
                ts_port = ts2_port

            try:
                TS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("[C]: Client socket to TS created")
                # Connect to the TS Server
                ts_addr = socket.gethostbyname(ts_hostname)
                ts_binding = (ts_addr, ts_port)
                print("[C]: Connecting to TS host: {} {}".format(ts_hostname, ts_binding))
                TS.connect(ts_binding)
                # Sends query to TS
                TS.send(host[2].encode('utf-8'))
                print("[C]: Sending {} to TS {}".format(host[2], ts_hostname))
                ts_data = process_data(TS.recv(200).decode('utf-8'))
                print("[C]: Received {} from TS {}".format(ts_data, ts_hostname))
                resolved_hosts.append(ts_data)
                TS.close()
                print("[C]: Client socket to TS closed")
            except socket.error as err:
                print("[C]: Socket open error: {} \n".format(err))
                exit()
        except socket.error as err:
            print("[C]: Network error: {} \n".format(err))

    output_hosts(resolved_hosts)
    # Close the as socket
    AS.close()
    print("[C]: Client socket to AS closed")
    exit()


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("[C]: Error.\n \tSyntax: python client.py asHostname asListenPort ts1ListenPort_c ts2ListenPort_c")
        exit()

    t1 = threading.Thread(name='client', target=client)

    t1.start()

    print("Done.")
