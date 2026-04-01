from django.http import HttpResponse

def hello_pms(request):
    return HttpResponse("Hello Real Estate PMS")