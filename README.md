watchit-monitor
===============

Real time logging monitor built with tornado, websockets and pika. Also including other cool stuff.

Requirements
------------

Aside from the required python modules listed in `watchit-monitor/requirements`,
you will need these:

* python 2.7
* rabbitmq server

Setup
-----

```bash
shell> cd watchit-monitor
shell> virtualenv env
shell> pwd > env/lib/python2.7/site-packages/project.pth
shell> source env/bin/activate
shell> pip install -r requirements # alternatively: pip install requirements.pybundle
shell> echo 'from .default import *' > config/local.py
shell> editor config/local.py # setup for your environment (rabbitmq, etc)
```

Run
---

Make sure you set your RabbitMQ server in `config/local.py` and it is running.
Start the tornado server.

```bash
shell> cd watchit-monitor
shell> virtualenv env
shell> source env/bin/activate
shell> ./bin/server.py
```

Open your browser and open `http://localhost:8888/`.
Create some logging messages with `./bin/genlogs.py`

```bash
shell> cd watchit-monitor
shell> virtualenv env
shell> source env/bin/activate
shell> ./bin/genlogs.py -h
```

Watch the logging messages appear in your browser :)
