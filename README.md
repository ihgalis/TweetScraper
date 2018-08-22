# Introduction #
`TweetScraper` can get tweets from [Twitter Search](https://twitter.com/search-home). 
It is built on [Scrapy](http://scrapy.org/) without using [Twitter's APIs](https://dev.twitter.com/rest/public).
The crawled data is not as *clean* as the one obtained by the APIs, but the benefits are you can get rid of the API's rate limits and restrictions. Ideally, you can get all the data from Twitter Search.

**WARNING:** please be polite and follow the [crawler's politeness policy](https://en.wikipedia.org/wiki/Web_crawler#Politeness_policy).
 

# Installation #
It requires [Scrapy](http://scrapy.org/) and [PyMongo](https://api.mongodb.org/python/current/) (Also install [MongoDB](https://www.mongodb.org/) if you want to save the data to database). Setting up:

    $ git clone https://github.com/ihgalis/TweetScraper.git
    $ cd TweetScraper/
    $ pip install -r requirements.txt  #add '--user' if you are not root
	$ scrapy list
	$ #If the output is 'TweetScraper', then you are ready to go.

# Usage #

1. Change the `USER_AGENT` in `TweetScraper/settings.py` to identify who you are
	
		USER_AGENT = 'your website/e-mail'
		
2. In the root folder of this project, run command like: 

		scrapy crawl TweetScraper -a query="foo,#bar"

	where `query` is a list of keywords seperated by comma and quoted by `"`. The query can be any thing (keyword, hashtag, etc.) you want to search in [Twitter Search](https://twitter.com/search-home). `TweetScraper` will crawl the search results of the query and save the tweet content and user information. You can also use the following operators in each query (from [Twitter Search](https://twitter.com/search-home)):
	
	| Operator | Finds tweets... |
	| --- | --- |
	| twitter search | containing both "twitter" and "search". This is the default operator. |
	| **"** happy hour **"** | containing the exact phrase "happy hour". |
	| love **OR** hate | containing either "love" or "hate" (or both). |
	| beer **-** root | containing "beer" but not "root". |
	| **#** haiku | containing the hashtag "haiku". |
	| **from:** alexiskold | sent from person "alexiskold". |
	| **to:** techcrunch | sent to person "techcrunch". |
	| **@** mashable | referencing person "mashable". |
	| "happy hour" **near:** "san francisco" | containing the exact phrase "happy hour" and sent near "san francisco". |
	| **near:** NYC **within:** 15mi | sent within 15 miles of "NYC". |
	| superhero **since:** 2010-12-27 | containing "superhero" and sent since date "2010-12-27" (year-month-day). |
	| ftw **until:** 2010-12-27 | containing "ftw" and sent up to date "2010-12-27". |
	| movie -scary **:)** | containing "movie", but not "scary", and with a positive attitude. |
	| flight **:(** | containing "flight" and with a negative attitude. |
	| traffic **?** | containing "traffic" and asking a question. |
	| hilarious **filter:links** | containing "hilarious" and linking to URLs. |
	| news **source:twitterfeed** | containing "news" and entered via TwitterFeed |

3. The tweets will be saved to disk in `./Data/tweet/` in default settings and `./Data/user/` is for user data. The file format is JSON. Change the `SAVE_TWEET_PATH` and `SAVE_USER_PATH` in `TweetScraper/settings.py` if you want another location.

4.  In you want to save the data to MongoDB, change the `ITEM_PIPELINES` in `TweetScraper/settings.py` from `TweetScraper.pipelines.SaveToFilePipeline` to `TweetScraper.pipelines.SaveToMongoPipeline`.

### Other parameters
* `lang[DEFAULT='']` allow to choose the language of tweet scrapped. This is not part of the query parameters, it is a different part in the search API URL
* `top_tweet[DEFAULT=False]`, if you want to query only top_tweets or all of them
* `crawl_user[DEFAULT=False]`, if you want to crawl users, author's of tweets in the same time

E.g.: `scrapy crawl TweetScraper -a query=foo -a crawl_user=True`

# Usage with Docker (simple) #
Before you start through the entire setup process think about where you want to store the data. This fork is designed that you go straight ahead with MongoDB and Docker. You can start the crawler directly or within a Docker container.

For the purpose of a Docker container I have created a Dockerfile which can be used to build your own Image.

## Install Docker

If you have Docker already I advise you to use portainer.io for a simpler usage of docker. Of course you can go by commandline interfaces but portainer.io helps you maybe to understand more and better. (https://portainer.io/install.html)

    docker volume create portainer_data
    docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer

1. Windows

Download and install the community edition: https://store.docker.com/editions/community/docker-ce-desktop-windows   

2. Linux (Ubuntu 16.04)

    sudo apt-get update
    sudo apt-get install docker-ce
    
    # verify your installation
    sudo docker run hello-world

3. Mac

Download and install the community edition: https://store.docker.com/editions/community/docker-ce-desktop-mac

## Build your Image

        cd /to/your/project/
        docker build -t tweetscrape .
        
## Start the scraper inside docker

        docker run -d \
        --name tweet_scraper \
        -v /path/on/your/host/with/gitclone:/home/tweetscraper/ \
        tweetscraper:latest \
        scrapy crawl TweetScraper -a query="example #fun"
        
If you want to debug your container just delete the -d from your command and see it's output in your console.

# Usage with Docker (automatic) #
I have created a couple of automatisms which allow you to make bulk searches and save the results to your
desired destination. Nothing has to be started directly inside of a container!

1. Build the template image (Docker Node)

        cd /to/your/project/
        docker build -t tweetscraper_alpine .
        
2. Start your scraping job (Docker Node)

        python tweetscraper_bootstrap.py -h

## Basic Scrape ##
* The most basic search is to use your own keyword combinations

        python tweetscraper_bootstrap.py \
        -v \                            # verbose mode
        -n my_own_twitter_scrape \      # container name (part of it)
        -q "nasa filter:links" \        # search for "nasa" related tweets but only with links containing
        -vol /path/to/hose/src          # docker volume binding
        
## Based on Large German Cities ##
* Search for keywords within multiple large german cities

        python tweetscraper_bootstrap.py \
        -v \                            # verbose mode
        -n keyword_large_de_city \      # container name (part of it)
        --querymode near_xl_de_city \   # indicates the type of search (multiple large cities in germany)
        -k keyword \                    # the keyword you want to search for
        -vol /path/to/src/on/host       # docker volume binding

What will hapen now is that there will be started a couple of docker containers which will be automatically be deleted after they finish their work. All crawlers will be started with the necessary parameters without you having to interfere with them.

You can also use **-k** multiple times to use **more keywords**. 

## Based on Popular Dating Keywords (english) ##
* Find tweets based on popular dating keywords (english)

        python tweetscraper_bootstrap.py \
        -v \
        -n dating_keywords_english \
        --querymode dating_keywords_en \
        -vol /path/to/src/on/host
        
This will only trigger the keywords in a specific list. Although you can do more to filter by adding arguments.

   | Argument | Consequence |
   | --- | --- |
   | --sentiment positive | adds the ":)" string to the search parameter to find only positive mentions |
   | --sentiment negative | adds the ":(" string which will give you negative mentions  |
   | --filter links | finds tweets which are linking to URLs. Must not be only "links"" |
   | --question | adds the "?" string to your search query and finds tweets containing questions |
   | --source twitterfeed | indicates that you want only tweets which came from TwitterFeed, but this can be different |
   | --near Berlin | filters your results to geogrpahical points like Berlin |
   | --within 15mi | filters your results to a 15 miles radius around the geographical point specified in 'near* |
   | --since 2016-08-08 | only looks at tweets where the oldest are from the specified date |
   | --until 2017-09-07 | only looks at tweets where the newest are from the speicified date  |

## Examples ##

This one findes positive tweets about all dating keywords. Keyword by keyword, everyone in its docker container.

    python tweetscraper_bootstrap.py \
        -v \
        -n dating_keywords_english \
        --querymode dating_keywords_en \
        -vol /path/to/src/on/host \
        --sentiment positive 
        
# Acknowledgement #
Keeping the crawler up to date requires continuous efforts, we thank all the [contributors](https://github.com/jonbakerfish/TweetScraper/graphs/contributors) for their valuable work.

And thank you [Daniel Guerra](https://hub.docker.com/r/danielguerra/alpine-scrapy/) for the base docker image with alpine I found to be useful for this project.

# License #
TweetScraper is released under the [GNU GENERAL PUBLIC LICENSE, Version 2](https://github.com/jonbakerfish/TweetScraper/blob/master/LICENSE)
