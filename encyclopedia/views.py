from django.shortcuts import render
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entree):

    code = util.get_entry(entree)
    if code is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(code),
            "entree": entree
            })
    else:
        return render(request, "encyclopedia/apology1.html", {
            "message": f"Article '{entree}' doesn't exist."
        })


def search(request):
    template_name = 'search.html'
    query = request.GET.get('q').lower()

    results = []
    entries = util.list_entries()

    if query != "":
        for entry in entries:
            if query in entry.lower():
                results.append(entry)

    print("prout")
    for result in results:
        print(result)

    return render(request, "encyclopedia/search.html", {
        "entree": query,
        "results": results
    })

