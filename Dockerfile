FROM python:3.10-alpine3.17 as builder

# set the working dir for docker
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add --no-cache postgresql-dev gcc g++ subversion python3-dev musl-dev libffi-dev

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY /QuizGeneratorModel/requirements.txt .
RUN pip install numpy==1.25.0 --prefer-binary
RUN ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install --upgrade numpy
RUN pip install -Ur ./requirements.txt --prefer-binary

COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

COPY .. .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]