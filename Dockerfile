FROM fkrull/multi-python:focal

COPY . /usr/src
WORKDIR /usr/src

ENV PATH=/root/.local/bin:$PATH
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry self update 1.1.12
RUN poetry config virtualenvs.create false
RUN python3 -m pip install --upgrade pip==22.0.4
RUN poetry install -vvv