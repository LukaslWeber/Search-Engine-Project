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
        results = [(1, "result 1"), (2, "result 2"), (3, "result 3"), (4, "result 4"), (5, "result 5"), (6, "result 6"), (7, "result 7"), (8, "result 8"), (9, "result 9"), (10, "result 10"), (11, "result 11"),
                   (12, "result 12"), (13, "result 13"), (14, "result 14"), (15, "result 15")]
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


    context = {
        'query': query,
        'search_results': limited_results,
        'start_index': start_index + results_per_page,
        'previous_start_index': previous_start_index,
        'show_more': show_more,
        'show_previous': show_previous,
        'remaining_elements': remaining_elements
    }
    print(f"Full results are: ")
    print(results)
    print(context)
    return render(request, 'searchview.html', context)
