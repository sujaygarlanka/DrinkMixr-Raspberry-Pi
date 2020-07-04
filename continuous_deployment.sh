#!/bin/bash
python3 main.py &
while true
do
    REMOTE_STATUS=$(git remote update && git status)
    if [[ $REMOTE_STATUS == *"behind"* ]];
    then
        git pull
        killall python3
        python3 main.py &
    fi
    sleep 1
done