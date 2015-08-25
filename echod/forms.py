from wtforms import Form
from wtforms.validators import AnyOf, InputRequired
from wtforms.fields import FormField, StringField, IntegerField

http_methods_validator_options = {
    'values': ['GET', 'HEAD', 'POST', 'PUT',
               'DELETE', 'TRACE', 'OPTIONS', 'PATCH'],
    'message': 'HTTP Method not valid.',
}


class HeadersForm(Form):
    content_type = StringField('')
    accept = StringField('')


class RequestForm(Form):
    body = StringField('', [InputRequired])
    headers = FormField(HeadersForm)


class ResponseForm(Form):
    body = StringField('', [InputRequired])
    headers = FormField(HeadersForm)
    status_code = IntegerField('', [InputRequired])


class MockForm(Form):
    method = StringField('', [InputRequired,
                              AnyOf(**http_methods_validator_options)])
    path = StringField('',)
    request = FormField(RequestForm)
    response = FormField(ResponseForm)
