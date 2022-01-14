#!/usr/bin/env python3

import os

os.system('curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -')
os.system('$HOME/.poetry/bin/poetry add cyclonedx-bom')
os.system('$HOME/.poetry/bin/poetry export -f requirements.txt --output requirements.txt')
os.system('rm bom.xml')
os.system('$HOME/.poetry/bin/poetry run cyclonedx-py -e -o bom.xml')
