#!/bin/bash
if [ $# -eq 0 ]; then
    echo "No arguments supplied. Correct syntax: $> listen [80|443]"
    exit 3
fi

if [[ ! $1 =~ ^-?[0-9]+$ ]]; then
    echo "Parameter must be an integer";
    exit 2
fi

if [ $1 -ne 443 ] && [ $1 -ne 80 ]; then
    echo "Port number must be either 80 or 443"
    exit 1
fi

ln -sf /etc/nginx/default-$1.conf /etc/nginx/conf.d/default.conf
nginx -s reload
sleep 2
