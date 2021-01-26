from django.shortcuts import render, redirect
import markdown2
import random
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

    return render(request, "encyclopedia/search.html", {
        "entree": query,
        "results": results
    })


def new(request):
    return render(request, "encyclopedia/new.html")


def rand_entry():
    entries = util.list_entries()
    if entries is not None:
        entry_name = entries[random.randrange(len(entries))]
        return redirect(f"/wiki/{entry_name}")


