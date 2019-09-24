Project 3: Client and authenticated DNS server
==============================================

Overview
--------

The goal of this project is to extend the DNS system from project 2 to
incorporate authentication of the DNS server that responds to client queries.

In project 3, you will change the root server from project 2, RS, into an
**authentication server** (AS) that authenticates exactly one of two top-level
domain servers, TS1 and TS2, for each client query. Only the TLD servers store
mappings between hostnames and IP addresses; the AS does not. The AS runs a
challenge-response protocol with the TS servers (detailed below), thereby
choosing exactly one of TS1 or TS2 for each client query. Based on this result
from the AS, the client must connect directly with TS1 or TS2, querying the IP
address for the desired hostname. Overall, you will have four programs: the
client, the AS, and two DNS servers (TS1 and TS2).

The DNS client program maintains two secret but shared keys, one shared each
with TS1 and TS2. For each query, the client uses one of its keys and a
challenge string to create a digest and sends the challenge string as well as
the digest to the authentication server (AS). The AS sends ONLY the challenge
string to both the TS servers. The TS servers each use their corresponding
shared key and the challenge string to obtain a digest, and send their
respective digests to AS. Exactly one of these digests matches the digest sent
by the client to the AS. We consider the corresponding TS authenticated for this
query. The AS sends the hostname of the authenticated TS server to the
client. The client then connects to that TS server, sending the queried Hostname
and obtaining an A record (if found) or an error.

Some more details
-----------------

Suppose the client maintains two shared secret keys, "k1234" (with TS1) and
"k5678" (with TS2). Each Hostname queried by the client is specified along with
a key and a challenge string. An example query input looks like the following:

k5678 foxtrot www.princeton.edu

Using the key and the challenge, the client creates a digest, for example, using
the following lines of code (adapt these lines appropriately for your solution):

import hmac

# test case 1. In your project, you will read test cases from an input file.
key_query1 = "k5678"
challenge_query1 = "foxtrot"
query1 = "www.princeton.edu"

# Generate a digest for the challenge
digest_query1 = hmac.new(key_query1.encode("utf-8"), challenge_query1.encode("utf-8"))
print digest_query1.hexdigest()

The client then sends ONLY the challenge string and generated digest to the AS
(**NOT the queried Hostname**). Here is a sample line that the AS receives from
the client:

foxtrot 83cdae16a693560b34bac1f64b7cf10a

Here is a sample line that the AS sends to both TS1 and TS2 (**it does NOT
include the digest**):

foxtrot

The two TS servers each maintain a key which is used to create a digest from the
challenge. In our running example, that key is either "k1234" or "k5678". Here
are two sample responses from TS1 and TS2:

83cdae16a693560b34bac1f64b7cf10a
# from ts1.edu

60f30e6935a8476d8277d465500fd38f
# from ts2.edu

Once AS receives the two digests from TS1 and TS2, it compares them with the
client's digest. Exactly one of the TS digests will match with that of the
client. We consider this matching TS to be the TS authenticated for this
query. The AS returns the hostname of the authenticated TS back to the
client. For the example above, the AS will return the string

ts1.edu

to the client. The AS must send exactly ONE TS hostname (ex: ts1.edu) back to
the client for each query. The client then uses the returned hostname, ts1.edu,
to make a connection to the authenticated TS program. The client sends the
queried Hostname as a string (www.princeton.edu) over that connection.

The two TS programs each maintain a DNS_table consisting of three fields:

- Hostname
- IP address
- Flag (A only; no NS)

The authenticated TS server does a lookup in its DNS_table, and if there is a
match, sends the DNS table entry as a string:

Hostname IPaddress A

If the Hostname isn't found, the authenticated TS server returns

Hostname - Error:HOST NOT FOUND

The client directly prints the output it receives from the authenticated TS
server.

The client must NOT send a queried Hostname to the TS server that did not
authenticate successfully through the challenge issued for that query. 

To summarize, the client maintains three connections: one with the AS, and two
with the TS servers. The AS maintains two connections, one with each TS.

Note that all DNS lookups are case-insensitive. If there is a hit in the local
DNS table, the server programs must respond with the version of the string that
is in their local DNS table.

How we will test your programs
------------------------------

As part of your submission, you will turn in four programs: as.py, ts1.py,
ts2.py, and client.py, and one README file (more on this below). We will be
running the four programs on the ilab machines with Python 2.7.

Please do not assume that all programs will run on the same machine or that all
connections are made to the local host.  We reserve the right to test your
programs with local and remote socket connections, for example with client.py,
ts1.py, ts2.py, and as.py each running on a different machine. You are welcome
to simplify the initial development and debugging of your project and get off
the ground by running all programs on one machine first. However, you must
eventually ensure that the programs can work across multiple machines.

The programs must work with the following command lines:

python ts1.py ts1ListenPort_a ts1ListenPort_c
python ts2.py ts2ListenPort_a ts2ListenPort_c
python as.py asListenPort ts1Hostname ts1ListenPort_a ts2Hostname ts2ListenPort_a
python client.py asHostname asListenPort ts1ListenPort_c ts2ListenPort_c

Here:

- ts1ListenPort_a and ts2ListenPort_a are ports accepting incoming connections
  at TS1 and TS2 (resp.) from the AS;
- ts1ListenPort_c and ts2ListenPort_c are ports accepting incoming connections
  at TS1 and TS2 (resp.) from the client;
- asListenPort is a port accepting incoming connections from the client at AS;
- asHostname, ts1Hostname, and ts2Hostname are the hostnames of the machines
  running AS, TS1, and TS2 (resp.).

Note that the hostnames for TS1 and TS2 will be provided to the client by the
AS; these hostnames are not included in the arguments provided to the client.

The queried hostname strings along with keys and challenges will be given one
per line in a file PROJ3-HNS.txt.

The shared keys, one line per file, will be in the files named PROJ3-KEY1.txt
and PROJ3-KEY2.txt. Each TS reads exactly one of them: TS1 reads key1 and TS2
reads key2.

Note that the client does not need to read the PROJ3-KEY files since the keys
are provided alongside the queried Hostnames in PROJ3-HNS.txt. We will ensure
that the keys provided with queries match the keys shared with either TS1 or
TS2.

The entries in the DNS tables (one each for TS1 and TS2) will be strings with
fields separated by spaces. There will be one entry per line. You can see the
format in PROJ3-DNSTS1.txt and PROJ3-DNSTS2.txt. Your server programs should
populate the DNS table by reading the entries from the corresponding files.

Your client program should output the results to a file RESOLVED.txt, with one
line per result.

See the samples attached in this folder.

We will test your programs by running them with the hostnames, tables, and keys
in the attached input files (*.txt) as well as with new hostnames, table
configurations, and keys. You will be graded based on the outputs in
RESOLVED.txt. Your programs should not crash on correct inputs.

README file
-----------

In addition to your programs, you must also submit a README file with clearly
dilenated sections for the following.

0. Please write down the full names and netids of all your team members.
1. Briefly discuss how you implemented the challenge-response functionality and
   the authenticated DNS query.
2. Are there known issues or functions that aren't working currently in your
   attached code? If so, explain.
3. What problems did you face developing code for this project?
4. What did you learn by working on this project?

Submission
----------

Turn in your project on Sakai assignments. Only one team member needs to
submit. Please upload a single zip file consisting of client.py, as.py,
ts1.py, ts2.py, and README.

Some notes and tips
-------------------

As before, run your programs by first starting the TS programs, then the AS
program, and finally the client program. Brief sketches of the interactions
among the programs is attached in this folder.

DNS lookups are case-insensitive.

It is okay to assume that each DNS entry or hostname is smaller than 200
characters.

START EARLY to allow plenty of time for questions on Piazza should you run into
difficulties.
