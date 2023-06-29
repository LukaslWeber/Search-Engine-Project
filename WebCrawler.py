import re
import time
from queue import PriorityQueue
from typing import List
from urllib.parse import urljoin, urlparse

# Method for sending and receiving websites and sending http requests (urllib) and parsing them (BeautifulSoup)
import urllib3
from bs4 import BeautifulSoup
# For checking whether a page is English or German
from py3langid.langid import LanguageIdentifier, MODEL_FILE

from File_loader import load_frontier, load_visited_pages


# Crawl the web to discover English content related to Tübingen.
# The crawled content should be stored locally.
# If interrupted, your crawler should be able to re-start the crawling process at any time.

#  TODO: Read about a "Focused Crawler"
#  DONE: HTTP-Anfrage starten
#  DONE: Was passiert wenn http Anfrage nicht klappt?
#  TODO: Was mit deutschen Seiten die keinen englischen Content haben?
#           --> Könnte man übersetzen Sicherstellen, dass wir auf der englischen Seite bleiben oder
#           deutsche auf niedrigere PRIOO setzen --> Rufe detect_language auf und checke ob die Sprache en ist
# TODO: Priority Queue in der Englischer Content vorne steht Vielleicht:
#       1. TÜBINGEN & ENGLISCH 2. Tübingen & Deutsch oder andere Sprachen 3. Andere Seiten
#       momentant: priorität 1 für seed urls, 2 für links in denen tübingen vorkommt, 3 sonst. 
#  TODO: Duplicate Detections
#  TODO: Den Inhalt der Website vielleicht besser lesen. Jetzt fehlen teilweise
#           Im Korpus Leerzeichen, ist zeug von der oberen Leiste drin etc.
#  TODO: Stop einbauen
#  TODO: Dokumente in collection speichern


class WebCrawler:
    def __init__(self, max_pages, frontier: List[str] = None):
        """
        Initializes the Crawler object with a frontier and a maximum number of pages to be crawled
        :param max_pages: Number indicating the maximum number of webpages to be crawled
        :param frontier: np.ndarray of urls (Strings) or None if the past search should be continued!
        """
        # If no frontier is given --> Load the frontier from a previous search
        if frontier is None:
            self.frontier = load_frontier()
            self.visited = load_visited_pages()
        else:
            self.frontier = frontier
            self.visited = set()
        self.max_pages = max_pages
        # Language identifier for checking the language of a document
        self.identifier = LanguageIdentifier.from_pickled_model(MODEL_FILE, norm_probs=True)
        self.identifier.set_languages(['de', 'en', 'fr'])

    def crawl(self, frontier: List[str], index: int):
        """
        Crawls the web with the given frontier
        :param frontier: The frontier of known URLs to crawl. You will initially populate this with
        your seed set of URLs and later maintain all discovered (but not yet crawled) URLs here.
        :param index: The location of the local index storing the discovered documents.
        """
        num_pages_crawled = 0
        #initialize priority queue and add seed urls 
        pq_frontier = PriorityQueue()
        for doc in frontier:
            pq_frontier.put((1, doc))

        while pq_frontier and num_pages_crawled < self.max_pages:
            # get next URL from the frontier
            _,url = pq_frontier.get()

            if url in self.visited:
                continue

            # Mark the URL as visited
            self.visited.add(url)
            num_pages_crawled += 1

            print('crawled:')
            print(num_pages_crawled)

            # get page content and page language
            page_links, page_content = get_web_content_and_urls(url)
            page_language = self.detect_language(page_content)
            print("content:")
            print(page_content)
            
            #skip empty pages
            if page_links == "" and page_content == "":
              continue 

            #optional:skip if content is not english
            #if page_language != "en":
            #    continue

            # Skip if the URL has already been visited
            
            #add document to collection if its language is english and content is relevant
            #(check language here if not english content is not skipped above)
            page_relevant = self.is_relevant(page_content, url)
            if page_relevant and page_language == 'en' :
               self.add_to_collection(url, page_content, 'collection.txt')
            
            page_links = set(page_links)
            # Add newly discovered URLs to the frontier, assign priority 1 to topic relevant docs
            # optional: assign priorities 1 to english content, 2 to german content, 3 otherwise
            for link in page_links:
                #check if url is valid (to prevent http request fails)
                #link = get_base_url(link)
                if not is_valid_url(link):
                    continue
                """
                language = self.detect_language(get_web_content_and_urls(link)[1])
                if language == 'en':
                    priority = 1
                elif language == 'de':
                    priority = 2
                else:
                    priority = 3
                """
                #check if link is relevant
                if self.is_relevant("",link):
                    priority = 2
                else:
                    priority = 3

                pq_frontier.put((priority, link))
        self.frontier = pq_frontier

    def index(self, doc: str, index: int):
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

    def add_to_collection(self, url: str, page_content: str, filename: str):
        """
        Add the URL and page content to a text document in the collection.
        :param url: The URL of the page.
        :param page_content: The content of the page.
        :param filename: The name of the text document.
        """
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"URL: {url}\n\n")
            file.write(f"Page Content:\n{page_content}\n\n")


    def detect_language(self, text: str):
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

            print(detected_languages)
            lang_with_most_sentences = max(detected_languages, key=detected_languages.get)
            return lang_with_most_sentences

        except Exception as e:
            print(f"Some error occured during language detection of the string: {str(e)}")
            return None


# checks if given url is valid (considered valid if host and port components are present)
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_base_url(url: str):
    """
    Method that strips the given URL and returns only the base part of the URL.
    Example: https://www.tuebingen.de/blumenschmuck -> https://www.tuebingen.de
    :param url:
    :return:
    """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def get_web_content_and_urls(url: str):
    """
    Method that sends a http request with the given URL and gives the contained content and URLs back
    :param url: URL of the website that should be retrieved
    :return: links, content
    """
    #handling failed requests
    max_retries = 1
    retry_delay = 2
    retry = urllib3.Retry(total=3, redirect=3)
    timeout = urllib3.Timeout(connect=2.0, read=2.0)

    # Create a PoolManager with the Retry object
    http = urllib3.PoolManager(retries=retry, timeout=timeout)

    links = ""
    content = ""
    for retry in range(max_retries):
        try:
            with http.request('GET', url, preload_content=False) as response:
                # Stream the response data in chunks
                content = b""
                for chunk in response.stream(4096):
                    content += chunk

            break  # Break out of the retry loop if the request is successful
        except Exception as e:
            print(f"Attempt {retry + 1} failed. Retrying after {retry_delay} seconds., exception: {e}")
            time.sleep(retry_delay)

    if content != "":
        html_content = content.decode('utf-8')

        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract all the <a> html-tags for links IF they don't start with # because those are usually internal links
        # within a webpage (anchor links) and also don't include JavaScript links because they often execute a
        # JavaScript script or are not relevant here
        links = [a['href'] for a in soup.find_all('a', href=True)
                 if not a['href'].startswith(('#', 'javascript:'))]
        # Some links are given in an absolute (http...) form and some are given in a relative form (/example...).
        # The latter need to be transformed
        links = get_absolute_links(url, links)
        content = soup.get_text()
        # print(content)
        # print(soup.find_all(text=True))

    return links, content


def get_absolute_links(url: str, links: List[str]):
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


# response = get_web_content_and_urls("https://www.tuebingen.de/14101.html")

# response = get_url_content("https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/autonomous-vision/lectures/computer-vision/")
# print(response)

# links, content = get_url_content("https://www.w3schools.com/videos/index.php")


# print(get_absolute_links("https://www.tuebingen.de/", ["https://www.tuebingen.de/", "https://www.tuebingen.de", "https://www.tuebingen.de/#content"]))


#print(get_absolute_links("https://www.tuebingen.de/", ["https://www.tuebingen.de/", "https://www.tuebingen.de", "https://www.tuebingen.de/#content"]))



#-----------------------------
#just testing
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

crawler = WebCrawler(max_pages=10, frontier=urls)
crawler.crawl(frontier=crawler.frontier, index=1)

# Print the visited URLs to verify the crawling process
#print("Visited URLs:")
#for url in crawler.visited:
 #   print(url)

#print("frontier")
#print(crawler.frontier)


# Check the content of the collection to verify indexing
# print("Collection:")

content = get_web_content_and_urls('https://en.wikipedia.org/wiki/T%C3%BCbingen')[1]
#print(content)



    
