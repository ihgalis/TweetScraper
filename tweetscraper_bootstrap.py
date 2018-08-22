from exceptions.exceptions import TweetScrapeBootstrapException
from enumerate import TwitterCommand

import logging
import time
import argparse
import docker

# Argparse
parser = argparse.ArgumentParser(description="TweeterScraper Bootstraper for Docker-based fun!")
parser.add_argument('-n', action='store', dest='container_name',
                    help='Name of your Docker container should be different to the others already running.',
                    required=True)
parser.add_argument('-q', action='store', help="You really want to search yourself? Go ahead!")
parser.add_argument('--querymode', help="What do you want to have?")
parser.add_argument('-k', action='append', dest='keyword_col', default=[],
                    help="Some keywords you would like to include.")
parser.add_argument('-v', action="store_true", help="Verbose mode, you know.")
parser.add_argument('-vol', action="store", help="some Docker volume for your code binding")
parser.add_argument('-lp', action="store", help="Custom list path in case you want to make a bulk search for multiple keywords.")

# params for querymode: dating_keywords
parser.add_argument('--question', action="store_true")
parser.add_argument('--sentiment', action="store", dest="sentiments")
parser.add_argument('--person', action="store", dest='persons')
parser.add_argument('--hashtag', action="store", dest="hashtags")
parser.add_argument('--filter', action="store", dest="links")
parser.add_argument('--source', action="store", dest="sources")
parser.add_argument('--near', action="store", dest="near")
parser.add_argument('--within', action="store", dest="radius")
parser.add_argument('--since', action="store", dest="since")
parser.add_argument('--until', action="store", dest="until")

args = parser.parse_args()

# Logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if args.v:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class TweetScrapeBootstrap(object):
    """
    This class gives you the possibility to scrape Twitter in a different way. Thanks to johnbakerfish we do not have to use
    the API but scrape the results by using his scrapy based code. Furthermore this class has been built to make it possible to
    scrape Twitter much faster using docker. There will be created multiple docker container for each scraper needed.
    """

    def __init__(self, search_string=None, name=None, docker_image_name="tweetscraper_alpine:latest"):
        """
        Basic constructor just sets some start values and initializes lists which will be used later for bulk Twitter scrapes.

        :param search_string: The string which will be used to "search" in Twitter
        :param name: Just some identifier (maybe later)
        :param docker_image_name: The name will be used to identify the docker container (part of it)
        """
        self.name = name
        self.separator = " "
        self.search_string = search_string
        self.docker_image_name = docker_image_name

        self.large_german_cities = list()
        self.docker_client = docker.from_env()

        self.read_large_german_cities()

    def read_large_german_cities(self, path=None):
        """
        Reads the list with large Germany cities in order to make bulk Twitter scrapes regarding tweets where you want to
        find something near those cities or within:

        Twitter search string: "party near: Stuttgart", "party near: Hamburg"

        :param path: The path where the file is located, this is somehow standard but you can pick another one
        :return: None
        """

        if path is None:
            logger.debug("Large German Cities: Path not given - Taking standard")
            with open("analyze_data/large_german_cities.txt", encoding='utf-8', mode='r') as file:
                for line in file:
                    self.large_german_cities.append(line.replace("\n", " "))
        else:
            logger.debug("Large German Cities: Path given - "+str(path))
            with open(path, encoding='utf-8', mode='r') as file:
                for line in file:
                    self.large_german_cities.append(line.replace("\n", " "))

    def search(self):
        """
        This method creates the final scrapy command which is needed to start scrapy and finally starts the docker
        container where the scraper will run.

        :return: None
        """

        temp_command = "scrapy crawl TweetScraper -a query=\"" + self.search_string + "\""
        logger.debug("COMMAND: " + str(temp_command))

        if args.vol:

            # the -v configuration for the docker
            docker_volumes = {
                args.vol: {
                    'bind': '/home/tweetscraper/',
                    'mode': 'ro'
                }
            }

            self.docker_client.containers.run(image="tweetscraper_alpine:latest",
                                              auto_remove=True,
                                              detach=True,
                                              name="tweetscraper_"+str(self.docker_image_name)+"_"+str(time.time()),
                                              volumes=docker_volumes,
                                              command=temp_command)
        else:
            temp_command = "scrapy crawl TweetScraper -a query=\"" + self.search_string + "\""
            logger.debug("COMMAND: " + str(temp_command))
            self.docker_client.containers.run(image="tweetscraper_alpine:latest",
                                              auto_remove=True,
                                              detach=True,
                                              name="tweetscraper_" + str(self.docker_image_name) + "_" + str(time.time()),
                                              command=temp_command)

    def search_near_large_german_cities(self, keyword_string):
        """
        This method is triggered when you want to search for a term in relation to large german cities or even within
        the cities themselves. It invokes the search() method multiple times (as much cities as the list has).

        :param keyword_string: the keywords you want to search for (can be more)
        :return: None
        """

        for city in self.large_german_cities:
            self.search_string = keyword_string + "near:" + self.separator + city
            self.search()

    def search_dating_keywords_en(self, sentiment=None, question=None, links=None, source=None, near=None, within=None, since=None, until=None):
        """
        Method takes a lot of parameters which can be used to make a twitter search ore precise. All parameters
        will be taken care of in a way that in case that it is set, the software starts to run corresponding docker
        containers.

        :param sentiment: can be ":)" or ":("
        :param question: can just be set or not
        :param filter: can be set with a word "links" in order to construct "filter:links" which filters for links only.
        :param source: can be set to "twitterfeed" in order to filter for only items entered via TwitterFeed
        :param near: can be added to place some city as the keyword in order to get information about things around cities
        :param within: can be used to define a radius
        :param since: defines some start day when we should enccountter
        :return: None
        """

        dating_keywords = self.read_custom_list("analyze_data/dating_keywords_en.txt")

        # when everything is noen just go ahead
        if sentiment is None and \
            question is False and \
            links is None and \
            source is None and \
            near is None and \
            within is None and \
            since is None:

            self.search_with_symbol(None, dating_keywords)

        if question:
            self.search_with_symbol("?", dating_keywords)

        if sentiment:
            if sentiment == "positive":
                self.search_with_symbol(":)", dating_keywords)
            elif sentiment == "negative":
                self.search_with_symbol(":(", dating_keywords)
            else:
                raise TweetScrapeBootstrapException("Unknown sentiment.")

        if links:
            self.search_with_symbol("filter:" + links, dating_keywords)

        if source:
            self.search_with_symbol("source:" + source, dating_keywords)

        if near:
            self.search_with_symbol("near:" + near, dating_keywords)
        elif near and within:
            self.search_with_symbol("near:" + near + self.separator + "within:" + within, dating_keywords)

        if since:
            self.search_with_symbol("since: " + since, dating_keywords)

        if until:
            self.search_with_symbol("until: " + until, dating_keywords)

    def search_with_symbol(self, symbol, keyword_list):
        """
        Used as a shortcut when you have to add somehting like ? or :( or :) behind a search
        query on Twitter.

        :param symbol: The symbol in form of a string
        :param keyword_list: The list with all keywords that should be searched for
        :return:
        """

        for keyword in keyword_list:
            if symbol:
                self.search_string = keyword.replace(" ", "") + tsb.separator + symbol
            else:
                self.search_string = keyword.replace(" ", "")

            logger.debug("Search with symbol: " + str(self.search_string))
            self.search()

    @staticmethod
    def read_custom_list(path):
        """
        Reads a custom list if you want to provider your own list (bulk)

        :param path: The path where the file resides.
        :return: A list containing the file rows
        """

        temp_custom_list = list()

        with open(path, encoding='utf-8', mode='r') as file:
            for line in file:
                temp_custom_list.append(line.replace("\n", " "))

        return temp_custom_list


if __name__ == "__main__":

    logging.debug("Arguments: " + str(args))

    # generate basic object to work with
    tsb = TweetScrapeBootstrap(search_string=None, name=None)

    # in this case you want to make a manual scrape
    if args.q:
        logger.debug("Selfdefined Mode activated.")

        # self defined query
        tsb.name = args.container_name
        tsb.search_string = args.q
        tsb.search()

    # in this case you want to make an automatic scrape
    elif args.q is None and args.querymode:
        logger.debug("Automatic Mode activated.")

        # automatism is working
        tsb.docker_image_name = args.container_name

        # decide what to do based on the enum
        # in this case you want to scrape results based on large german cities
        if args.querymode == TwitterCommand.NEAR_LARGE_GERMAN_CITIES:
            logger.debug("near large german cities - keyword: " + args.keyword_col[0])

            # get all keywords
            keyword_string = ""
            for keyword in args.keyword_col:
                keyword_string += keyword.replace("\n", "") + tsb.separator

            # invoke the scrapers
            tsb.search_near_large_german_cities(keyword_string)

        # WIP: custom list mode
        # elif args.querymode == TwitterCommand.CUSTOM_LIST:
        #    custom_list = tsb.read_custom_list()

        elif args.querymode == TwitterCommand.DATING_KEYWORDS_EN:
            logger.debug("dating keywords en")
            tsb.search_dating_keywords_en(args.sentiments, args.question, args.links, args.sources,
                                          args.near, args.radius, args.since)

        else:
            raise TweetScrapeBootstrapException("No known automatic mode selected.")

    else:
        raise TweetScrapeBootstrapException("Yeah, no. Not like that. Try again my friend!")
