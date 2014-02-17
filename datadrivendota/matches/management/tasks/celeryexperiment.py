from time import sleep

import logging
import celery
from celery import task, Task

logger = logging.getLogger(__name__)
# Notes: In order to make things work correctly, you must:
#     1: make sure this module is in your celery imports in the django
#        settings.
#     2: Start a fresh dj shell
#     3: Start a fresh celery worker.
#     2 & 3 are there because of the preloading that both of those tasks do
#         (by looking in 1)


@task
def hello():
    """Returns a string literal."""
    return "Hi!"


@task
def parent():
    print "In parent"
    # Both delay and apply_async() allow for parent release
    child.s().delay()
    # Catching the result and not both allow release
    child.s().delay()
    print "Out of parent"


@task
def child():
    print "In child"
    sleep(.1)
    print "Out of child"
    #  forms a subtask that allows the parent to be freed before the child
    #  starts.
    # .s()


#Returns nonetype error.  I do n
# @todo: What the hell is this task? Can it maybe be renamed or deleted?
# --kit 2014-02-16
class PingerPonger(Task):
    abstract = True

    def run(self, strng="test", *args, **kwargs):
        print "1"
        self.ping(self, strng, *args, **kwargs)
        self.pong(self, strng, *args, **kwargs)

    def ping(self, strng='Ping', *args, **kwargs):
        print strng

    def pong(self, strng='Pong', *args, **kwargs):
        print strng


class TestTask(PingerPonger):
    def ping(self, strng='Hi!', *args, **kwargs):
        print strng

    def pong(self, strng='Bye!', *args, **kwargs):
        print strng


class ApiFollower(celery.Task):

    def __call__(self, *args, **kwargs):
        """In celery task this function call the run method, here you can
        set some environment variable before the run of the task"""
        self.x = kwargs['x']
        self.y = kwargs['y']
        logger.info("Starting to run")
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        #exit point of the task whatever is the state
        logger.info("Ending run")
        logger.info(self.x)
        logger.info(self.y)
        pass
