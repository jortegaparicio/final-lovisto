from django.http import HttpResponse
from .models import Content, User, Comment, Vote
from django.template import loader
from operator import attrgetter
from django.contrib.auth import logout
import urllib.request
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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
                res = '<div class="og"> <p>' + str(ogTitle['content']) + '</p> <img src="' + str(ogImage['content']) + '"></div>'
            else:
                title = soup.title.string
                if title is not None:
                    res = '<div class="html"><p>' + str(title) + '</p></div>'
                else:
                    res = '<div class html="html"><p>Información extendida no disponible</p></div>'
        else:
            title = soup.title.string
            if title is not None:
                res = '<div class="html"><p>' + str(title) + '</p></div>'
            else:
                res = '<div class html="html"><p>Información extendida no disponible</p></div>'
    except:
        res = '<div class html="html"><p>Información extendida no disponible</p></div>'

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

def processAemetInfo(o):
    resource = o.path.split(sep='/')[-1]
    municipio = resource.split(sep='-id')[0]
    resource_id = resource.split(sep='-id')[-1]
    url = "https://www.aemet.es/xml/municipios/localidad_" + resource_id + ".xml"

    xmlStream = urllib.request.urlopen(url)
    aemet = Aemet(xmlStream)
    general, days = aemet.predicciones()

    info = data.CABECERA.format(municipio=general['municipio'],
                                provincia=general['provincia'])

    for day in days:
        info = info + data.DAY.format(tempMin=day['tempMin'],
                                      tempMax=day['tempMax'],
                                      sensMin=day['sensMin'],
                                      sensMax=day['sensMax'],
                                      humMin=day['humMin'],
                                      humMax=day['humMax'],
                                      fecha=day['fecha'])

    info = info + data.COPYRIGHT.format(copy=general['copyright'],
                                        url="www.aemet.es/" + resource)


def knownResource(link):
    res = None
    o = urlparse(link)
    if o.netloc == 'www.aemet.es' or o.netloc == 'aemet.es':
        pattern = re.compile("/es/eltiempo/prediccion/municipios/.+-id.+")
        print(o.path)
        # Si es un formato de recurso conocido
        if pattern.match(o.path):
            print('\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('Hemos reconocido el recurso')
            res = processAemetInfo(o)
        else:
            print('No hemos reconocido el recurso')
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


def index(request):
    if request.method == 'POST':
        if request.POST['votation'] == '1':
            votation(request)
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

    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/index.html')


    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': content_list,
        'content_user_list': content_user_list,
        'one': one,
        'two': two,
        'three': three
    }
    # 4.- Renderizar
    return HttpResponse(template.render(context, request))


def get_content(request, content_id):

    # POST
    if request.method == 'POST':
        if request.POST['votation'] == '1':
            print('************************************************************************')
            user = User.objects.get(id=request.user.id)
            content = Content.objects.get(id=request.POST['content_id'])
            print(str(user))
            print(str(content))
            v = Vote.objects.filter(user=user, content=content).first()
            print(str(v))
            print('Hay que votar')
            if request.POST['vote'] == 'like':
                if v is None :
                    v = Vote(user=user, content=content, vote=1)
                    content.positive += 1
                    content.save()
                    v.save()
                    print("No hay ninún voto a este contenido")
                else:
                    if v.vote != 1:
                        v.vote = 1
                        content.positive += 1
                        content.negative -= 1
                        content.save()
                        v.save()
                    print("Ya hay algun vvoto de este contenido")
                print('HAY QUE AÑADIR UN LIKE')
            else:
                if v is None :
                    v = Vote(user=user, content=content, vote=-1)
                    content.negative += 1
                    content.save()
                    v.save()
                    print("No hay ninún voto a este contenido")
                else:
                    if v.vote != -1:
                        v.vote = -1
                        content.negative += 1
                        content.positive -= 1
                        content.save()
                        v.save()
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
        sorted_list = sorted(comment_list, key=attrgetter('id'), reverse=True)  # Ordenamos por id

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
            'comment_list': sorted_list,
            'one': one,
            'two': two,
            'three': three
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

        # 2.- Cargar la plantilla
        template = loader.get_template('LoVisto/user.html')
        # 3.- Ligar las variables de la plantilla a las variables de python
        context = {
            'content_list': sorted_list,
            'comment_list': comment_list,
            'vote_list' : vote_user_list,
            'one': one,
            'two': two,
            'three': three
        }
    else:
        template = loader.get_template('LoVisto/notAuthenticated.html')
        context = {}
    # Renderizar
    return HttpResponse(template.render(context, request))


def all_content(request):
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
    # 2.- Cargar la plantilla
    template = loader.get_template('LoVisto/allcontent.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'content_list': sorted_list,
        'one': one,
        'two': two,
        'three': three
    }
    # Renderizar
    return HttpResponse(template.render(context, request))


def information(request):
    content_list = Content.objects.all()
    sorted_list = sorted(content_list, key=attrgetter('id'), reverse=True) # Ordenamos por id
    one = None
    two = None
    three = None
    if len(sorted_list) > 3:
        one = sorted_list[0]
        two = sorted_list[1]
        three = sorted_list[2]
    template = loader.get_template('LoVisto/information.html')
    # 3.- Ligar las variables de la plantilla a las variables de python
    context = {
        'one': one,
        'two': two,
        'three': three
    }
    # Renderizar
    return HttpResponse(template.render(context, request))

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