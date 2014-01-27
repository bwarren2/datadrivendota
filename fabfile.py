from fabric.api import local


def test(suite="all"):
    if suite == 'all':
        local('python -W ignore datadrivendota/manage.py test integration_tests')
    else:
        local('python -W ignore datadrivendota/manage.py test {suite}'.format(suite=suite))

def hp():
    local('git push heroku master')
    local(collect_static())
    local(heroku_migrate())

def heroku_migrate():
    local(heroku_run(migrate()))

def migrate():
    return "python datadrivendota/manage.py migrate --no-initial-data"

def collect_static():
    return 'python datadrivendota/manage.py collectstatic --settings=datadrivendota.settings.production --noinput'


def scrape_valve_heroes():
    return 'python datadrivendota/manage.py scrapeheroes'


def scrape_hero_faces():
    return 'python datadrivendota/manage.py scrapeloreandmugshot'


def scrape_dossiers():
    return 'python datadrivendota/manage.py importHeroStats --file hero_stats.txt'


def get_hero_seed_local():
    local(scrape_valve_heroes())
    local(scrape_hero_faces())
    local(scrape_dossiers())


def heroku_run(str):
    return "heroku run "+str


def get_hero_seed_heroku():
    local(heroku_run(scrape_valve_heroes()))
    local(heroku_run(scrape_hero_faces()))
    local(heroku_run(scrape_dossiers()))


def generate_heroku_static_pages():
    local("python datadrivendota/manage.py generate_static_error_pages --settings=datadrivendota.settings.production")
