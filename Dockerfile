FROM python:3.10 as builder

# set the working dir for docker
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql postgresql-contrib gcc g++ subversion \
    python3-dev libffi-dev libssl-dev openssh-client

# create venv and isntall requirements
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY /QuizGeneratorModel/requirements.txt .
RUN pip install -r ./requirements.txt
RUN pip install watchdog

# copy project
COPY . .

# generate keys
# RUN chmod +x ./key_gen.sh
# RUN ./key_gen.sh