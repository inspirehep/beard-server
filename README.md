# beard-server

Beard as RESTful API and Celery service.

## Instalation
`beard-server` uses `Bower` to install dependencies of the assets (JavaScript and CSS files).

```shell
npm install -g bower
```

However if you do not want to install `Bower`, run `./build_assets.sh` script after installation steps listed below.
The script runs `npm install` and moves all the dependencies to the correct directory.

To install `beard-server` in your `virtualenv` just follow the steps below.
```shell
mkvirtualenv beard-server
cdvirtualenv && mkdir src
cdvirtualenv src
git clone https://github.com/inspirehep/beard-server
cd beard-server
pip install -e .
bower install
```

## Running
Note that the server will be running on port `5000` by default.

```shell
cdvirtualenv src/beard-server/beard_server
python app.py
```

## Notes
* Free software: GPLv2 license
* This is an experimental developer preview release.
