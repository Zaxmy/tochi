#!/bin/bash
# Generate a passphrase
openssl rand -base64 48 > passphrase.txt

# Generate a Private Key
openssl genrsa -aes128 -passout file:passphrase.txt -out server.key 2048

# Generate a CSR (Certificate Signing Request)
openssl req -new -passin file:passphrase.txt -key server.key -out server.csr \
    -subj "/C=JZ/O=zaxmy/OU=Domain Control Validated/CN=*.zaxmy.com"

# Remove Passphrase from Key
cp server.key server.key.org
openssl rsa -in server.key.org -passin file:passphrase.txt -out server.key
rm  server.key.org passphrase.txt
# Generating a Self-Signed Certificate for 100 years
openssl x509 -req -days 36500 -in server.csr -signkey server.key -out server.crt
rm server.csr
mv server.crt ssl.crt
mv server.key ssl.key
