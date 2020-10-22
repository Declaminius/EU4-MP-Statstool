from werkzeug.routing import BaseConverter
from flask import request

class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(value for value in values)

def redirect_url(default='main.home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)
