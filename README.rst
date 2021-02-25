=========
LimitLess
=========

This is a platform that allows for scientific discussions and communication.


Development
===========

Preferred way to run LimitLess development instances on your machine is with `Docker <https://www.docker.com/community-edition#/download>`_, which makes it easy to spin up arbitrary number of instances running different code with separate databases and dependencies besides each other.

To start, clone the repository and run ``./dev init`` command in your terminal. This will build necessary docker containers, install python dependencies and initialize the database. After command does its magic, you will be able to start development server using the ``docker-compose up`` command.

After development server starts, visit the ``http://127.0.0.1:8000/`` in your browser to see your Misago installation.

Admin Control Panel is available under the ``http://127.0.0.1:8000/admincp/`` address. To log in to it use ``Admin`` username and ``password`` password.

The ``./dev`` utility implements other features besides the ``init``. Run it without any arguments to get the list of available actions.


Running in development without `dev`
-------------------------------------------

You may skip `./dev init` and setup dev instance manually, running those commands:

1. `docker-compose build` - builds docker containers
2. `docker-compose run --rm limitless python manage.py migrate` - runs migrations
3. `docker-compose run --rm limitless python manage.py createsuperuser` - creates test user
4. `docker-compose up` - starts dev server


Copyright and license
=====================

This project is modified from Misago.

**Misago** - Copyright © 2018 `Rafał Pitoń <http://github.com/rafalp>`_

