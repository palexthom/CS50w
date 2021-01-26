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
            "message": f"Article '{entree}' doesn't exist.",
            "suggestion": "Would you like to  ",
            "link_url": f"/wiki/new/",
            "link_name": f"create {entree} ?"
        })


def search(request):
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
    if request.method == 'GET':
        return render(request, "encyclopedia/new.html")

    elif request.method == 'POST':
        entry_name = request.POST.get('title')
        content = request.POST.get('content')
        entries = [entry.lower() for entry in util.list_entries()]

        if entry_name.lower() not in entries:
            util.save_entry(entry_name, content)
            return redirect(f"/wiki/{entry_name}")
        else:
            return render(request, "encyclopedia/apology1.html", {
                "message": f"Entry '{entry_name}' already exists!.",
                "suggestion": "Visit entry ",
                "link_url": f"/wiki/{entry_name}",
                "link_name": f"{entry_name} ?"
            })


def edit(request, entree):
    if request.method == 'GET':
        entries = util.list_entries()
        if entree in entries:
            return render(request, "encyclopedia/edit.html", {
                "entry_name": entree,
                "content": util.get_entry(entree)
            })

    elif request.method == 'POST':
        entry_name = request.POST.get('title')
        content = request.POST.get('content')

        util.save_entry(entry_name, content)
        return redirect(f"/wiki/{entry_name}")



def rand_entry(request):
    entries = util.list_entries()
    if entries is not None:
        entry_name = entries[random.randrange(len(entries))]
        return redirect(f"/wiki/{entry_name}")


