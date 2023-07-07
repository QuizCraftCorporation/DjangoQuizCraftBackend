# RS KEY GENERATION PART
# generate private key if not exists
if [[ ! -f "${PRIVATE_KEY_PATH:-jwtRS256.key}" ]]; then
  ssh-keygen -t rsa -b 4096 -m PEM -f ${PRIVATE_KEY_PATH:-jwtRS256.key} -N ${RS_PASSPHRASE:-""}
fi

# generate public ket if not exists
if [[ ! -f "${PRIVATE_KEY_PATH:-jwtRS256.key}.pub" ]]; then
  openssl rsa -in ${PRIVATE_KEY_PATH:-jwtRS256.key} -pubout -outform PEM -out ${PRIVATE_KEY_PATH:-jwtRS256.key}.pub
fi

# DJANGO KEY GENERATION PART
# create and activate venv
python3 -m venv venv
source ./venv/bin/activate
# installing django for key generation
pip install django
# running script for django secret key generation
echo "Put this secret key to env variables file in config folder (SECRET_KEY):"
python $(dirname "$0")/get_secret_key.py