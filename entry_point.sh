#!/bin/sh
getent hosts api_git_1
if [ $? -eq 0 ]
then
    ssh-keyscan api_git_1 > /root/.ssh/known_hosts 
else
    echo "api_git_1 is not a known host"
fi
bash -c "$1"
