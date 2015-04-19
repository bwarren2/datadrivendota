from fabric.api import local


def test(suite="all"):
    if suite == 'all':
        local(
            'python -W ignore datadrivendota/manage.py  test integration_tests'
        )
    elif suite == 'apps':
        local(
            'python datadrivendota/manage.py test accounts guilds heroes items leagues matches players teams utils --settings=datadrivendota.settings.test'
        )

    else:
        local(
            'python datadrivendota/manage.py test {suite} --settings=datadrivendota.settings.test'.format(
                suite=suite
            )
        )


def push():
    local('git push origin master')
    local('git push heroku master')


def deploy():
    local('git push origin master')
    collect_static()
    local('git push heroku master')


def hp():
    local('git push heroku master')
    local(collect_static())
    local(heroku_migrate())


def rabbit_reset():
    return local('sh convenience\ files/rabbit_reset')


def rabbit_list():
    return local('sudo rabbitmqctl list_queues')


def heroku_migrate():
    return local("heroku run python datadrivendota/manage.py migrate --no-initial-data")


def migrate():
    return local("python datadrivendota/manage.py migrate --no-initial-data")


def collect_static():
    command = (
        'python datadrivendota/manage.py collectstatic'
        ' -i bootstrap'
        ' --settings=datadrivendota.settings.production --noinput'
    )
    local(command)


def scrape_valve_heroes():
    return local('python datadrivendota/manage.py scrapeheroes')


def scrape_hero_faces():
    return local('python datadrivendota/manage.py scrapeloreandmugshot')


def scrape_dossiers():
    return local(
        'python datadrivendota/manage.py '
        'importHeroStats --file hero_stats.txt'
    )


def generate_heroku_static_pages():
    local(
        "python datadrivendota/manage.py "
        "generate_static_error_pages "
        "--settings=datadrivendota.settings.production"
    )
