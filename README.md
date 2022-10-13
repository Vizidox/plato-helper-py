# Plato-Client-Py

Plato-Client-Py is an auxiliary Python client library that provides interaction with our Plato API. 
It is compatible with Python versions 3.7 through 3.9.

## Usage ##

1. Install the library with your preferred dependency manager:
``` shell
pip install plato-client-py
``` 

2. Initialize the Plato Client object with your plato Host and optionally, the maximum number of retries you want 
in case of connection error. The default value for retries is 3.
``` python
plato = PlatoClient(<PLATO_HOST>, <MAX_TRIES>)
```
3. Create a new plato template by using a zipfile with the template data directory structure and assets for Amazon S3, as well as
your new template JSON schema.
``` python
plato = PlatoClient(<PLATO_HOST>)
template = plato.create_template(file_stream=<zip_file>, template_details=<template_schema>)
```
4. You can also fetch all the registered templates and search by tag.
``` python
plato = PlatoClient(<PLATO_HOST>)
template = plato.templates(tags=["tag1", "tag2"])
```

5. For creating a new file using the template you created, you can compose it by sending the intended compose data. There
are some optional parameters you can pass in, such as the mime type of the final file, the number of the page that 
should be printed (in case of a multi-page template), and size of the template.
``` python
plato = PlatoClient(<PLATO_HOST>)
file = plato.compose(template_id=<template_id>, 
                     compose_data={"name": "Carlos", "course": "Advanced Python"},
                     mime_type="application/pdf")
```

## Development ##

### Prerequisites ###

- Pyenv
- Python 3.7.2+, up to 3.9 (included)
- Python Poetry
- Docker + Docker-compose

### Setup environment for development ###

1. Setup a Python version on your local environment
```shell
pyenv install 3.7.7
pyenv install 3.8.12
pyenv install 3.9.8
pyenv local 3.7.7 3.8.12 3.9.8
``` 
2. Install dependencies
```shell
poetry install
``` 

### Running the tests ###

A Tox configuration has been created, which runs all the tests in the compatible Python versions, linter and type 
checking for you. To do so, run:
```shell
tox -p
``` 
Feel free to add '-v' for more verbose logs while running the tests.

However, if you want to run any of these configurations individually, for ease of debugging, then use the following commands:
* Unit tests, and to check coverage:
```shell
coverage run --source=plato_client_py -m unittest
coverage report
``` 
* Mypy:
```shell
mypy --config-file conf/mypy.ini plato_client_py
```
* Pylint:
```shell
pylint --rcfile=conf/.pylintrc plato_client_py
```

Finally, if you just want to run the tests within a docker container, without setting up the local environment, run 
the following command. However, bear in mind that the docker process changes the ownership of the plato_client_py/coverage 
directory and the .coverage file to root. As such, they will not be modifiable without root access and any subsequent 
tox command will fail. Just delete both with sudo to proceed as usual.
```shell
docker-compose build
docker-compose run --rm plato-client
```

## Authors ##

* **Tiago Santos** - *Initial work* - [Vizidox](https://vizidox.com)
* **Joana Teixeira** - *Additional work* - [Vizidox](https://vizidox.com)
* **Rita Mariquitos** - *Additional work* - [Vizidox](https://vizidox.com)


