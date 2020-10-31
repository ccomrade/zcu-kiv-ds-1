# zcu-kiv-ds-1

This is the first KIV/DS project. It's a distributed application for simulating simple bank account transactions.

Note that this is just a school project without any practical use.

## Architecture

Here's an overview of whole application with all its components:

```
                ┏━━━━━━━━━━━━━━━━━━┓      ┏━━━━━━━━━━━━━━━━━━┓        ┏━━━━━━━━━━━━━━━━━━┓
┏━━━━━━━━┓      ┃    Sequencer     ┃      ┃     Shuffler     ┃        ┃  Bank Server 1   ┃
┃ Client ┃ ━━━❯ ┃                  ┃ ━━━❯ ┃                  ┃ ━━┳━━❯ ┃                  ┃
┗━━━━━━━━┛      ┃  192.168.151.10  ┃      ┃  192.168.151.20  ┃   ┃    ┃  192.168.151.31  ┃
                ┗━━━━━━━━━━━━━━━━━━┛      ┗━━━━━━━━━━━━━━━━━━┛   ┃    ┗━━━━━━━━━━━━━━━━━━┛
                                                                 ┃
                                                                 ┃    ┏━━━━━━━━━━━━━━━━━━┓
                                                                 ┃    ┃  Bank Server 2   ┃
                                                                 ┣━━❯ ┃                  ┃
                                                                 ┃    ┃  192.168.151.32  ┃
                                                                 ┃    ┗━━━━━━━━━━━━━━━━━━┛
                                                                 ┃
                                                                 ┃    ┏━━━━━━━━━━━━━━━━━━┓
                                                                 ┃    ┃  Bank Server 3   ┃
                                                                 ┣━━❯ ┃                  ┃
                                                                 ┃    ┃  192.168.151.33  ┃
                                                                 ┃    ┗━━━━━━━━━━━━━━━━━━┛
                                                                 ┃
                                                                 ┃    ┏━━━━━━━━━━━━━━━━━━┓
                                                                 ┃    ┃  Bank Server 4   ┃
                                                                 ┗━━❯ ┃                  ┃
                                                                      ┃  192.168.151.34  ┃
                                                                      ┗━━━━━━━━━━━━━━━━━━┛
```

The client generates random bank account transactions and sends them to the sequencer. The sequencer assigns an unique
sequence number to each transaction and forwards it to the shuffler. The shuffler changes the order of received transactions
and dispatches them to the bank servers. Each bank server receives all transactions. Finally, the bank servers maintain
a single bank account and commit the received transactions in the correct order. That is, in the same order as the client
sent them.

All communication between application components is done using the REST API with messages in JSON format.

## Implementation

Application components are implemented in Python using:
- Requests HTTP library
- Flask web framework + Waitress WSGI server
- Debian GNU/Linux Buster (current stable)

The infrastructure is built using Vagrant.

## Usage

### Setup

First of all, the infrastructure has to be created. Use the following command to create and run all the VMs.

```
vagrant up
```

### Testing

When the application is up and running, it's time to generate some transactions with the client. The following command
dispatches 20 random transactions. Make sure the `requests` library is installed before running the client.

```
src/client.py 192.168.151.10 20
```

### Verification

To verify that all generated transactions have been successfully committed, you need to query the status of each bank
server. The following command can be used for that. Brace expansion from the Bash shell is used to query all the bank
servers at once.

```
curl http://192.168.151.{31..34}/api/v1/account
```

Here's an example of possible result. All bank servers have the same account balance.

```json
{"balance":4226570,"current_seq":1030,"pending_transactions":0}
{"balance":4226570,"current_seq":1030,"pending_transactions":0}
{"balance":4226570,"current_seq":1030,"pending_transactions":0}
{"balance":4226570,"current_seq":1030,"pending_transactions":0}
```

Note that the results may be incomplete if you query bank server status right after the client finishes sending the
transactions. To avoid that, just wait a few seconds to make sure all active transactions are propagated to the bank
servers.

### Cleanup

Finally, to shut down and remove all the VMs, use the command below.

```
vagrant destroy -f
```
