from django.http import HttpResponse, Http404
from .models import Content, User, Comment, Vote
from django.template import loader
from operator import attrgetter
from django.contrib.auth import logout
from django.utils import timezone

# Create your views here.
NLASTOBJ = 10    # Number of the last objects that will be presented on the principal page
NLASTAPORT = 5   # Number of the last aportations that will be presented on the principal page


def index(request):
    if request.method == 'POST':
        print('ppppppppppppaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaajjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
        if request.POST['votation'] == '1':
            user = User.objects.get(user_name=request.user.username)
            print("Content-id = " + str(request.POST['content_id']))
            content = Content.objects.get(id=request.POST['content_id'])
            if request.POST['vote'] == 'like':
                v = Vote(user=user, content=content, vote=1)
            else:
                v = Vote(user=user, content=content, vote=-1)
            v.save()
            print('OJO QUE YA ESTAMOS VOTANDOOOOOOOO')
        else:
            user = User.objects.get(user_name=request.user.username)
            title = request.POST['title']
            description = request.POST['description']
            link = request.POST['link']
            c = Content(title=title, link=link, description=description, user=user)
            print(str(user.password) + 'ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')
            c.save()


    # 1.- Lista de contenidos
    content = Content.objects.all()

    # --> Lista de las últimas aportaciones del usuario
    user_list = []
    content_user_list = []
    for i in content:   # Ponemos en la respuesta los últimos objetos añadidos
        if i.user.user_name == request.user.username:
            user_list.append(i)
    for i in user_list[:NLASTAPORT]:
        content_user_list.append(i)

    # --> Lista de las ultimas aportaciones de todos los usuarios
    content_list = []
    sorted_list = sorted(content, key=attrgetter('date'), reverse=True) # Ordenamos por fecha
    print(sorted_list)
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
        'content_user_list': content_user_list
    }
    # 4.- Renderizar
    return HttpResponse(template.render(context, request))


def get_content(request, content):

    # POST
    if request.method == 'POST':
        user = User.objects.get(user_name=request.user.username)
        content1 = Content.objects.get(title=content)
        body = request.POST['body']
        c = Comment(user=user, body=body, content=content1)
        c.save()

    # GET
    try:
        # 1.- Obtenemos el contenido
        content = Content.objects.get(title=content)
        comment_list = content.comment_set.all()
        sorted_list = sorted(comment_list, key=attrgetter('date'), reverse=True)  # Ordenamos por fecha

        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/content.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content': content,
            'comment_list': sorted_list
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


def user_view(request):

    if request.user.is_authenticated:
        # 1.- Lista de contenidos
        content = Content.objects.all()

        # Lista de comentarios
        user = User.objects.get(id=request.user.id)
        print(str(user) + '++++++++++++++++++++++++++++++++++++++++++++++++++ñññllllllllllllllllllllllllllllllllllllllllllllllll')
        comment_list = user.comment_set.all()
        print(comment_list)
        comment_user_list = []
        for i in comment_list:
            if i.user.id == request.user.id:
                comment_user_list.append(i)
        print(comment_user_list)
        # --> Lista de las últimas aportaciones del usuario
        content_list = []
        for i in content:   # Ponemos en la respuesta los últimos objetos añadidos
            print(str(i.user.id) + ' : ' + str(request.user.id))
            if i.user.id == request.user.id:
                content_list.append(i)
            print(content_list)
        sorted_list = sorted(content_list, key=attrgetter('date'), reverse=True) # Ordenamos por fecha

        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/user.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content_list': sorted_list,
            'comment_list': comment_list
        }
    else:
        template = loader.get_template('LoVisto/notAuthenticated.html')
        context = {}
    # Renderizar
    return HttpResponse(template.render(context, request))


def all_content(request):
    # 1.- Obtenemos el contenido
    content_list = Content.objects.all()
    sorted_list = sorted(content_list, key=attrgetter('date'), reverse=True) # Ordenamos por fecha

    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/allcontent.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': sorted_list,
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