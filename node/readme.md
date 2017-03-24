Steps to Run w/ Docker
======================

Assuming you have Docker setup,

```bash
docker run -d -p $external_port:$internal_port -e "node_port=$internal_port" -e "node_key=$node_key" -e "erebus_address=$erebus_address" -e "node_name=$node_name" -e "sleipnir_address=$sleipnir_address" --restart=always jcharante/node
```

Development Example:

```bash
docker run -d -p 7101:80 -e "node_port=80" -e "node_key=testkey" -e "erebus_address=http://192.168.0.13:7004" -e "node_name=Scipio" -e "sleipnir_address=ws://192.168.0.13:7100/node" -e "public_address=ws://0.0.0.0:7101" --name=Scipio --restart=always jcharante/node
```

Production Example:



Steps to Run w/o Docker
=======================

1. 

Have Python 3.6.0

If on Ubuntu 16.04: `$ sudo add-apt-repository ppa:jonathonf/python-3.6`

Then on Ubuntu >= 16.04:
```bash
$ sudo apt update
$ sudo apt install python3.6
```

2. (Optional)

Setup Virtual Environment

```bash
virtualenv -p python3.6 .venv
source env/bin/activate
```

3. 

Setup requirements

```bash
pip install -r requirements.txt
```

4.

Set your environmental variables. Here's an example

```bash
export node_port=80  #  type: int
export node_key=testkey  # type: str
export erebus_address=http://0.0.0.0:7004  #type: str
export node_name=Scipio  # type: str
export sleipnir_address=ws://0.0.0.0:7100/node  # type: str
```

Then run the node with `$ python DockerNode.py`
