# Makefile for the audio controller

CC=gcc
CFLAGS=-c 
LIBS=-lasound -lpthread

all: audio

audio: audio_controller.o buffer.o comms.o sound.o
	$(CC) audio_controller.o buffer.o comms.o sound.o -o audio $(LIBS) 

audio_controller.o: audio_controller.c
	$(CC) $(CFLAGS) audio_controller.c

buffer.o: buffer.c
	$(CC) $(CFLAGS) buffer.c

comms.o: comms.c
	$(CC) $(CFLAGS) comms.c

sound.o: sound.c
	$(CC) $(CFLAGS) sound.c

clean: rm *o audio
