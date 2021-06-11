#!/usr/bin/python3

# Simple XML parser for Aemet XML predictions
# César Borao Moratinos. 2021
# Based on "Youtube XML parser": Jesus M. Gonzalez-Barahona
# SAT subject (Universidad Rey Juan Carlos)
#

from xml.sax.handler import ContentHandler
from xml.sax import make_parser


class AemetHandler(ContentHandler):

    def __init__(self):

        self.inContent = False
        self.inDay = False
        self.inTemp = False
        self.inSens = False
        self.inHumedad = False
        self.content = ""
        self.tempMax = ""
        self.tempMin = ""
        self.sensMax = ""
        self.sensMin = ""
        self.humMax = ""
        self.humMin = ""
        self.date = ""
        self.days = []
        self.general = {}

    def startElement(self, name, attrs):

        if name == 'nombre':
            self.inContent = True
        elif name == 'provincia':
            self.inContent = True
        elif name == 'copyright':
            self.inContent = True
        elif name == 'dia':
            self.date = attrs.get('fecha')
            self.inDay = True

        elif self.inTemp:

            if name == 'maxima':
                self.inContent = True
            elif name == 'minima':
                self.inContent = True

        elif self.inSens:
            if name == 'maxima':
                self.inContent = True
            elif name == 'minima':
                self.inContent = True

        elif self.inHumedad:
            if name == 'maxima':
                self.inContent = True
            elif name == 'minima':
                self.inContent = True

        elif self.inDay:
            if name == 'temperatura':
                self.inTemp = True
            elif name == 'sens_termica':
                self.inSens = True
            elif name == 'humedad_relativa':
                self.inHumedad = True

    def endElement(self, name):

        if name == 'nombre':
            self.general['municipio'] = self.content
            self.content = ""
            self.inContent = False

        elif name == 'provincia':
            self.general['provincia'] = self.content
            self.content = ""
            self.inContent = False

        elif name == 'copyright':
            self.general['copyright'] = self.content
            self.content = ""
            self.inContent = False

        elif name == 'dia':
            self.inDay = False
            self.days.append({'tempMin': self.tempMin,
                              'tempMax': self.tempMax,
                              'sensMin': self.sensMin,
                              'sensMax': self.sensMax,
                              'humMin': self.humMin,
                              'humMax': self.humMax,
                              'fecha': self.date})

        elif name == 'temperatura':
            self.inTemp = False
        elif name == 'sens_termica':
            self.inSens = False
        elif name == 'humedad_relativa':
            self.inHumedad = False
        elif self.inTemp:
            if name == 'maxima':
                self.tempMax = self.content
                self.content = ""
                self.inContent = False
            elif name == 'minima':
                self.tempMin = self.content
                self.content = ""
                self.inContent = False

        elif self.inSens:
            if name == 'maxima':
                self.sensMax = self.content
                self.content = ""
                self.inContent = False
            elif name == 'minima':
                self.sensMin = self.content
                self.content = ""
                self.inContent = False

        elif self.inHumedad:
            if name == 'maxima':
                self.humMax = self.content
                self.content = ""
                self.inContent = False
            elif name == 'minima':
                self.humMin = self.content
                self.content = ""
                self.inContent = False

    def characters(self, chars):
        if self.inContent:
            self.content = self.content + chars


class Aemet:

    def __init__(self, stream):
        self.parser = make_parser()
        self.handler = AemetHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

    def predicciones(self):
        return self.handler.general, self.handler.days
