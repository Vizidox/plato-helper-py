FROM python:3.7

COPY . .

RUN curl https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py --output get-poetry.py
RUN python get-poetry.py --version 1.0.2
ENV PATH=/root/.poetry/bin:$PATH
RUN poetry config virtualenvs.create false
RUN poetry install -vvv