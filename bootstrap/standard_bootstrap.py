from exceptions.exceptions import TweetScrapeBootstrapException

import time
import docker


class TweetScrapeBootstrap(object):
    """
    This class gives you the possibility to scrape Twitter in a different way. Thanks to johnbakerfish we do not have to use
    the API but scrape the results by using his scrapy based code. Furthermore this class has been built to make it possible to
    scrape Twitter much faster using docker. There will be created multiple docker container for each scraper needed.
    """

    def __init__(self, search_string=None, name=None, docker_image_name="tweetscraper_alpine:latest", logger=None, args=None):
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
        self.logger = logger
        self.args = args

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
            self.logger.debug("Large German Cities: Path not given - Taking standard")
            with open("analyze_data/large_german_cities.txt", encoding='utf-8', mode='r') as file:
                for line in file:
                    self.large_german_cities.append(line.replace("\n", " "))
        else:
            self.logger.debug("Large German Cities: Path given - "+str(path))
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
        self.logger.debug("COMMAND: " + str(temp_command))

        if self.args.vol:

            # the -v configuration for the docker
            docker_volumes = {
                self.args.vol: {
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
            self.logger.debug("COMMAND: " + str(temp_command))
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

    def search_with_symbol_generic(self, keywords, sentiment=None, question=None, links=None, source=None, near=None, within=None, since=None, until=None):
        """

        :param sentiment:
        :param question:
        :param links:
        :param source:
        :param near:
        :param within:
        :param since:
        :param until:
        :return:
        """

        # when everything is noen just go ahead
        if sentiment is None and \
                question is False and \
                links is None and \
                source is None and \
                near is None and \
                within is None and \
                since is None:
            self.search_with_symbol(None, keywords)

        if question:
            self.search_with_symbol("?", keywords)

        if sentiment:
            if sentiment == "positive":
                self.search_with_symbol(":)", keywords)
            elif sentiment == "negative":
                self.search_with_symbol(":(", keywords)
            else:
                raise TweetScrapeBootstrapException("Unknown sentiment.")

        if links:
            self.search_with_symbol("filter:" + links, keywords)

        if source:
            self.search_with_symbol("source:" + source, keywords)

        if near:
            self.search_with_symbol("near:" + near, keywords)
        elif near and within:
            self.search_with_symbol("near:" + near + self.separator + "within:" + within, keywords)

        if since:
            self.search_with_symbol("since: " + since, keywords)

        if until:
            self.search_with_symbol("until: " + until, keywords)

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
        self.search_with_symbol_generic(dating_keywords, sentiment, question, links, source, near, within, since, until)

    def search_with_symbol(self, symbol, keyword_list):
        """
        Used as a shortcut when you have to add somehting like ? or :( or :) behind a search
        query on Twitter.

        :param symbol: The symbol in form of a string
        :param keyword_list: The list with all keywords that should be searched for
        :return:
        """

        # sometimes it is not a list ... well
        if isinstance(keyword_list, (list,)):
            for keyword in keyword_list:
                self.proceed_symbol_search(symbol, keyword)

        # no list? well must be some custom thing
        else:
            # make it more readable
            keyword = keyword_list
            self.proceed_symbol_search(symbol, keyword)

    def proceed_symbol_search(self, symbol, keyword):
        """
        Method checks whether there is a symbol or not and adds it or not. Finfally it invokes
        search() in order to create the docker containers.

        :param symbol:
        :param keyword:
        :return:
        """
        if symbol:

            # include it with the "symbol" whatever it is
            self.search_string = keyword.replace(" ", "") + self.separator + symbol

        else:
            # do it without the symbol but clean the keyword up (just in case)
            self.search_string = keyword.replace(" ", "")

        self.logger.debug("Search with symbol: " + str(self.search_string))
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
