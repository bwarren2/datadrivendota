from django.db import models
from django.db.models import Q


class PublicManager(models.Manager):

    def get_queryset(self):
        return super(PublicManager, self).get_queryset().filter(
            Q(publicity=0)  # Bad hardcoding, but circumvents circular import
        )


class LoginManager(models.Manager):

    def get_queryset(self):
        return super(LoginManager, self).get_queryset().filter(
            Q(publicity=0) | Q(publicity=1)
            # Bad hardcoding, but circumvents circular import
        )


class PrivateManager(models.Manager):

    def get_queryset(self):
        return super(PrivateManager, self).get_queryset().filter(
            Q(publicity=0) | Q(publicity=1) | Q(publicity=2)
            # Bad hardcoding, but circumvents circular import
        )
