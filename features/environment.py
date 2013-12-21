import threading
from wsgiref import simple_server
from splinter.browser import Browser

from django.test import utils
from django.contrib.auth.models import User

from datadrivendota.wsgi import application

from behave import given, when, then


HOST = 'localhost'
PORT = 8000


def before_all(context):
    utils.setup_test_environment()

    context.server = simple_server.make_server(
        HOST,
        PORT,
        application
    )
    context.thread = threading.Thread(target=context.server.serve_forever)
    context.thread.start()
    context.browser = Browser('phantomjs')

    # Prime the DB
    User.objects.create_user(
        username='kit',
        email='kit@datadrivendota.com',
        password='password'
    )


def after_all(context):
    context.server.shutdown()
    context.thread.join()
    context.browser.quit()


@given(u'I am logged in as "{username}"')
def logged_in(context, username):
    user = User.objects.get(username=username)


@given(u'I go to "{path}"')
def go_to(context, path):
    context.browser.visit("http://{HOST}:{PORT}{path}".format(
        HOST=HOST,
        PORT=PORT,
        path=path
    ))


@when(u'I click on "{text}"')
def click_on(context, text):
    context.browser.click_link_by_text(text)


@then(u'I will see "{text}"')
def see_string(context, text):
    assert text in context.browser.html
