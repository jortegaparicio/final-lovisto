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

# Create your views here.
NLASTOBJ = 10    # Number of the last objects that will be presented on the principal page
NLASTAPORT = 5   # Number of the last aportations that will be presented on the principal page



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

def unknownResource(link):
    try:
        res = None
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

def knownResource2(link):
    res = None
    o = urlparse(link)
    print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP')
    if o.netloc == 'www.aemet.es' or o.netloc == 'aemet.es':
        resource = o.path.split(sep='/')[-1]
        municipio = resource.split(sep='-id')[0]
        id = resource.split(sep='-id')[-1]
        print('Municipio = ' + municipio + '  ID = ' + str(id))
        if o.path == '/es/eltiempo/prediccion/municipios/' + str(municipio) + '-id' + str(id):
            print('Lo Estamos reconociendo')

        else:
            print('No lo hemos podido reconocer')
    else:
        print('No lo hemos podido reconocer')
    return res

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


def processYT(path):
    video_id = path.split(sep='=')[-1]
    url = 'https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v=' + video_id

    jsonStream = urllib.request.urlopen(url)
    video = Youtube(jsonStream)
    information = video.info()
    print('IMPORTANTE = ' + information['video'])
    aux = information['video']
    aux = aux.replace('="200"', '="560"')
    aux = aux.replace('="113"', '="315"')
    print('ACCBEFGHIJKLMNÑOPQRSTU = '+aux)

    info = data.VIDEO.format(titulo=information['titulo'],
                             video=aux,
                             nombre_autor=information['nombre_autor'],
                             link_autor=information['link_autor'],
                             url=video_id)
    return info


def processReddit(path):
    print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPAAAAAAAAAAAAAAAAAAAAAAAAAAAAJJJJJJJJJJJJJJJJJJJJJJJJJJJJ' + path)
    reddit_id = path.split(sep='/')[-3]
    print('\n\n' + reddit_id + '\n\n')
    url = 'https://www.reddit.com/r/django/comments/' + reddit_id + '/.json'
    print(path)
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


def knownResource(link):
    res = None
    o = urlparse(link)
    netloc = o.netloc
    path = o.path

    if netloc == 'www.aemet.es' or netloc == 'aemet.es':
        pattern = re.compile("/es/eltiempo/prediccion/municipios/.+-id.+")
        print(path)
        # Si es un formato de recurso conocido
        if pattern.match(path):
            print('\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('Hemos reconocido el recurso')
            res = processAemetInfo(path)
        else:
            print('No hemos reconocido el recurso')

    if netloc == 'www.youtube.com' or netloc == 'youtube.com':
        path = link.split(sep='/')[-1]
        pattern = re.compile("watch\?v=.+")

        if pattern.match(path):
            print('\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(path)
            print('PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPAAAAAAAAAAAAAAAAAAAAAAAAAAAAJJJJJJJJJJJJJJJJJJJJJJJJJJJJ' + path)
            res = processYT(path)

    if netloc == 'www.reddit.com' or netloc == 'reddit.com':
        pattern = re.compile("/r/.+/comments/.+/.+/")
        if pattern.match(path):
            res = processReddit(path)


    return res


def analizeLink(link):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(link)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    res = knownResource(link)
    if res is None:
        res = unknownResource(link)
    # Get title
    return res


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

def chMode(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        print(user.mode)
        cssDir = user.mode
        if cssDir == 'css/LoVisto/dark.css':
            user.mode = 'css/LoVisto/style.css'
        else:
            user.mode = 'css/LoVisto/dark.css'
        user.save()


def getMode(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        print(user.mode)
        cssDir = user.mode
    else:
        cssDir = 'css/LoVisto/style.css'

    return cssDir

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
    sorted_list = sorted(content, key=attrgetter('id'), reverse=True) # Ordenamos por id
    print(sorted_list)
    for i in sorted_list[:NLASTOBJ]:   # Ponemos en la respuesta los últimos objetos añadidos
        content_list.append(i)
    one = None
    two = None
    three = None
    if len(content_list) > 3:
        one = content_list[0]
        two = content_list[1]
        three = content_list[2]

    print(one)
    print(two)
    print(three)

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

        cssDir = getMode(request)

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
        print(str(user) + '++++++++++++++++++++++++++++++++++++++++++++++++++ñññllllllllllllllllllllllllllllllllllllllllllllllll')
        comment_list = user.comment_set.all()
        print(comment_list)
        comment_user_list = []
        for i in comment_list:
            if i.user.id == request.user.id:
                comment_user_list.append(i)
        print(comment_user_list)

        # Lista de las aportaciones del usuario
        content_list = []
        for i in content:   # Ponemos en la respuesta los últimos objetos añadidos
            print(str(i.user.id) + ' : ' + str(request.user.id))
            if i.user.id == request.user.id:
                content_list.append(i)
            print(content_list)
        sorted_list = sorted(content_list, key=attrgetter('date'), reverse=True) # Ordenamos por fecha

        # Lista de los votos del usuario
        vote_list = user.vote_set.all()
        vote_user_list = []
        for i in vote_list:
            if i.user.id == request.user.id:
                vote_user_list.append(i)
        print(vote_user_list)

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
    # Renderizar
    return HttpResponse(template.render(context, request))


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


def json_view(request):
    return None


def loged_in(request):
    if request.user.is_authenticated:
        # Guardamos el nuevo usuario en nuestra lista de usuarios
        try:
            User.objects.get(user_name=request.user.username)
        except User.DoesNotExist:
            user = User(user_name=request.user.username, password=request.user.password)
            user.save()
        template = loader.get_template('LoVisto/login.html')

    else:
        template = loader.get_template('LoVisto/notAuthenticated.html')
    return HttpResponse(template.render({}, request))


def logout_view(request):
    logout(request)
    template = loader.get_template('LoVisto/logout.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {}
    # Renderizar
    return HttpResponse(template.render(context, request))