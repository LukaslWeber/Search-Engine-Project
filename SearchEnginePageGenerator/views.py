from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def open_mainview(request):
    context = {'name': 'Lukas'}
    return render(request, 'mainview.html', context)


def search(request):
    query = str(request.GET.get('queryField'))
    print(f"Query is: {query}")
    #TODO: checke if alte query ist jetzt neue query?
    #Check if results are already stored in the session
    if 'search_results' not in request.session:
        results = [(1, "erstes dok"), (2, "Neues 2 ..."), (3, "Neues 3 ..."), (4, "4 ..."), (5, "5 ..."), (6, "6 ..."),
                   (7, "7 ..."), (8, "8 ..."), (9, "9 ..."), (10, "10 ..."), (11, "11 ...")]

        # Store search results in the session
        request.session['search_results'] = results
    else:
        results = request.session['search_results']

    # Perform search operation based on the query
    start_index = int(request.GET.get('start_index', 0))
    limited_results = results[start_index: start_index + 10]
    show_more = start_index + 10 < len(results)


    context = {
        'query': query,
        'search_results': limited_results,
        'start_index': start_index + 10,
        'show_more': show_more
    }
    print(context)
    return render(request, 'searchview.html', context)
