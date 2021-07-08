import json


class Youtube:
    yt_info = {}

    def parser(self, info):
        self.yt_info['titulo'] = info['title']
        self.yt_info['nombre_autor'] = info['author_name']
        self.yt_info['link_autor'] = info['author_url']

        self.yt_info['video'] = info['html']

    def __init__(self, stream):
        info = json.load(stream)
        self.parser(info)

    def info(self):
        return self.yt_info
