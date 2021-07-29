#!/bin/bash
clear

MOUNTPOINT=/tmp/fake

fusermount -u $MOUNTPOINT 2> /dev/null

gcc \
	-Isrc \
	src/passthrough.c \
	`pkg-config fuse --cflags --libs` \
	-o fakefs