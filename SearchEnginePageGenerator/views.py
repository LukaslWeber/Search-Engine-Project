from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def open_mainview(request):
    return render(request, 'mainview.html', {'name': 'Lukas'})


def search(request):
    query = request.GET.get('query')
    # Perform search operation based on the query
    # Retrieve search results from the database or external APIs
    results = [(1, "erstes dok"), (2, "2 ..."), (3, "3 ..."), (4, "4 ..."), (5, "5 ..."), (6, "6 ..."),
               (7, "7 ..."), (8, "8 ..."), (9, "9 ..."), (10, "10 ...")]  # Retrieve the search results

    context = {
        'query': query
    }
    for (pos, doc) in results:
        context["pos_" + str(pos)] = doc

    print(context)
    return render(request, 'searchview.html', context)
