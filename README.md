Simple exchange
===============

The project uses [pipenv](https://github.com/pypa/pipenv). After installing it you can create a new environment:

```
$ pipenv --python 3.6
```

To install the dependencies:

```
pipenv install --dev
```

And start the server:

```
flask run
```

Features
--------

- Support only limit orders. Order are resolved immediately if a matching order exists
- Orders can be partially filled
- Orders and trades are not stored in a database, but exist only in memory.
