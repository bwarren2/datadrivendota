from django.contrib import admin
from heroes.models import Hero, Role, Ability, HeroDossier

admin.site.register(Hero)
admin.site.register(Role)
admin.site.register(Ability)
admin.site.register(HeroDossier)
