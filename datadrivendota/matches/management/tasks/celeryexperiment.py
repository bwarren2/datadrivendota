from celery import task, Task
from time import sleep
from celery.registry import tasks

import logging
import celery

logger = logging.getLogger(__name__)

@task
def parent():
    print "In parent"
    child.s().delay()
    print "Out of parent"

@task
def child():
    print "In child"
    sleep(10)
    print "Out of child"


class PingerPonger(Task):
    abstract=True

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
        self.x=kwargs['x']
        self.y=kwargs['y']
        logger.info("Starting to run")
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        #exit point of the task whatever is the state
        logger.info("Ending run")
        logger.info(self.x)
        logger.info(self.y)
        pass

class AddTask(MyCoolTask):

    def run(self,x,y):
        if x and y:
            result=x+y
            logger.info('result = %d' % result)
            return result
        else:
            logger.error('No x or y in arguments')

tasks.register(AddTask)
