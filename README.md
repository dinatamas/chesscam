chesscam
========

> dinatamaspal | 21st December, 2021

chesscam is a computer vision application that detects a
chessboard on a video feed and follows the moves made.

Instructions
------------

* `virtualenv venv`
* `source venv/bin/activate.fish`
* `pip install -r requirements.txt -c constraints.txt`
* `pip freeze > constraints.txt`
* `./chesscam.py --help`
* `deactivate`

Note for Wayland users
----------------------

Please export `QT_QPA_PLATFORM=xcb` before execution.
