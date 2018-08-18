FROM danielguerra/alpine-scrapy

COPY . /home/tweetscraper/
WORKDIR /home/tweetscraper/

RUN pip install -r requirements.txt