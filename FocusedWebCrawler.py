import os
import re
import tempfile
import time
import timeit
from queue import PriorityQueue
from typing import List
from urllib.parse import urljoin, urlparse

import numpy as np
# Method for sending and receiving websites and sending http requests (urllib) and parsing them (BeautifulSoup)
import urllib3
from bs4 import BeautifulSoup
# For checking whether a page is English or German
from py3langid.langid import LanguageIdentifier, MODEL_FILE

from File_loader import load_frontier, load_visited_pages, load_index, save_frontier_pages, save_visited_pages, \
    save_index


#  TODO: Was mit deutschen Seiten die keinen englischen Content haben?
#           --> Könnte man übersetzen Sicherstellen, dass wir auf der englischen Seite bleiben oder
#           deutsche auf niedrigere PRIOO setzen --> Rufe detect_language auf und checke ob die Sprache en ist
# TODO: Duplicate Detections
# TODO: Nicht zu wenig zeit zwischen den Anfragen
# TODO: ROBOTS.TXT BEACHTEN


def has_tuebingen(string_to_check: str) -> bool:
    """
    Check if a webpage is relevant based on the presence of the word "Tübingen" or "Tuebingen" within the content.
    The uppercase should be ignored here
    :param string_to_check: The string that is to be checked
    :return: True if the webpage is relevant (contains "Tübingen" or "Tuebingen"), False otherwise
    """
    tuebingen_umlaut_regexp = re.compile(r"Tübingen", re.IGNORECASE)
    tuebingen_regexp = re.compile(r"Tuebingen", re.IGNORECASE)

    if tuebingen_umlaut_regexp.search(string_to_check) or tuebingen_regexp.search(string_to_check):
        return True

    return False


def get_priority(contains_tuebingen: bool, language: str) -> int or None:
    """
    Returns the priority of a document given the information if it contains Tübingen and its langauge
    :param contains_tuebingen: bool, Parameter that indicates whether some form of
    the word "Tübingen" is contained in the document
    :param language: str, String that represents the abbreviation of the most used language in the document
    :return: Integer indicating the priority where 1 is the highest and 4 is the lowest priority or None if the document is
    not of relevance of any sort.
    """
    if contains_tuebingen and language == 'en':
        return 1
    elif contains_tuebingen and language == 'de':
        return 2
    elif language == 'en':
        return 3
    elif language == 'de':
        return 4
    else:
        return None


class FocusedWebCrawler:
    def __init__(self, max_pages: int = np.inf, frontier: List[str] = None):
        """
        Initializes the Crawler object with a frontier and a maximum number of pages to be crawled.
        If the frontier is not given (None or no argument given), then the last search will be continued.
        :param max_pages: Number indicating the maximum number of webpages to be crawled
        :param frontier: np.ndarray of urls (Strings) or None if the past search should be continued!
        """
        # If no frontier is given --> Load the frontier, visited pages and index from a previous search
        if frontier is None:
            self.frontier = load_frontier()
            self.visited = load_visited_pages()
            self.index_db = load_index()
        else:
            self.frontier = PriorityQueue()
            for doc in frontier:
                self.frontier.put((1, doc))
            self.visited = set()
            self.index_db = {}
        # Maximum pages to be indexed
        self.max_pages = max_pages
        # Language identifier for checking the language of a document
        self.identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True)
        # self.identifier.set_languages(['de', 'en', 'fr'])

    def crawl(self, frontier: PriorityQueue, index_db):
        """
        Crawls the web with the given frontier
        :param frontier: The frontier of known URLs to crawl. You will initially populate this with
        your seed set of URLs and later maintain all discovered (but not yet crawled) URLs here.
        :param index_db: The location of the local index storing the discovered documents.
        """
        num_pages_crawled = 0
        # initialize priority queue and add seed urls
        sss = time.time()
        while not frontier.empty() and num_pages_crawled <= self.max_pages:
            _, url = frontier.get()

            # If page has already been visited --> Continue loop
            if url in self.visited:
                continue

            print(f"Crawling page: {num_pages_crawled} with url: {url}")

            # get page content and links on the page
            start = timeit.default_timer()
            page_links, page_header, page_content, page_footer = get_web_content_and_urls(url)
            print(f" getting content and urls took: {timeit.default_timer() - start:.2f}")
            print(f" Page content: {page_content}")
            print(f" Page links: {page_links}")

            # skip empty pages
            if page_links is None and page_content is None:
                continue

            # Check if "Tübingen" or "Tuebingen" is contained somewhere in the URL or document
            contains_tuebingen = has_tuebingen(url) or has_tuebingen(page_header) or \
                                 has_tuebingen(page_content) or has_tuebingen(page_footer)
            start = timeit.default_timer()
            page_language = self.detect_language(page_content)
            print(f" Detecting language took: {timeit.default_timer() - start:.2f}s")

            page_priority = get_priority(contains_tuebingen, page_language)
            print(f" Detected priority was {page_priority}")
            page_links = set(page_links)

            # Add the URL to the Visited links,
            self.visited.add(url)
            # TODO: Page Priority one is only taken because many pages that are irrelevant
            # Example: http://uli.nli.org.il/F/HM74MN1YKM7KYGP7KV882Y74M4DB45EIEPULCYI73KGS3G57HX-01577?func=full-set-set&set_number=011746&set_entry=000001&format=002
            # http://uli.nli.org.il/F/HM74MN1YKM7KYGP7KV882Y74M4DB45EIEPULCYI73KGS3G57HX-01582?func=myshelf-add-ful-1&doc_library=NLX10&doc_number=000975756
            if page_priority is None or page_priority >= 2:
                print(" THIS PAGE IS NOT RELEVANT!!! Continuing search")
                print("________________________________________________________")
                continue
            # Add newly discovered URLs to the frontier, assign priority 1 to topic relevant docs
            for link in page_links:
                if is_valid_url(link):
                    frontier.put((page_priority, link))
                else:
                    print(f"An invalid URL has been found and could not be added to the frontier: {link}")
            # Add the URL and page content to the index
            self.index(index_db, url, page_content, num_pages_crawled)

            # Save everything to files after every 25 documents
            if num_pages_crawled % 25 == 0 or num_pages_crawled == self.max_pages:
                try:
                    # Use temporary files for saving
                    temp_index_path = os.path.join(tempfile.gettempdir(), "temp_forward_index.joblib")
                    temp_visited_path = os.path.join(tempfile.gettempdir(), "temp_visited_pages.json")
                    temp_frontier_path = os.path.join(tempfile.gettempdir(), "temp_frontier_pages.json")

                    # Save to temporary files
                    save_index(temp_index_path, index_db)
                    save_visited_pages(temp_visited_path, self.visited)
                    save_frontier_pages(temp_frontier_path, frontier)

                    # If all saves are successful, move the temporary files to the actual save locations
                    file_folder = "data_files"
                    os.replace(temp_index_path, os.path.join(file_folder, "forward_index.joblib"))
                    os.replace(temp_visited_path, os.path.join(file_folder, "visited_pages.json"))
                    os.replace(temp_frontier_path, os.path.join(file_folder, "frontier_pages.json"))

                    print("Data saved successfully.")
                except Exception as e:
                    # Handle any exceptions that occur during saving
                    print(f"An error occurred while saving data: {str(e)}")
                    print("Data not saved.")

            # After page has been crawled, increment the number of visited pages by 1
            num_pages_crawled += 1
            print("____________________________")

        print(f"Index is: {self.index_db}")
        print(f"took time: {time.time() - sss}")

    def index(self, index_db : dict, url: str, doc: str, key) -> None:
        """
        Add a document to the index. You need (at least) two parameters:
        :param url: The URL with which the document was retrieved
        :param doc: The document to be indexed
        :param index_db: The location of the local index storing the discovered documents.
        :return:
        """
        index_db[key] = (url, doc)

    def detect_language(self, text: str) -> str:
        """
        Method that detects the language that was used in a document to prevent German and documents of other
        languages to get into our index
        :param text: The text that is to be classified into a language
        :return: Shortcut for the text language, e.g. 'de', 'en', ...
        """
        try:
            detected_languages = {}
            for sentence in text.split('.'):  # Split text into sentences
                lang, confidence = self.identifier.classify(sentence)
                if confidence >= 0.5:  # Set a confidence threshold
                    detected_languages[lang] = detected_languages.get(lang, 0) + 1

            lang_with_most_sentences = max(detected_languages, key=detected_languages.get)
            print(f" The detected language was: {lang_with_most_sentences} from the occurences {detected_languages}")
            return lang_with_most_sentences

        except Exception as e:
            print(f"Some error occured during language detection of the string: {str(e)}")
            return None


def add_to_collection(url: str, page_content: str, filename: str) -> None:
    """
    Add the URL and page content to a text document in the collection.
    :param url: The URL of the page.
    :param page_content: The content of the page.
    :param filename: The name of the text document.
    """
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"URL: {url}\n\n")
        file.write(f"Page Content:\n{page_content}\n\n")


# checks if given url is valid (considered valid if host and port components are present)
def is_valid_url(url) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_base_url(url: str) -> str:
    """
    Method that strips the given URL and returns only the base part of the URL.
    Example: https://www.tuebingen.de/blumenschmuck -> https://www.tuebingen.de
    :param url:
    :return:
    """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def get_web_content_and_urls(url: str, max_retries: int = 1, retry_delay: float = 2) \
        -> (List[str], str, str, str) or (None, None, None, None):
    """
    Method that sends a http request with the given URL and gives the contained content and URLs back
    :param max_retries: Optional, Number of maximum retries if the get request fails
    :param retry_delay: Optional, The delay between requests if a get request fails
    :param url: URL of the website that should be retrieved
    """
    # handling failed requests
    retry = urllib3.Retry(total=3, redirect=3)
    timeout = urllib3.Timeout(connect=2.0, read=2.0)
    http = urllib3.PoolManager(retries=retry, timeout=timeout)

    raw_html_content = ""
    for retry in range(max_retries):
        try:
            with http.request('GET', url, preload_content=False) as response:
                # Stream the response data in chunks
                raw_html_content = b""
                for chunk in response.stream(4096):
                    raw_html_content += chunk
            break  # Break out of the retry loop if the request is successful
        except Exception as e:
            print(f"Attempt {retry + 1} failed. Retrying after {retry_delay} seconds., exception: {e}")
            time.sleep(retry_delay)

    if raw_html_content != "":
        # Decode the retrieved html web page
        html_content = raw_html_content.decode('utf-8', 'ignore')
        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove style and script tags as they contain no information
        for data in soup(['style', 'script']):
            # Remove tags
            data.decompose()

        # Extract header
        header = soup.find('header')
        header_content = header.extract().get_text(separator=" ") if header else ""

        # Extract footer
        footer = soup.find('footer')
        footer_content = footer.extract().get_text(separator=" ") if footer else ""

        # Get body content. After having extracted the header and footer, only the title and the body of the document
        # shall remain
        body_content = soup.get_text(separator=" ")
        body_content = re.sub(r'\s+', ' ', body_content)

        # Extract all the <a> html-tags for links IF they don't start with # because those are usually internal links
        # within a webpage (anchor links) and also don't include JavaScript links because they often execute a
        # JavaScript script or are not relevant here
        links = [a['href'] for a in soup.find_all('a', href=True)
                 if not a['href'].startswith(('#', 'javascript:'))]
        # Some links are given in an absolute (http...) form and some are given in a relative form (/example...).
        # The latter need to be transformed. The rest stays the same
        links = get_absolute_links(url, links)

        return links, header_content, body_content, footer_content

    return None, None, None, None


def get_absolute_links(url: str, links: List[str]) -> List[str]:
    """
    Method that returns absolute links for a list of absolute and/or relative links
    :param url: The website url that is origin of all received links
    :param links: List of links that were retrieved from the url
    :return: A list of Strings (URLs) which contains only absolute links which are directly callable
    """
    base_url = get_base_url(url)
    absolute_links = set()
    for link in links:
        # If link is relative then join it with the base page url
        absolute_link = link if link.startswith(('http://', 'https://')) else urljoin(base_url, link)
        # Only add the page if it is not the page that was used to retrieve all the links to prevent unnecessary
        # requests
        if absolute_link != url and absolute_link != base_url:
            absolute_links.add(absolute_link)
    return list(absolute_links)


# _______________ OLD UNUSED METHODS __________________-
#     def crawl(self, frontier: List[str], index: int):
#         """
#         Crawls the web with the given frontier
#         :param frontier: The frontier of known URLs to crawl. You will initially populate this with
#         your seed set of URLs and later maintain all discovered (but not yet crawled) URLs here.
#         :param index: The location of the local index storing the discovered documents.
#         """
#         num_pages_crawled = 0
#         # initialize priority queue and add seed urls
#         pq_frontier = PriorityQueue()
#         for doc in frontier:
#             pq_frontier.put((1, doc))
#
#         while pq_frontier and num_pages_crawled < self.max_pages:
#
#             _, url = pq_frontier.get()
#
#             if url in self.page_overview and self.page_overview[url][2] == True:
#                 continue
#
#             # Mark the URL as visited
#             # self.visited.add(url)
#             num_pages_crawled += 1
#
#             print('crawled:')
#             print(num_pages_crawled)
#
#             if url in self.page_overview:
#                 page_content = self.page_overview[url][0]
#                 page_links = self.page_overview[url][1]
#                 page_language = self.page_overview[url][4]
#                 page_relevant = self.page_overview[url][3]
#             else:
#
#                 # get page content and page language
#                 page_links, page_content = get_web_content_and_urls(url)
#                 page_language = self.detect_language(page_content)
#                 # print("content:")
#                 # print(page_content)
#
#                 # skip empty pages
#                 if page_links == "" and page_content == "":
#                     continue
#
#                     # add document to collection if its language is english and content is relevant
#                 page_relevant = self.is_relevant(page_content, url)
#                 self.page_overview[url] = (page_content, page_links, True, page_relevant, page_language)
#
#             if page_relevant and page_language == 'en':
#                 add_to_collection(url, page_content, 'collection.txt')
#
#             page_links = set(page_links)
#             if pq_frontier.qsize() > self.max_pages:
#                 continue
#             # Add newly discovered URLs to the frontier, assign priority 1 to topic relevant docs
#             for link in page_links:
#                 if not is_valid_url(link):
#                     continue
#
#                 if link in self.page_overview:
#                     if self.page_overview[link][2] == True:
#                         continue
#                     language = self.page_overview[link][4]
#                     relevant = self.page_overview[link][3]
#                 else:
#                     links, content = get_web_content_and_urls(link)
#                     relevant = self.is_relevant(content, link)
#                     language = self.detect_language(content)
#                     self.page_overview[link] = (content, links, False, relevant, language)
#
#                 if relevant and language == 'en':
#                     priority = 2
#                 elif relevant:
#                     priority = 3
#                 elif language == 'en':
#                     priority = 4
#                 else:
#                     priority = 5
#
#                 pq_frontier.put((priority, link))
#
#         self.frontier = pq_frontier


# -----------------------------
# just testing
urls = ['https://uni-tuebingen.de/en/',
        'https://www.tuebingen.mpg.de/en',
        'https://www.tuebingen.de/en/',
        'https://en.wikipedia.org/wiki/T%C3%BCbingen',
        'https://www.dzne.de/en/about-us/sites/tuebingen',
        'https://www.britannica.com/place/Tubingen-Germany',
        'https://tuebingenresearchcampus.com/en/tuebingen/general-information/local-infos/',
        'https://wikitravel.org/en/T%C3%BCbingen',
        'https://www.tasteatlas.com/local-food-in-tubingen',
        'https://www.citypopulation.de/en/germany/badenwurttemberg/t%C3%BCbingen/08416041__t%C3%BCbingen/',
        'https://www.braugasthoefe.de/en/guesthouses/gasthausbrauerei-neckarmueller/']
# crawler = FocusedWebCrawler(max_pages=1, frontier=urls)
# crawler.crawl(frontier=crawler.frontier, index_db=crawler.index_db)
crawler = FocusedWebCrawler()
crawler.crawl(crawler.frontier, index_db=crawler.index_db)
#
# # Print the visited URLs to verify the crawling process
# print("Visited URLs:")
# for url in crawler.page_overview:
#     print(url)
