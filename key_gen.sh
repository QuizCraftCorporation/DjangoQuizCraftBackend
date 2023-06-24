if [[ ! -f "${PRIVATE_KEY_PATH:-jwtRS256.key}" ]]; then
  ssh-keygen -t rsa -b 4096 -m PEM -f ${PRIVATE_KEY_PATH:-jwtRS256.key} -N ${RS_PASSPHRASE:-""}
fi

if [[ ! -f "${PRIVATE_KEY_PATH:-jwtRS256.key}.pub" ]]; then
  openssl rsa -in ${PRIVATE_KEY_PATH:-jwtRS256.key} -pubout -outform PEM -out ${PRIVATE_KEY_PATH:-jwtRS256.key}.pub
fi


