Steps to Run
============

### Have Python 3.6.0

If on Ubuntu 16.04 (this installs release candidate 1)

```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6
```

If on Ubuntu 16.10:

```
sudo apt install python3.6
```


### (Required) Setup Virtual Environment

```
virtualenv -p python3.6 env
source env/bin/activate
```

### Setup requirements

```
pip install -r requirements.txt
```

### Settings

Modify `settings.json` to match the environment

### Run

Run Sleipnir with `python server.py`
