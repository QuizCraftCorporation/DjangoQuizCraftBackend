#!/usr/bin/env bash
BASEDIR=$(pwd)

openssl rand -base64 512 | tr -d '/+=\n' | head -c256 > "${BASEDIR}/secrets/redis-password.txt"
openssl rand -base64 512 | tr -d '/+=\n' | head -c256 > "${BASEDIR}/secrets/postgres-password.txt"
# openssl rand -base64 512 | tr -d '/+=\n' | head -c256 > "${BASEDIR}/secrets/rabbitmq-password.txt"