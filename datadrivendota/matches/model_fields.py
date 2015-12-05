from django.db import models


class ReplayFragmentField(models.FileField):

    def __init__(
        self,
        verbose_name=None,
        name=None,
        upload_to='playermatchsummaries/replays/',
        storage=None,
        **kwargs
    ):
        kwargs['null'] = True
        kwargs['upload_to'] = 'playermatchsummaries/replays/'
        kwargs['blank'] = True
        super(ReplayFragmentField, self).__init__(verbose_name, name, **kwargs)
