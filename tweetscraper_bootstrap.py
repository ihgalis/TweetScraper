from bootstrap.standard_bootstrap import TweetScrapeBootstrap
from exceptions.exceptions import TweetScrapeBootstrapException
from enumerate import TwitterCommand

import logging
import argparse
import sys


def parse_args(args):
    """
    Provides an argument handling based on argparse.

    :param args: system args
    :return: The parser object which can be worked on later
    """

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
    parser.add_argument('-lp', action="store", dest="custom_list",
                        help="Custom list path in case you want to make a bulk search for multiple keywords.")

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

    return parser.parse_args(args)


def main():
    """
    Hook for the entire application. Interprets the argparse things, sets up a working
    logger and interprets the start condition based on the arguments.

    :return:
    """

    args = parse_args(sys.argv[1:])

    # Logger
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.debug("Arguments: " + str(args))

    if args.v:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # generate basic object to work with
    tsb = TweetScrapeBootstrap(search_string=None, name=None, docker_image_name="tweetscraper_alpine:latest", logger=logger, args=args)

    # in this case you want to make a manual scrape
    if args.q:
        logger.debug("Selfdefined Mode activated.")

        # self defined query
        tsb.name = args.container_name

        # set the search string
        tsb.search_string = args.q

        # start the docker party
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

        # dating keywords english
        elif args.querymode == TwitterCommand.DATING_KEYWORDS_EN:
            logger.debug("dating keywords en")
            tsb.search_dating_keywords_en(args.sentiments, args.question, args.links, args.sources,
                                          args.near, args.radius, args.since)

        # in case of custom lists
        elif args.querymode == TwitterCommand.CUSTOM_LIST:
            logger.debug("custom list detected")

            # get the list
            keyword_list = tsb.read_custom_list(args.custom_list)

            for keyword in keyword_list:
                # clean it upt
                keyword = keyword.replace("\n", "")

                # give it a name
                tsb.name = args.container_name + tsb.separator + str(keyword)
                logger.debug("custom list keyword: " + str(keyword))

                # search for it (docker etc.)
                tsb.search_with_symbol_generic(keyword, args.sentiments, args.question, args.links, args.sources,
                                               args.near, args.radius, args.since, args.until)

        else:
            raise TweetScrapeBootstrapException("No known automatic mode selected.")

    else:
        raise TweetScrapeBootstrapException("Yeah, no. Not like that. Try again my friend!")


if __name__ == "__main__":
    main()
