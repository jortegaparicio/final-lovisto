from django.http import JsonResponse, HttpResponse
from .models import Content, User, Comment, Vote
from django.template import loader
from operator import attrgetter
from django.contrib.auth import logout, login, authenticate
import urllib.request
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .aemet_parser import Aemet
from .YTparser import Youtube
from .redditParser import Reddit
from . import data
from django.shortcuts import render

NLASTOBJ = 10    # Number of the last objects that will be presented on the principal page
NLASTAPORT = 5   # Number of the last aportations that will be presented on the principal page

"""
Este método se encarga del sistema de votación de la API, el cual no permite que un usuario
haga más de una votación por cada publicación
"""
def votation(request):
    user = User.objects.get(id=request.user.id)
    content = Content.objects.get(id=request.POST['content_id'])
    v = Vote.objects.filter(user=user, content=content).first()

    if request.POST['vote'] == 'like':
        if v is None:
            v = Vote(user=user, content=content, vote=1)
            content.positive += 1
            content.save()
            v.save()
        else:
            if v.vote != 1:
                v.vote = 1
                content.positive += 1
                content.negative -= 1
                content.save()
                v.save()
    else:
        if v is None:
            v = Vote(user=user, content=content, vote=-1)
            content.negative += 1
            content.save()
            v.save()
        else:
            if v.vote != -1:
                v.vote = -1
                content.negative += 1
                content.positive -= 1
                content.save()
                v.save()

"""
Método encargado de analizar los recursos categorizados como no reconocidos
"""
def unknownResource(link):
    try:
        htmlStream = urllib.request.urlopen(link)
        soup = BeautifulSoup(htmlStream, 'html.parser')
        ogTitle = soup.find('meta', property='og:title')

        if ogTitle:
            ogImage = soup.find('meta', property='og:image')

            if ogImage:
                res = data.OG.format(titulo=ogTitle['content'], imagen=str(ogImage['content']))
            else:
                title = soup.title.string

                if title is not None:
                    res = data.TITLE.format(titulo=str(title))
                else:
                    res = data.NO_INFO.format()

        else:

            title = soup.title.string

            if title is not None:
                res = data.TITLE.format(titulo=title)
            else:
                res = data.NO_INFO.format()
    except:
        res = data.NO_INFO.format()

    return res

"""
Método que se encarga del formato de las publicaciones de AEMET tal y como se indica en el enunciado
"""
def processAemetInfo(path):
    resource = path.split(sep='/')[-1]
    resource_id = resource.split(sep='-id')[-1]
    url = "https://www.aemet.es/xml/municipios/localidad_" + resource_id + ".xml"

    xmlStream = urllib.request.urlopen(url)
    aemet = Aemet(xmlStream)
    general, days = aemet.predicciones()

    info = data.HEADER.format(municipio=general['municipio'],
                                provincia=general['provincia'])

    for day in days:
        info = info + data.DATE.format(tempMin=day['tempMin'],
                                      tempMax=day['tempMax'],
                                      sensMin=day['sensMin'],
                                      sensMax=day['sensMax'],
                                      humMin=day['humMin'],
                                      humMax=day['humMax'],
                                      fecha=day['fecha'])

    info = info + data.COPYRIGHT.format(copy=general['copyright'],
                                        url="www.aemet.es/" + resource)
    return info

"""
Método que se encarga de las publicaciones de youtube tal y como se nos indica en el enunciado
"""
def processYT(path):
    video_id = path.split(sep='=')[-1]
    url = 'https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=' + video_id

    jsonStream = urllib.request.urlopen(url)
    video = Youtube(jsonStream)
    information = video.info()

    aux = information['video']
    aux = aux.replace('="200"', '="560"')
    aux = aux.replace('="113"', '="315"')

    info = data.VIDEO.format(titulo=information['titulo'],
                             video=aux,
                             nombre_autor=information['nombre_autor'],
                             link_autor=information['link_autor'],
                             url=video_id)

    return info

"""
Método que se encarga de analizar las publicaciones procedentes de reddit tal y como se nos indica en el enunciado
"""
def processReddit(path):
    reddit_id = path.split(sep='/')[-3]
    url = 'https://www.reddit.com/r/django/comments/' + reddit_id + '/.json'
    jsonStreamReddit = urllib.request.urlopen(url)
    reddit = Reddit(jsonStreamReddit)
    information = reddit.info()
    url = information['url']
    pattern = re.compile("https://i.redd.it/.+")

    if pattern.match(url):
        info = data.REDD_IMG.format(titulo=information['titulo'],
                                    subreddit=information['subreddit'],
                                    url=url,
                                    aprobacion=information['aprobacion'])
    else:
        info = data.REDD_TEXT.format(titulo=information['titulo'],
                                     subreddit=information['subreddit'],
                                     texto=information['texto'],
                                     url=url,
                                     aprobacion=information['aprobacion'])
    return info

"""
Método que se encarga de detectar los recursos que son conocidos y de mandarlos a procesar
"""
def knownResource(link):
    res = None
    o = urlparse(link)
    netloc = o.netloc
    path = o.path

    if netloc == 'www.aemet.es' or netloc == 'aemet.es':
        pattern = re.compile("/es/eltiempo/prediccion/municipios/.+-id.+")
        # Si es un formato de recurso conocido
        if pattern.match(path):
            res = processAemetInfo(path)

    if netloc == 'www.youtube.com' or netloc == 'youtube.com':
        path = link.split(sep='/')[-1]
        pattern = re.compile("watch\?v=.+")
        if pattern.match(path):
            res = processYT(path)

    if netloc == 'www.reddit.com' or netloc == 'reddit.com':
        pattern = re.compile("/r/.+/comments/.+/.+/")
        if pattern.match(path):
            res = processReddit(path)

    return res


"""
Método encargado de distribuir el flujo entre los recursos reconocidos y los no reconocidos
"""
def analizeLink(link):
    res = knownResource(link)
    if res is None:
        res = unknownResource(link)
    # Get title
    return res

"""
Método encargado de la gestión de usuarios
"""
def login_r(request):
    username = request.POST['username']
    password = request.POST['password']
    user_auth = authenticate(request, username=username, password=password)

    if user_auth is not None:
        login(request, user_auth)
        try:
            User.objects.get(user_name=username)
        except User.DoesNotExist:
            user = User(user_name=username, password=password)
            user.save()

"""
Método encargado de cambiar el css cuando el usuario esté registrado
"""
def chMode(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        cssDir = user.mode
        if cssDir == 'css/LoVisto/dark.css':
            user.mode = 'css/LoVisto/style.css'
        else:
            user.mode = 'css/LoVisto/dark.css'
        user.save()

"""
Método encargado de obtener el css de un usuario
"""
def getMode(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        cssDir = user.mode
    else:
        cssDir = 'css/LoVisto/style.css'

    return cssDir

"""
Método que se encarga de la página principal de la API
"""
def index(request):

    if request.method == 'POST':
        if request.POST['action'] == 'vote':
            votation(request)
        elif request.POST['action'] == 'logout':
            logout(request)
        elif request.POST['action'] == 'login':
            login_r(request)
        elif request.POST['action'] == 'changeMode':
            chMode(request)
        else:
            user = User.objects.get(user_name=request.user.username)
            title = request.POST['title']
            description = request.POST['description']
            link = request.POST['link']
            info = analizeLink(link)
            c = Content(title=title, link=link, description=description, user=user, extended_info=info)
            c.save()


    # 1.- Lista de contenidos
    content = Content.objects.all()
    content_list = []
    content_user_list = []

    # Lista de las últimas aportaciones del usuario
    if request.user.is_authenticated:
        user_list = []

        for i in content:   # Ponemos en la respuesta los últimos objetos añadidos
            if i.user.user_name == request.user.username:
                user_list.append(i)
        for i in user_list[:NLASTAPORT]:
            content_user_list.append(i)

    # Lista de las ultimas aportaciones de todos los usuarios
    sorted_list = sorted(content, key=attrgetter('id'), reverse=True) # Ordenamos por id
    for i in sorted_list[:NLASTOBJ]:   # Ponemos en la respuesta los últimos objetos añadidos
        content_list.append(i)

    one = None
    two = None
    three = None

    if len(content_list) > 3:
        one = content_list[0]
        two = content_list[1]
        three = content_list[2]

    # Obtenemos el modo de vista
    cssDir = getMode(request)

    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/index.html')


    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': content_list,
        'content_user_list': content_user_list,
        'one': one,
        'two': two,
        'three': three,
        'cssDir': cssDir
    }
    # 4.- Renderizar
    return HttpResponse(template.render(context, request))

"""
Métooo encargado de la página de cada publicación, el cual deja un enlace al sitio web
que contiene la publicación
"""
def get_content(request, content_id):

    # POST
    if request.method == 'POST':
        if request.POST['action'] == 'vote':
            votation(request)
        elif request.POST['action'] == 'logout':
            logout(request)
        elif request.POST['action'] == 'login':
            login_r(request)
        elif request.POST['action'] == 'changeMode':
            chMode(request)
        else:
            user = User.objects.get(user_name=request.user.username)
            content = Content.objects.get(id=content_id)
            body = request.POST['body']
            c = Comment(user=user, body=body, content=content)
            content.num_comment += 1
            content.save()
            c.save()

    # GET
    try:
        # 1.- Obtenemos el contenido
        content = Content.objects.get(id=content_id)
        comment_list = content.comment_set.all()
        sorted_comment_list = sorted(comment_list, key=attrgetter('date'), reverse=True)  # Ordenamos por id

        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/content.html')

        # 3.- Ligar las variables de la plantilla a las variables de python
        content2 = Content.objects.all()
        sorted_list = sorted(content2, key=attrgetter('id'), reverse=True)  # Ordenamos por id

        one = None
        two = None
        three = None

        if len(sorted_list) > 3:
            one = sorted_list[0]
            two = sorted_list[1]
            three = sorted_list[2]

        # Obtenemos el modo de vista
        cssDir = getMode(request)

        context = {
            'content': content,
            'comment_list': sorted_comment_list,
            'one': one,
            'two': two,
            'three': three,
            'cssDir': cssDir
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

"""
Método encargado de la página de usuario de la API
"""
def user_view(request):

    if request.method == 'POST':
        if request.POST['action'] == 'logout':
            logout(request)
        elif request.POST['action'] == 'login':
            login_r(request)
        elif request.POST['action'] == 'changeMode':
            chMode(request)

    if request.user.is_authenticated:

        # 1.- Lista de contenidos
        content = Content.objects.all()
        sorted_list = sorted(content, key=attrgetter('id'), reverse=True)  # Ordenamos por id

        one = None
        two = None
        three = None

        if len(sorted_list) > 3:
            one = sorted_list[0]
            two = sorted_list[1]
            three = sorted_list[2]

        # Lista de comentarios
        user = User.objects.get(id=request.user.id)
        comment_list = user.comment_set.all()
        comment_user_list = []

        for i in comment_list:
            if i.user.id == request.user.id:
                comment_user_list.append(i)

        # Lista de las aportaciones del usuario
        content_list = []

        for i in content:   # Ponemos en la respuesta los últimos objetos añadidos
            if i.user.id == request.user.id:
                content_list.append(i)

        sorted_list = sorted(content_list, key=attrgetter('date'), reverse=True) # Ordenamos por fecha

        # Lista de los votos del usuario
        vote_list = user.vote_set.all()
        vote_user_list = []

        for i in vote_list:
            if i.user.id == request.user.id:
                vote_user_list.append(i)

        cssDir = getMode(request)

        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/user.html')

        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content_list': sorted_list,
            'comment_list': comment_list,
            'vote_list' : vote_user_list,
            'one': one,
            'two': two,
            'three': three,
            'cssDir': cssDir
        }
    else:
        template = loader.get_template('LoVisto/user.html')
        context = {}

    return HttpResponse(template.render(context, request))

"""
Método encargado de la página de todos los contenidos de los usuarios
"""
def all_content(request):

    if request.method == 'POST':
        if request.POST['action'] == 'logout':
            logout(request)
        elif request.POST['action'] == 'login':
            login_r(request)
        elif request.POST['action'] == 'changeMode':
            chMode(request)


    if request.GET.get('format') == "xml":
        content_list = Content.objects.all().order_by('date').reverse()
        context = {"content_list": content_list}
        response = render(request, 'LoVisto/file.xml', context=context, status=200)
        response['Content-Type'] = 'application/xml'
        return response


    if request.GET.get('format') == "json":
        content_list = Content.objects.all().order_by('date').reverse()
        jsonFile = {}

        for i in range(0, len(content_list), 1):
            content = content_list[i]
            info = {'title': content.title, 'link': content.link}
            jsonFile['Contenido ' + str(i)] = info

        return JsonResponse(jsonFile)

    # 1.- Obtenemos el contenido
    content_list = Content.objects.all()
    sorted_list = sorted(content_list, key=attrgetter('id'), reverse=True) # Ordenamos por id

    one = None
    two = None
    three = None

    if len(sorted_list) > 3:
        one = sorted_list[0]
        two = sorted_list[1]
        three = sorted_list[2]

    # Obtenemos el modo de vista
    cssDir = getMode(request)

    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/allcontent.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': sorted_list,
        'one': one,
        'two': two,
        'three': three,
        'cssDir': cssDir
    }
    # Renderizar
    return HttpResponse(template.render(context, request))

"""
Método encargado de dar funcionalidad a la página de información dee la red social
"""
def information(request):

    if request.method == 'POST':
        if request.POST['action'] == 'logout':
            logout(request)
        elif request.POST['action'] == 'login':
            login_r(request)
        elif request.POST['action'] == 'changeMode':
            chMode(request)

    content_list = Content.objects.all()
    sorted_list = sorted(content_list, key=attrgetter('id'), reverse=True) # Ordenamos por id

    one = None
    two = None
    three = None

    if len(sorted_list) > 3:
        one = sorted_list[0]
        two = sorted_list[1]
        three = sorted_list[2]

    # Obtenemos el modo de vista
    cssDir = getMode(request)

    template = loader.get_template('LoVisto/information.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'one': one,
        'two': two,
        'three': three,
        'cssDir': cssDir
    }
    # Renderizar
    return HttpResponse(template.render(context, request))
