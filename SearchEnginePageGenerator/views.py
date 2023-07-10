import os

from django.shortcuts import render
from django.http import HttpResponse

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
        results = [(1, "abc"), (2, "def"), (3, "ghi"), (4, "jkl"), (5, "mno"), (6, "pqr"), (7, "stu"), (8, "vwx"), (9, "yz"), (10, "LOL"), (11, "11"),
                   (1, "abc"), (2, "def"), (3, "ghi"), (4, "jkl"), (5, "mno"), (6, "pqr"), (7, "stu"), (8, "vwx"), (9, "yz"), (10, "LOL"), (11, "11")]
        # Store search results and query in the session
        request.session['search_results'] = results
        request.session['query'] = query
    else:
        results = request.session['search_results']

    # Perform search operation based on the query
    start_index = int(request.GET.get('start_index', 0))
    previous_start_index = start_index - 10
    limited_results = results[start_index: start_index + 10]
    show_more = start_index + 10 < len(results)
    show_previous = start_index >= 10
    remaining_elements = len(results) - (start_index + 10)


    context = {
        'query': query,
        'search_results': limited_results,
        'start_index': start_index + 10,
        'previous_start_index': previous_start_index,
        'show_more': show_more,
        'show_previous': show_previous,
        'remaining_elements': remaining_elements
    }
    print(f"Full results are: ")
    print(results)
    print(context)
    return render(request, 'searchview.html', context)
