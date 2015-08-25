# coding: utf-8

from wtforms import Form
from wtforms.validators import AnyOf, DataRequired
from wtforms.fields import FormField, StringField, IntegerField

http_methods_validator_options = {
    'values': ['GET', 'HEAD', 'POST', 'PUT',
               'DELETE', 'TRACE', 'OPTIONS', 'PATCH'],
    'message': 'HTTP Method not valid.',
}


class RequestForm(Form):
    body = StringField('')
    headers = StringField('')


class ResponseForm(Form):
    body = StringField('', [DataRequired()])
    headers = StringField('', [DataRequired()])
    status_code = IntegerField('', [DataRequired()])


class MockForm(Form):
    method = StringField('', [DataRequired(),
                              AnyOf(**http_methods_validator_options)])
    path = StringField('',)
    request = FormField(RequestForm)
    response = FormField(ResponseForm)
