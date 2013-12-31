from urlparse import urljoin

from splinter.browser import Browser
from behave import given, when, then

from django.contrib.auth.models import User


def before_all(context):
    context.browser = Browser('phantomjs')


def after_all(context):
    context.browser.quit()
    context.browser = None


@given(u'the user is "{username}"')
def the_user_is(context, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username=username,
            email="{0}@example.com".format(username),
            password='password'
        )
    full_url = urljoin(context.config.server_url, '/admin/')
    context.browser.visit(full_url)
    context.browser.fill_form({
        'username': username,
        'password': 'password'
    })
    context.browser.find_by_css('input[type=submit]').first.click()
    assert "error" not in context.browser.html


@when(u'the user clicks on "{text}"')
def the_user_clicks_on(context, text):
    context.browser.click_link_by_text(text)


@given(u'the user accesses the url "{path}"')
def the_user_accesses_the_url(context, path):
    full_url = urljoin(context.config.server_url, path)
    context.browser.visit(full_url)


@then(u'the page contains the h1 "{h1}"')
def the_page_contains_the_h1(context, h1):
    page_h1 = context.browser.find_by_tag('h1').first
    assertion_error = "Page should contain h1 {0}, has {1}".format(
        repr(h1),
        repr(page_h1.text)
    )
    assert h1 == page_h1.text, assertion_error
