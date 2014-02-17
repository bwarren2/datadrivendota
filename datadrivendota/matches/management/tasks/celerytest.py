from celery import task, group
from time import sleep
# celery = Celery(
#     'tasks',
#     broker='amqp://guest:guest@localhost//',
#     backend='amqp'
# )
# celery = Celery('tasks')


@task(rate_limit='100/s')
def mymul(x, y):
    return x*y


@task
def mysum(lst):
    return sum(lst)


@task
def add(x, y):
    return x+y


@task
def sleepy_add(x, y):
    sleep(10)
    return x+y


@task
def mul(x, y):
    return x*y

if __name__ == '__main__':

    # Basic delay usage

    add.delay(4, 4)
    # Returns Async result.  Catch it.

    # Like so
    process = add.delay(4, 4)

    process.status
    # Ready/Pending/Etc.  Not callable.

    process.ready()
    # True/False

    process.get()
    # 8

    # Note the usage of a tuple of args
    process = add.apply_async((4, 4), )

    # Add options after arguments.  This kicks off in 5 seconds.
    process = add.apply_async((4, 4), countdown=5)

    # Note: this is just a signature.  It is not something that is running yet.
    # Note: you need to use apply async rather than subtask for the countdown
    # arg
    sig = add.subtask((4, 4), countdown=10)
    process = sig.delay()
    process.successful()  # takes 10 seconds

    sig = add.s(4)
    copy = sig.clone(args=(5, ), kwargs={'debug': True})
    copy  # mymod.celerytest.add(5, 4, debug=True)

    # Implicit chain grouped with pipes and immediately gotten.
    (add.s(4, 4) | add.s(5) | add.s(2))().get()
    # Or deferred
    sig = (add.s(4, 4) | add.s(5) | add.s(2))
    g = sig()  # Called it
    g.get()

    # You can see why something failed with .info
    p = add.s(2, 2, debug=True).delay()
    p.info

    g = group(add.s(i, i) for i in xrange(0, 10))
    proc = g()  # Apply the group.  Use apply async, alternatively
    proc.completed_count()  # How many are done?  There is no .status.
    proc.waiting()  # Am I waiting?
    proc.get()  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18] Note list return.
