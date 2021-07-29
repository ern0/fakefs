#!/bin/bash

fusermount -u /tmp/fake 2> /dev/null
mkdir -p /tmp/fake

./fakefs.py . /tmp/fake fakefs.conf
