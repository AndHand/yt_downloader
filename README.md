# YT_Downloader

A simple project a uses Django, yt-dlp, rabbitmq and valkey to create a website for downloading videos from youtube

This project is mainly for exploring how to use rabbitmq, Django and other technologies

The project has multiple parts

## Django Server
Acts as a webserver for the website and the api.
Submits work messages to rabbitmq.

## RabbitMQ worker (worker/worker.py)
Reads messages from rabbitmq and downloads the videos from youtube using the python library yt-dlp.

## Valkey
A simple key-value store for information about the current status of the rabbitmq message queue.
Contains information like id of last submitted job, progress of jobs, and where to find the output file of jobs.
This is used to keep track of the size of the message queue, the queue position of a certain job and other things.
