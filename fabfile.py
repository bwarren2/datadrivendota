from fabric.api import local


def hp():
    local('heroku push -b https://github.com/ddollar/heroku-buildpack-multi.git')


def scrape_valve_heroes():
    return 'python datadrivendota/manage.py scrapeheroes'


def scrape_hero_faces():
    return 'python datadrivendota/manage.py scrapeloreandmugshot'


def scrape_dossiers():
    return 'python datadrivendota/manage.py importHeroStats'


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
