watchit-monitor
===============

Real time logging monitor built with tornado, websockets and pika. Also including other cool stuff.

Requirements
------------

* python 2.7
* rabbitmq server

Setup
-----

```
shell> cd watchit-monitor
shell> virtualenv env
shell> source env/bin/activate
shell> pip install -r requirements
shell> echo 'from .default import *' > config/local.py
shell> editor config/local.py # setup for your environment (rabbitmq, etc)
```

Run
---

Make sure you set your RabbitMQ server in `config/local.py` and it is running.
Start the tornado server.

```
shell> cd watchit-monitor
shell> virtualenv env
shell> source env/bin/activate
shell> ./server.py
```

Open your browser and open `http://localhost:8888/`.
Create some logging messages with `./publish.py`

```
shell> cd watchit-monitor
shell> virtualenv env
shell> source env/bin/activate
shell> ./publish.py
```

Watch the logging messages appear in your browser :)
