from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Content
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from operator import attrgetter
from django.contrib.auth import logout
from django.shortcuts import redirect

# Create your views here.
NLASTOBJ = 10    # Number of the last objects that will be presented on the principal page


def index(request):
    content_list : Content = []
    # 1.- Lista de contenidos
    content = Content.objects.all()
    sorted_list = sorted(content, key=attrgetter('date'), reverse=True)
    for i in sorted_list[:NLASTOBJ]:   # Ponemos en la respuesta los últimos objetos añadidos
        content_list.append(i)
    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/index.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list' : content_list
    }
    # 4.- Renderizar
    return HttpResponse(template.render(context, request))

@csrf_exempt
def get_content(request, aportation):

    # POST
    if request.method == 'POST':
        title = request.POST['title']
        link = request.POST['link']
        description = request.POST['description']
        positive = request.POST['positive']
        negative = request.POST['negative']
        date = request.POST['date']
        num_comment = request.POST['num_comment']
        extended_info = request.POST['extended_info']
        c = Content(source=aportation, title=title, link=link, description=description, positive=positive,
                    negative=negative, date=date, num_comment=num_comment, extended_info=extended_info)
        c.save()

    # GET
    try:
        # 1.- Obtenemos el contenido
        content = Content.objects.get(source=aportation)
        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/aportation.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content': content
        }
        response = template.render(context, request)
    except Content.DoesNotExist:
        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/newcontent.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
        }
        response = template.render(context, request)

    return HttpResponse(response)


def say_hello_to(request, name):
    return HttpResponse("Hello " + name)


def say_number(request, num):
    return HttpResponse("Hello " + str(num))

def logedIn(request):
    if request.user.is_authenticated:
        response = "Logged in as \"" + request.user.username + '"'
    else:
        response = 'You are not authenticated. <a href="/admin/">Authentication here</a>'
    return HttpResponse(response)

def logout_view(request):
    logout(request)
    return redirect("/LoVisto/")