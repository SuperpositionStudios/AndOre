Steps to Run
============

1. 

Have Python 3.6.0

(If on Ubuntu 16.04):

```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
sudo apt-get install python3.6
```

2. (Optional)

Setup Virtual Environment

```
virtualenv -p python3.6 env
source env/bin/activate
```

3. 

Setup requirements

```
pip install -r requirements.txt
```

4. Settings

Modify `settings.json` to match the environment

Modify the logging level to your likings in `ws_node.py`

5.

To start a region, simple run it with `python Start.{region_name}.Node.py`

Example: `python Start.Scipio.Node.py`
