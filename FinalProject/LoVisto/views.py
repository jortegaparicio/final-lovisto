from django.http import HttpResponse
from .models import Content, User
from django.template import loader
from operator import attrgetter
from django.contrib.auth import logout
from django.utils import timezone

# Create your views here.
NLASTOBJ = 10    # Number of the last objects that will be presented on the principal page


def index(request):
    if request.method == 'POST':
        user = User.objects.get(user_name=request.user.username)
        title = request.POST['title']
        description = request.POST['description']
        link = request.POST['link']
        c = Content(title=title, link=link, description=description, user=user)
        c.save()


    content_list = []
    # 1.- Lista de contenidos
    content = Content.objects.all()
    sorted_list = sorted(content, key=attrgetter('date'), reverse=True)
    for i in sorted_list[:NLASTOBJ]:   # Ponemos en la respuesta los últimos objetos añadidos
        content_list.append(i)
    # 2.- Cargar la plantilla
    if request.user.is_authenticated:
        template = loader.get_template('LoVisto/index.html')
    else:
        template = loader.get_template('LoVisto/index_not.html')

    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': content_list,
    }
    # 4.- Renderizar
    return HttpResponse(template.render(context, request))


def get_content(request, content):

    # POST
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        link = request.POST['link']
        c = Content(title=title, link=link, description=description,
                    positive=0, negative=0, date=timezone.now, num_comment=0,
                    extended_info="", user=request.user.username())
        c.save()

    # GET
    try:
        # 1.- Obtenemos el contenido
        content = Content.objects.get(source=content)
        comment_list = content.comment_set.all()
        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/content.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content': content,
            'comment_list': comment_list
        }
        response = template.render(context, request)

    except Content.DoesNotExist:
        if request.user.is_authenticated:
            # 2.- Cargar la plantilla
            template = loader.get_template('LoVisto/newcontent.html')
            # 3.- Ligar las variables de la plantilla a las variables de python
            context = {
            }
            response = template.render(context, request)
        else:
            response = 'You are not authenticated. <a href="/login">Authentication here</a>'
    return HttpResponse(response)


def all_content(request):
    # 1.- Obtenemos el contenido
    content_list = Content.objects.all()
    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/allcontent.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': content_list,
    }
    # Renderizar
    return HttpResponse(template.render(context, request))


def information(request):
    template = loader.get_template('LoVisto/information.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {}
    # Renderizar
    return HttpResponse(template.render(context, request))

def loged_in(request):
    if request.user.is_authenticated:
        response = "Logged in as \"" + request.user.username + '"'
        # Guardamos el nuevo usuario en nuestra lista de usuarios
        try:
            User.objects.get(user_name=request.user.username)
        except User.DoesNotExist:
            user = User(user_name=request.user.username, password=request.user.password)
            user.save()
    else:
        response = 'You are not authenticated. <a href="/login">Authentication here</a>'
    return HttpResponse(response)


def logout_view(request):
    logout(request)
    template = loader.get_template('LoVisto/logout.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {}
    # Renderizar
    return HttpResponse(template.render(context, request))