from celery import task
from time import sleep

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
