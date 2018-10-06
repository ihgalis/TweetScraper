FROM vtep86/alpine-scrapy-python3

COPY . /home/tweetscraper/
WORKDIR /home/tweetscraper/

RUN pip install -r requirements.txt