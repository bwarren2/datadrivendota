from fabric.api import local


def scrape_valve_heroes():
    local('python datadrivendota/manage.py scrapeheroes')


def scrape_hero_faces():
    local('python datadrivendota/manage.py scrapeloreandmugshot')


def scrape_dossiers():
    local('python datadrivendota/manage.py importHeroStats')


def get_hero_seed():
    scrape_valve_heroes()
    scrape_hero_faces()
    scrape_dossiers()
