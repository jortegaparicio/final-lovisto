# Templates for AEMET
HEADER = """
    <div class="aemet">
        <p>Datos AEMET para {municipio} ({provincia})</p>
        <ul>"""

DATE = """
    <li>{fecha}. Temperatura: {tempMin}/{tempMax}, sensación: {sensMin}/{sensMax}, humedad: {humMin}/{humMax}.</li>"""

COPYRIGHT = """<ul><br>
            <p id=copy_aemet>{copy}<a href="http://{url}"> Página original en AEMET</a></p>
            </div>"""

# Templates for Youtube
VIDEO = """<div class="youtube">
                <p>Video YouTube: {titulo}</p>
                {video}
                <p>Autor: {nombre_autor}. <a href='https://www.youtube.es/watch?v={url}'>
                    Video en Youtube</a>
                </p>
           </div>"""

# Templates for Reddit
REDD_TEXT = """
<div class="reddit">
    <p>Nota Reddit: {titulo}</p>
    <p>{texto}</p>
    <p><a href="{url}">Publicado en {subreddit}</a>. Aprobación: {aprobacion}.</p>
</div>
"""

REDD_IMG = """
<div class="reddit">
    <p>Nota Reddit: {titulo}</p>
    <img src="{url}"  width="560" height="315"  class="img-fluid redd_image">
    <p><a href="{url}">Publicado en {subreddit}</a>. Aprobación: {aprobacion}.</p>
</div>
"""

# Templates for unknown resources
OG = """
<div class="og">
    <p>{titulo}</p>
    <p><img src="{imagen}"  width="560" height="315" class="img-fluid"></p>
</div>
"""

TITLE = """
<div class="title_html">
    <p>{titulo}</p>
</div>
"""

NO_INFO = """
<div class="html">
    <p>Información extendida no disponible</p>
</div>
"""
