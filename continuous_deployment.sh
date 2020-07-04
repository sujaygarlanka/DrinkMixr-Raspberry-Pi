#!/bin/bash
PID = $(python3 main.py &)
while true
do
    REMOTE_STATUS=$(git remote update && git status)
    if [[ $REMOTE_STATUS == *"behind"* ]];
    then
        git pull
        kill -9 $PID
        PID = python3 main.py &
    fi
    sleep 1
done
