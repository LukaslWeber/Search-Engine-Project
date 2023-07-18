from FocusedWebCrawler import FocusedWebCrawler

if __name__ == "__main__":
    urls = ['https://uni-tuebingen.de/en/',
        'https://www.tuebingen.mpg.de/en',
        'https://www.tuebingen.de/en/',
        'https://www.dzne.de/en/about-us/sites/tuebingen',
        'https://www.britannica.com/place/Tubingen-Germany',
        'https://tuebingenresearchcampus.com/en/tuebingen/general-information/local-infos/',
        'https://wikitravel.org/en/T%C3%BCbingen',
        'https://www.tasteatlas.com/local-food-in-tubingen',
        'https://allevents.in/tubingen/food-drinks',
        'https://www.tripadvisor.com/Attractions-g198539-Activities-c36-Tubingen_Baden_Wurttemberg.html',
        'https://wanderlog.com/list/geoCategory/199488/where-to-eat-best-restaurants-in-tubingen',
        'https://www.outdooractive.com/en/places-to-eat-drink/tuebingen/eat-drink-in-tuebingen/21873363',
        'https://www.citypopulation.de/en/germany/badenwurttemberg/t%C3%BCbingen/08416041__t%C3%BCbingen/',
        'https://www.braugasthoefe.de/en/guesthouses/gasthausbrauerei-neckarmueller/']
    crawler = FocusedWebCrawler(frontier=urls, max_pages=100)
    crawler.crawl(frontier=crawler.frontier, index_db=crawler.index_db)