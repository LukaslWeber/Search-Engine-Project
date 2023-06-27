import time
from typing import List

import nltk
from nltk import word_tokenize, pos_tag
#nltk.download('stopwords')
from nltk.corpus import stopwords

from py3langid.langid import LanguageIdentifier, MODEL_FILE
import numpy as np
import re
import urllib3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


# Crawl the web to discover English content related to Tübingen.
# The crawled content should be stored locally.
# If interrupted, your crawler should be able to re-start the crawling process at any time.

# TODO: Read about a "Focused Crawler"
# TODO: HTTP-Anfrage starten
# TODO: Was mit deutschen Seiten die keinen englischen Content haben?
# Sicherstellen, dass wir auf der englischen Seite bleiben --> Rufe detect_language auf und checke ob die Sprache en ist
# TODO: Priority Queue in der Englischer Content vorne steht
# TODO: Duplicate Detections

class Web_Crawler():

    def __init__(self, frontier: List[str], max_pages, use_index_from_file):
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
        # Language identifier for checking the language of a document
        self.identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True)
        self.identifier.set_languages(['de', 'en', 'fr'])

    def crawl(self, frontier, index):
        """
        Crawl the web
        :param frontier: The frontier of known URLs to crawl. You will initially populate this with your seed set of URLs and later maintain all discovered (but not yet crawled) URLs here.
        :param index: The location of the local index storing the discovered documents.
        :return:
        """
        # TODO: Implement me
        pass

    def index(self, doc: str, index):
        """
        Add a document to the index. You need (at least) two parameters:
        :param doc: The document to be indexed
        :param index: The location of the local index storing the discovered documents.
        :return:
        """
        # TODO: Implement me
        pass

    def is_relevant(self, response_text: str, url: str):
        """
        Check if a webpage is relevant based on the presence of the word "Tübingen" or "Tuebingen" within the content.
        The uppercase should be ignored here
        :param response_text:
        :param url: URL of the webpage to check
        :return: True if the webpage is relevant, False otherwise
        """

        tuebingen_umlaut_regexp = re.compile(r"Tübingen", re.IGNORECASE)
        tuebingen_regexp = re.compile(r"Tuebingen", re.IGNORECASE)

        if tuebingen_umlaut_regexp.search(response_text) \
                or tuebingen_umlaut_regexp.search(url) \
                or tuebingen_regexp.search(response_text) \
                or tuebingen_regexp.search(url):
            return True

        return False

    def detect_language(self, text):
        """
        Method that detects the language that was used in a document to prevent German and documents of other languages to get into our index
        :param text: The text that is to be classified into a language
        :return: Shortcut for the text language, e.g. 'de', 'en', ...
        """
        try:
            detected_languages = {}
            for sentence in text.split('.'):  # Split text into sentences
                lang, confidence = self.identifier.classify(sentence)
                if confidence >= 0.5:  # Set a confidence threshold
                    detected_languages[lang] = detected_languages.get(lang, 0) + 1

            print(detected_languages)
            lang_with_most_sentences = max(detected_languages, key=detected_languages.get)
            return lang_with_most_sentences

        except Exception as e:
            print(f"Some error occured during language detection of the string: {str(e)}")
            return None

test_crawler = Web_Crawler(["abc", "aaa"], 10, True)

def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

def get_url_content(url):
    http = urllib3.PoolManager()
    with http.request('GET', url, preload_content=False) as response:
        # Stream the response data in chunks
        content = b""
        for chunk in response.stream(4096):
            content += chunk
    html_content = content.decode('utf-8')

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all the <a> tags for links
    links = [a['href'] for a in soup.find_all('a', href=True)]
    print(links)

# TOD: Ftler#contet rau

    links = get_absolute_links(url, links)

    content = soup.get_text()

    print(links)

def get_absolute_links(url, links):
    base_url = get_base_url(url)
    absolute_links = set()
    for link in links:
        absolute_link = link if link.startswith(('http://', 'https://')) else urljoin(base_url, link)
        if absolute_link != url and absolute_link != base_url:
            absolute_links.add(absolute_link)
    return list(absolute_links)


response = get_url_content("https://www.tuebingen.de/14101.html")

#response = get_url_content("https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/autonomous-vision/lectures/computer-vision/")
print(response)

ponse = get_url_content("https://www.tuebingen.de/14101.html#content")
print(response)


print(get_absolute_links("https://www.tuebingen.de/", ["https://www.tuebingen.de/", "https://www.tuebingen.de", "https://www.tuebingen.de/#content"]))