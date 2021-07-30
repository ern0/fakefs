#!/bin/bash

fusermount -u /tmp/fake 2> /dev/null
mkdir -p /tmp/fake

#bash -c "sleep 0.5; ls -l /tmp/fake/media"

./fakefs.py / /mnt/fake fakefs.conf
