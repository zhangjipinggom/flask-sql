# -*- coding: utf-8 -*-

from wtforms import Form, StringField, validators


class LoginForm(Form):
    username = StringField('Username:', validators=[validators.required(), validators.Length(min=8, max=30),
                                                    validators.Regexp(r'ilovebme', 0, 'not allowed name')])
    password = StringField('Password:', validators=[validators.required(), validators.Length(min=1, max=30)])
    email = StringField('Email:', validators=[validators.optional(), validators.Length(min=0, max=50)])
