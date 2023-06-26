import time
from typing import List

import numpy as np
import re
# Crawl the web to discover English content related to Tübingen.
# The crawled content should be stored locally.
# If interrupted, your crawler should be able to re-start the crawling process at any time.

# TODO: Read about a "Focused Crawler"

class Web_Cralwer():

    def __init__(self, frontier : List[str], max_pages, use_index_from_file):
        """
        Initializes the Crawler object with a frontier and a maximum number of pages to be crawled
        :param frontier: np.ndarray of urls (Strings)
        :param max_pages: Number indicating the maximum number of webpages to be crawled
        :param use_index_from_file: Indicates whether the Index exists in the RAM (False) or in a file (True)
        """
        self.visited = set()
        self.max_pages = max_pages
        self.frontier = frontier
        self.use_index_from_file = use_index_from_file

    def crawl(self, frontier, index):
        """
        Crawl the web
        :param frontier: The frontier of known URLs to crawl. You will initially populate this with your seed set of URLs and later maintain all discovered (but not yet crawled) URLs here.
        :param index: The location of the local index storing the discovered documents.
        :return:
        """
        #TODO: Implement me
        pass

    def index(self, doc : str, index):
        """
        Add a document to the index. You need (at least) two parameters:
        :param doc: The document to be indexed
        :param index: The location of the local index storing the discovered documents.
        :return:
        """
        #TODO: Implement me
        pass

    def is_relevant(self, response_text : str, url : str):
        """
        Check if a webpage is relevant based on the presence of the word "Tübingen" or "Tuebingen" within the content.
        The uppercase should be ignored here
        :param url: URL of the webpage to check
        :return: True if the webpage is relevant, False otherwise
        """

        tübingen_regexp = re.compile(r"Tübingen", re.IGNORECASE)
        tuebingen_regexp = re.compile(r"Tuebingen", re.IGNORECASE)

        if tübingen_regexp.search(response_text) \
            or tübingen_regexp.search(url) \
            or tuebingen_regexp.search(response_text) \
            or tuebingen_regexp.search(url):
            return True

        return False


test_crawler = Web_Cralwer(["abc", "aaa"], 10, True)