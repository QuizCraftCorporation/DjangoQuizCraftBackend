FROM python:3.10-alpine3.17 as builder

# set the working dir for docker
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update && apk add --no-cache postgresql-dev gcc g++ subversion \
python3-dev musl-dev libffi-dev openssl openssh-keygen

# create venv and isntall requirements
RUN python3.10 -m venv venv
RUN source venv/bin/activate
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r ./requirements.txt
COPY /QuizGeneratorModel/requirements.txt .
RUN pip install -r ./requirements.txt

# copy project
COPY . .

# generate keys
# RUN chmod +x ./key_gen.sh
# RUN ./key_gen.sh