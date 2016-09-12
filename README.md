<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [DataDrivenDota](#datadrivendota)
- [Intro](#intro)
  - [Business Proposition](#business-proposition)
    - [Stretch analogy](#stretch-analogy)
  - [Napkin math](#napkin-math)
  - [Design Concept](#design-concept)
- [Setup](#setup)
  - [RabbitMQ](#rabbitmq)
  - [Redis](#redis)
  - [Postgres](#postgres)
  - [Grunt](#grunt)
  - [Necessary environment variables](#necessary-environment-variables)
  - [Initial Data Acquisition](#initial-data-acquisition)
    - [Superuser](#superuser)
    - [Client Data](#client-data)
    - [API Data](#api-data)
  - [Data Sources](#data-sources)
- [How data gets in](#how-data-gets-in)
        - [Heroes](#heroes)
        - [Players](#players)
        - [Teams](#teams)
        - [Leagues](#leagues)
        - [Matches](#matches)
- [Workflow Support](#workflow-support)
- [Todos](#todos)
  - [Accounts refactor](#accounts-refactor)
  - [Animations import](#animations-import)
  - [Error Propagation in Tasks](#error-propagation-in-tasks)
    - [Current workaround](#current-workaround)
- [Footnotes](#footnotes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# DataDrivenDota


# Intro

## Business Proposition

The business concept behind DDD is about filling a known market niche.  Dota is a complicated game with abundant data, but
 1. no one does a good job of visualizing the data well
  * people pay for the existing bad visualization
 2. it is hard to feel in control of one's progress
  * feeling in control minimizes frustration & improves happiness
  * progress is incentivized by the eSports theme Valve pushes
  * Hypothesis: community toxicity is like road rage: it stems from lack of communication and control.  Providing more levers may improve the community.

### Stretch analogy
Magic the Gathering is a game with complimentary modes: multiplayer is a social game, but requires sync actions and multiple people.  Deckbuilding, theorycrafting, and analysis are solo/async activities.  These two modes together are what allow Magic to replicate and saturate so successfully.  They provide:
 1. a finite state machine
  * (playing or thinking or talking about Magic)
 2. that admits several different world configurations
  * (how many people are there, how sync is your action)
 3. that is mutually reinforcing
  * (playing gathers data for theorycrafting gathers fodder for new decks/play)
 4. that provides emotional payoff
  * (feeling like you really understand or feeling the thrill of victory)
 5. that incentivizes more play

Dota 2 has a multiplayer mode that is highly successful, and has been growing the hairs of community discussion and media.  However, there is no analytic toolkit that quite counts as a single-player mode.  We want to build that, and capitalize on the success of the medium

## Napkin math

We know that Dotabuff, the main existing stat site, employs 3 full time people and 3 part time people.  Assuming they are only paying average US salary (and not dev salary), that 4.5*50K = $225K/yr to cover salary.  Half of that revenue would be more than sufficient to justify this project.

We know that the player base was 6M 2 years ago (or so), and is ~11M now.  0.1% (1 in 1000) of the player base paying $2.49./mo = $22K/mo if $0.49 goes to expenses.  (This is about 10-15 server hours/user/mo.)  22K/mo = $242K/yr, which is sufficient to justify the project.

Amazing case: 1/100 players is $2.42M/yr.  (According to extra credits, in freemium games about 1 in 100 players is a "whale" that spends money profligately.)

Magic Christmasland case: 1/10 players = $24.2M/yr.

Obviously this all varies with price, but dotabuff charges $6/mo.

## Design Concept

DDD is a data acquisition and visualization platform that seeks to mirror Valve's API data.  This reliance on a foreign API leads to some design quirks:

 1. because new data can show up in the API before our database, we need to be accomodating of incomplete data.
 2. because incomplete data causes problems, we need to true-up our understanding regularly.
 3. overall, we seek convergence: we won't get the full view of the world at any given time, but we want the system to trend toward a complete view.

Implementationally, this has a few implications:

 1. The uniqueness criterion we get is a steam_id (the number valve uses to identify various objects).  Everything else might be blank.
 2. We have some tasks we want to run when they can, like the API data access.  We use celery for this.
 3. We use celery tasks to regularly check in on the data, ensure its integrity (thus the 'integrity' queue), and call new tasks as needed.

Keeping this convergence theme in mind will help in understanding why the code works the way it does.

# Setup

Make a new virtualenv with

`mkvirtualenv <name>`

then git clone the repo to your favorite directory with

`git clone --recursive https://github.com/bwarren2/datadrivendota`

(This will also clone the submodules we use.)  Then install the requirements with `pip install -r requirements/local.txt` from inside repo_root.


We need to set up a few backing services:
 * A [RabbitMQ](https://www.rabbitmq.com/install-debian.html) instance (for celery tasks)
 * A [Redis](http://redis.io/topics/quickstart) instance for short-term persistence (like sleeving API responses)
 * A [postgres](https://wiki.postgresql.org/wiki/Detailed_installation_guides) instance with database for long-term persistence

## RabbitMQ

After setup, put your access URI in the CLOUDAMQP_URL env var.  (This name matches the heroku config var for the addon we use.)

## Redis

After setup, put your access URI in the REDISTOGO_URL env var.  (This name matches the heroku config var for the addon we use.)

## Postgres

After installation, we need to make a database

`su postgres`

`postgres=# create database datadrivendota;`

Then we have to do migrations.  Annoyingly, we are using third party libraries that do not respond well to a blanket `python datadrivendota/manage.py migrate`; auth users are expected to exist when they don't and badness ensues.

Currently, the way to get up from zero is:

`> python datadrivendota/manage.py  migrate sites`

`> python datadrivendota/manage.py  migrate auth`

`> python datadrivendota/manage.py  migrate`

The first two will make progress before erroring, and the last will run to completion.*

Now we have a database, but it is (mostly) empty.  We'll fill it during Initial Data Acquisition later; existing data migrations only add a couple perms and a sample player.

## Grunt

We use grunt for local less compilation.  Install with `npm install`.

## Necessary environment variables

Under 12 Factor, resources are connected by environment URIs.  DDD expects a whole bunch of these:

```
# Celery (tasks) configuration
CELERYD_CONCURRENCY=            2
CELERY_IGNORE_RESULT=           False
CELERYD_TASK_SOFT_TIME_LIMIT=   90
CELERY_REDIS_MAX_CONNECTIONS=   40
BROKER_POOL_LIMIT=              1
CELERYD_TASK_TIME_LIMIT=        60
VALVE_RATE=                     .5/s
RESULT_EXPIRY_RATE=             600
BROKER_CONNECTION_TIMEOUT=      6
CLOUDAMQP_URL=                  <redacted>
REDISTOGO_URL=                  <redacted>

# Valve data access
STEAM_API_KEY=                  <redacted>

# Celery queue
RABBITMQ_USER=                  wattrabbit
RABBITMQ_VHOST=                 testvhost
RABBITMQ_PASS=                  <redacted>

# Django
DJANGO_PROJECT_DIR=             <redacted>
DJANGO_SETTINGS_MODULE=         datadrivendota.settings.local
DEBUG=                          TRUE
SECRET_KEY=                     <redacted>

# Postgres
DATABASE_URL=                   <redacted>

# Charting analytics
KEEN_WRITE_KEY=                 <redacted>
KEEN_PROJECT_ID=                <redacted>
KEEN_READ_KEY=                  <redacted>
KEEN_API_URL=                   https://api.keen.io

# User interaction
INTERCOM_API_SECRET=            <redacted>

# Payments
STRIPE_PUBLIC_KEY=              <redacted>
STRIPE_SECRET_KEY=              <redacted>

# Mailing backend
MAILGUN_SMTP_PORT=              <redacted>
MAILGUN_SMTP_LOGIN=             <redacted>
MAILGUN_SMTP_SERVER=            <redacted>
MAILGUN_SMTP_PASSWORD=          <redacted>

# Aws handles static assets
AWS_SECRET_ACCESS_KEY=          <redacted>
AWS_ACCESS_KEY_ID=              <redacted>
AWS_STORAGE_BUCKET_NAME=        <redacted>
```

Storing settings in a repo is a bad policy, so talk to Ben about getting unredacted copy.  Putting these in the postactivate of your virtualenv is recommended.

## Initial Data Acquisition

### Superuser

In order to access the admin etc, you will need to make a superuser.

`python datadrivendota/manage.py  createsuperuser`

### Client Data

There are certain files only accessible from the game client, and we commit these into json_files/ .  How to get them is a different project.

`fab json_populate` should merge these data files into the database and hit foreign assets for things like images.  If you are starting from a blank DB, also run `python datadrivendota/manage.py  importRoles`; this should only need to happen once in the life of your db.

You can test that this worked by starting a shell:

`fab shell`

then poking at the data models:

`from heroes.models import Hero, Ability, HeroDossier`

`Hero.objects.all().count()`

`HeroDossier.objects.all().count()`

`Ability.objects.all().count()`

Note: Not all heroes will have dossiers, because sometimes heroes are in the data files before they are fully released.

### API Data

With the basic info established, we can hit the API to add more.

You should have the [heroku toolbelt](https://toolbelt.heroku.com/) installed, and we can start a celery worker with `foreman start worker`.  That worker will wait for tasks and chew through the rabbitmq queue as long as it is up.

To put a task in the queue, start a shell (`fab shell`) and start by making a player (this is my steam id):

```
from players.models import Player
p, _ = Player.objects.update_or_create(steam_id=66289584, defaults={'updated': True})
# updated is a flag for tasks to know which players are intended to be in repeat scrapes.

# Then import my matches
from players.management.tasks import UpdateClientPersonas, MirrorPlayerData
from datadrivendota.management.tasks import ApiContext

c = ApiContext()
c.account_id = 66289584
c.matches_desired = 50
UpdateClientPersonas().s().delay(api_context=c)
MirrorPlayerData().s().delay(api_context=c)
```

If you look back into the worker tab, it should be happily running along.  If you want to do some basic monitoring of the celery worker itself, try `flower  --broker=<your amqp url, ex $CLOUDAMQP_URL>`.

Starting a web process (`fab devserver`) and hitting the player page for my id ([http://127.0.0.1:8000/players/66289584/](http://127.0.0.1:8000/players/66289584/)), my games should show up!  Click one of the hero faces to see that game's detail.

## Data Sources

How exactly each type of data gets into our system is a bit complex, because there are many different avenues and the system is only _eventually_ convergent.

Getting initial data in this eventually-convergent system can be tricky, because some frequent tasks expect there to have been a run of long running tasks, and the long running tasks may expect that the fast tasks have run, etc.  But this is not a deadlock!  Each cycle through the task list makes progress, so the question is how to conveniently run a few iterations.

For now, there is a process for initial data which takes about ~5 minutes.  Here's a list of tasks.  Run the first block in a shell with an active worker, wait for the queues to clear (`fab rabbit_list`) or for the workers to stop actively processing tasks (`flower`, connect to [127.0.0.1:5555/monitor](127.0.0.1:5555/monitor)) whichever comes first, and then repeat with the next block.  Some api calls may fail and go into a long retry loop; if there are tasks in the queue but the workers are not working, you can probably flush the queues (`fab rabbit_reset`).  Allowing better error propagation in tasks is a todo.


```

from items.management.tasks import MirrorItemSchema
from leagues.management.tasks.league import UpdateLeagues
MirrorItemSchema().s().delay()

// Wait for the queue to clear
UpdateLeagues().s().delay(matches=100, leagues=[2733])

// Wait for the queue to clear
from leagues.management.tasks import MirrorRecentLeagues as tsk
tsk().s().delay()
from teams.management.tasks import MirrorRecentTeams as tsk
tsk().s().delay()
from matches.management.tasks import CheckMatchIntegrity as tsk
tsk().s().delay()

// Wait for the queue to clear
from matches.management.tasks import UpdateMatchValidity as tsk
tsk().s().delay()

// Most of the work is done!  Things past here are optional.

// This should be fast.  It
from heroes.management.tasks import CheckHeroIntegrity as tsk
tsk().s().delay()

// This gets the official names for pro players.
// It works on all the currently imported players affiliated with a team, so
// it might take a while if you have lots of pro games.  *For starting dev,
// you don't need it,* but it is here for completeness.
from players.management.tasks import MirrorProNames as tsk
tsk().s().delay()
```

The last task does not need to run all the way throufh; you should see results if any of its subtasks have finished.

Now, you should be able to see:
 * leagues in [127.0.0.1:8000/leagues](127.0.0.1:8000/leagues), and inspect their games.
 * teams in [127.0.0.1:8000/teams](127.0.0.1:8000/teams), and inspect their rosters.
 * pro players in [127.0.0.1:8000/players](127.0.0.1:8000/players).
 * heroes in [127.0.0.1:8000/heroes](127.0.0.1:8000/heroes).

That's it!

# How data gets in

Eventually-convergent systems can be hard to understand, because for a given kind of data it can be unclear what necessary chain of conditions will be advanced by which tasks to ensure a pipeline of new data.  So let's list it out.  Keep in mind that it is possible for elements to enter the system with only a steam_id if they are needed to support other data, for example a hero being created to import a match (before we get the data to make the hero ourselves).

##### Heroes

These come from data files in the game client itself and are manually extracted to json.  We then run management commands (or the fabric wrapper to run them all) to push their statistics to the db.

##### Players

We automatically poll the API regularly for any player that is a client.  Creating a player with `updated=True` sets that player up to always have their matches stream in.

##### Teams

We automatically poll for league games, and get team stubs to support that import.  There is a recency task that takes all the teams that played recently (or are on the upcoming schedule) and looks for their other matches.

##### Leagues

We have a periodic task that imports stubs for all the leagues, (lacking logos etc,) and pulls 1 match for them.  The more-frequent update task looks for any recent games and sees if there are more.  (This avoids reimporting a ton of games for every league all the time.)

##### Matches

This one is complicated, because matches are kind of an apex data object: they incorporate teams, and players, and heroes, and items, etc.

Matches can be classified a bit.  Matches with a skill level ('skill' between 1 and 3) for heroes come from the hero skill data task (infrequently polling).  Tournament grade matches (skill 4) come from the leagues updating.  Everything else comes from tracking players.  In short, there is no particular "get da matches" process (aside from manual requests, which are available in all things).


# Workflow Support

With a populated db, here are the possible support processes to have up:

 * Server (`fab devserver`)  # `foreman start web` does not server statics well locally
 * Celery Worker (`foreman start worker`)  #
 * Celery beat Worker (`foreman start beatnik_worker`)  # Useful for work that touches the streaming league task, for example.
 * Celery Monitor  (`flower`)  # Sets up on 127.0.0.1:5555 by default
 * Grunt Less Compilation  (`grunt`)  # For monkeying with the styles

#Todos

## Accounts refactor
The old model of accounts was useful for a closed-off site, but needs to be refactored for a primarily-public, secondarily-subscriber model.

## Animations import
Importing cast and attack animations is currently a manual hit to a foreign service, combined with some regexing to reformat.  This is annoying, but is only necessary on patch update.

## Error Propagation in Tasks
Because so many processes involve chaining through an API call, there is lots of sensitivity to the API call working.  Unfortunately, it sometimes does not, and we don't propagate errors well.  In order to avoid api calls going into a long retry loop, eventually failing, and killing the chain they were a part of, we need a convention for how errors propagate and are handled.


### Current workaround
Some helpful regexen:
```
.png[ ]* => @
(?<=[a-zA-Z])[ ]+(?=Melee|[0-9]) => @
Melee => 0
(?<=[0-9])[ ]+(?=[0-9]) => @
```

# Footnotes

*:

Here is a sample of what the output looks like, minus some deprecation warnings.

    > python datadrivendota/manage.py  migrate sites

    Operations to perform:
      Apply all migrations: sites
    Running migrations:
      Rendering model states... DONE
      Applying sites.0001_initial... OK
    Traceback (most recent call last):
      File "datadrivendota/manage.py", line 10, in <module>
        execute_from_command_line(sys.argv)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/__init__.py", line 338, in execute_from_command_line
        utility.execute()
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/__init__.py", line 330, in execute
        self.fetch_command(subcommand).run_from_argv(self.argv)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/base.py", line 390, in run_from_argv
        self.execute(*args, **cmd_options)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/base.py", line 441, in execute
        output = self.handle(*args, **options)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/commands/migrate.py", line 225, in handle
        emit_post_migrate_signal(created_models, self.verbosity, self.interactive, connection.alias)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/core/management/sql.py", line 280, in emit_post_migrate_signal
        using=db)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/dispatch/dispatcher.py", line 201, in send
        response = receiver(signal=self, sender=sender, **named)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/contrib/auth/management/__init__.py", line 82, in create_permissions
        ctype = ContentType.objects.db_manager(using).get_for_model(klass)
      File "/home/ben/.virtualenvs/ddd-upgrade/local/lib/python2.7/site-packages/django/contrib/contenttypes/models.py", line 78, in get_for_model
        "Error creating new content types. Please make sure contenttypes "
    RuntimeError: Error creating new content types. Please make sure contenttypes is migrated before trying to migrate apps individually.

    > python datadrivendota/manage.py  migrate auth

    Operations to perform:
      Apply all migrations: auth
    Running migrations:
      Rendering model states... DONE
      Applying contenttypes.0001_initial... OK
      Applying contenttypes.0002_remove_content_type_name... OK
      Applying auth.0001_initial... OK
      Applying auth.0002_alter_permission_name_max_length... OK
      Applying auth.0003_alter_user_email_max_length... OK
      Applying auth.0004_alter_user_username_opts... OK
      Applying auth.0005_alter_user_last_login_null... OK
      Applying auth.0006_require_contenttypes_0002... OK

    > python datadrivendota/manage.py  migrate

    Operations to perform:
      Synchronize unmigrated apps: pipeline, mptt, corsheaders, staticfiles, debug_toolbar, utils, messages, devserver, debug_toolbar_line_profiler, django_forms_bootstrap, health, payments, template_profiler_panel, rest_framework, storages, bootstrapform, tagging, template_timings_panel
      Apply all migrations: leagues, sessions, players, admin, items, matches, sites, auth, teams, blog, default, contenttypes, accounts, guilds, heroes
    Synchronizing apps without migrations:
      Creating tables...
        Creating table corsheaders_corsmodel
        Creating table payments_eventprocessingexception
        Creating table payments_event
        Creating table payments_transfer
        Creating table payments_transferchargefee
        Creating table payments_customer
        Creating table payments_currentsubscription
        Creating table payments_invoice
        Creating table payments_invoiceitem
        Creating table payments_charge
        Creating table tagging_tag
        Creating table tagging_taggeditem
        Running deferred SQL...
      Installing custom SQL...
    Running migrations:
      Rendering model states... DONE
      Applying players.0001_initial... OK
      Applying accounts.0001_initial... OK
      Applying accounts.0002_auto_20150420_1410... OK
      Applying admin.0001_initial... OK
      Applying blog.0001_initial... OK
      Applying default.0001_initial... OK
      Applying default.0002_add_related_name... OK
      Applying default.0003_alter_email_max_length... OK
      Applying guilds.0001_initial... OK
      Applying heroes.0001_initial... OK
      Applying items.0001_initial... OK
      Applying leagues.0001_initial... OK
      Applying teams.0001_initial... OK
      Applying leagues.0002_auto_20150419_1128... OK
      Applying matches.0001_initial... OK
      Applying sessions.0001_initial... OK


Api resource list:

http://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/?key=09A6226940EB67F6D844B7D7E3A54186

Other person's example:
http://dotadb.azurewebsites.net/heroes/32/riki#


## Adding processes to ecs

Ensure you are using the right ECS creds and cluster:

>  cat ~/.ecs/config

Make a repo online.

SAMPLE: use the actual values from repo creation

> aws ecr get-login --region us-west-2

> docker build -t ddd-omniworker -f dockerdockerdocker/Dockerfiles/omniworker  .
> docker tag ddd-omniworker:latest <number>.dkr.ecr.us-west-2.amazonaws.com/ddd-omniworker:latest

> docker push <number>.dkr.ecr.us-west-2.amazonaws.com/ddd-omniworker:latest

Sometimes the push must be retried due to network failures.


(Set up creds in ~/.ecs/config)
`ecs-cli up --keypair ecs-usw2-keypair --capability-iam --size 1 --instance-type t2.medium`
`ecs-cli compose --file docker-secrets.yaml service up`

### Bringing it down on ECS
`ecs-cli compose --file docker-secrets.yaml service down`
`ecs-cli down --force`


Note on ECS docker-compose format:  this is fine:
```
omniworker:
  image: 288612536250.dkr.ecr.us-west-2.amazonaws.com/ddd-omniworker:latest
  env_file:
   - ../envs/.env-production
  command: celery worker --app=datadrivendota -E -Q default,api_call,integrity,rpr,db_upload,parsing,botting  --loglevel=INFO  -c 6 --workdir=datadrivendota
  mem_limit: 536870912
  log_driver: "syslog"
  log_opt:
    syslog-address: "udp://logs.papertrailapp.com:28310"
```

this is not:

```
version: '2'
services:
  omniworker:
    image: 288612536250.dkr.ecr.us-west-2.amazonaws.com/ddd-omniworker:latest
    env_file:
     - ../envs/.env-production
    command: celery worker --app=datadrivendota -E -Q default,api_call,integrity,rpr,db_upload,parsing,botting  --loglevel=INFO  -c 6 --workdir=datadrivendota
    mem_limit: 536870912
    log_driver: "syslog"
    log_opt:
      syslog-address: "udp://logs.papertrailapp.com:28310"
```
