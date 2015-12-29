from fabric.api import local


def test(suite="all"):
    """ The core test command. """
    if suite == 'all':
        local(
            'python -W ignore datadrivendota/manage.py  test integration_tests'
        )
    elif suite == 'apps':
        local(
            'python datadrivendota/manage.py test '
            'accounts blog guilds health heroes items leagues matches players'
            ' teams utils datadrivendota.tests'
            ' --settings=datadrivendota.settings.test'
        )
    # To ensure discovery of only project tests
    elif suite == 'datadrivendota':
        local(
            'python datadrivendota/manage.py test datadrivendota.tests'
            ' --settings=datadrivendota.settings.test'
        )
    else:
        local(
            (
                'python datadrivendota/manage.py test {suite}'
                ' --settings=datadrivendota.settings.test'
            ).format(suite=suite)
        )


def push():
    """ Move local code to github and production.  No statics. """
    local('git push origin master')
    local('git push heroku master')


def shell(setting="local"):
    """ Open a local shell for CLI access. """
    local(
        (
            'python datadrivendota/manage.py shell '
            '--settings=datadrivendota.settings.{0}'
        ).format(setting)
    )


def devserver(setting="local"):
    """ Start a local server process for testing. """
    local(
        (
            'python datadrivendota/manage.py runserver '
            '--settings=datadrivendota.settings.{0}'
        ).format(setting)
    )


def deploy():
    """ Push to github, statics to s3, push to production. """
    local('git push origin master')
    cs()
    local('git push heroku master')
    local('heroku run python datadrivendota/manage.py migrate')


def rabbit_reset():
    """ Flush the rabbitMQ instance. """
    local('sudo rabbitmqctl stop_app')
    local('sudo rabbitmqctl reset')
    local('sudo rabbitmqctl start_app')


def rabbit_list():
    """ Show the message count in each rabbitmq queue. """
    local('sudo rabbitmqctl list_queues')


def cs():
    """ Push static files to s3."""
    # command = "python move_glyphicons.py"
    # local(command)

    command = (
        'python datadrivendota/manage.py collectstatic'
        ' -i bower_components'
        ' -i css'
        ' -i rest_framework'
        ' -i js'
        ' --settings=datadrivendota.settings.production --noinput'
    )
    local(command)


def json_populate():
    """ Reflect the game client data files in the db. """
    local('python datadrivendota/manage.py  scrapeheroes')
    local('python datadrivendota/manage.py  scrapeloreandmugshot')
    local('python datadrivendota/manage.py  importHeroStats')
    local('python datadrivendota/manage.py  scrapeabilitydata')
    local('python datadrivendota/manage.py  scrapeitemdata')
    local('python datadrivendota/manage.py  importRoles')


def generate_heroku_static_pages():
    """ Create error pages. """
    local(
        "python datadrivendota/manage.py "
        "generate_static_error_pages "
        "--settings=datadrivendota.settings.production"
    )
