import os
from django.shortcuts import render
from django.http import HttpResponse
from gtts.tts import gTTS

# lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
lorem_ipsum = ""
#from Ranker import Ranker
#TODO
# path = 'data_files'
# index = os.path.join(path, 'forward_index.joblib')
# index_inverted = os.path.join(path, 'inverted_index.joblib')
# index_embedding = os.path.join(path, 'embedding_index.joblib')
# ranker = Ranker(index, index_inverted, index_embedding)


# Create your views here.
def open_mainview(request):
    context = {'name': 'Lukas'}
    return render(request, 'mainview.html', context)


def search(request):
    query = str(request.GET.get('queryField'))
    print(f"Query is: {query}")

    # Check if the current query matches the stored query in the session
    stored_query = request.session.get('query', '')
    if query != stored_query:
        # The query has changed, so remove the stored search results from the session
        request.session.pop('search_results', None)

    #Check if results are already stored in the session
    if 'search_results' not in request.session:
        print("Generating results")
        # TODO: results = ranker.rank(query, )
        results = [("https://theuselessweb.com/", "title", "result 1 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 2 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 3 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 4 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 5 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 6 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 7 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 8 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 9 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 10 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 11 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 12 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 13 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 14 website text" + lorem_ipsum),
                   ("https://theuselessweb.com/", "title", "result 15 website text" + lorem_ipsum)]
        # Store search results and query in the session
        request.session['search_results'] = results
        request.session['query'] = query
    else:
        results = request.session['search_results']

    # Perform search operation based on the query
    results_per_page = 11
    start_index = int(request.GET.get('start_index', 0))
    previous_start_index = start_index - results_per_page
    limited_results = results[start_index: start_index + results_per_page]
    show_more = start_index + results_per_page < len(results)
    show_previous = start_index >= results_per_page
    remaining_elements = len(results) - (start_index + results_per_page)
    audio_files = []
    audio_dir = "media"
    for f in os.listdir(audio_dir):
        os.remove(os.path.join(audio_dir,f))
    for i, result in enumerate(limited_results):
        website_text = result[2]
        # tts = gTTS(text=website_text + "from_query" + query, lang="en")
        audio_file_name = f"{query}_audio_file_{start_index + i}.mp3"
        # audio_path = os.path.join("media", audio_file_name)
        # tts.save(audio_path)
        audio_files.append(audio_file_name)


    context = {
        'query': query,
        'search_results': limited_results,
        'start_index': start_index + results_per_page,
        'previous_start_index': previous_start_index,
        'show_more': show_more,
        'show_previous': show_previous,
        'remaining_elements': remaining_elements,
        'audio_files': audio_files
    }
    print(f"Full results are: ")
    print(results)
    print(context)
    return render(request, 'searchview.html', context)
