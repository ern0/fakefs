#!/bin/bash

MOUNTPOINT=/tmp/fake

rm -rf /home/`whoami`/lof
touch /home/`whoami`/lof
bash -c "sleep 1; echo --" &
bash -c "sleep 2; echo lof > $MOUNTPOINT/home/`whoami`/lof" &

mkdir -p $MOUNTPOINT
./fakefs -o debug $MOUNTPOINT
