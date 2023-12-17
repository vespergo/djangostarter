from django.http import HttpResponse
from django.shortcuts import render
from .models import Record

def index(request):
    record_list = Record.objects.order_by("-rel_date")    
    context = {
        "record_list": record_list,
    }
    return render(request, "recordstore/index.html", context)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)