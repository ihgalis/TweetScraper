FROM ubuntu:18.04

COPY . /home/tweetscraper/
WORKDIR /home/tweetscraper/

RUN apt update
RUN apt install -y python3 python3-pip

RUN pip3 install -r requirements.txt