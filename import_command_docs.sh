# Pull all the known heroes from valve.  Requires no files, makes an API call.
# Makes things that do not exist, updates names and IDs for existing.
python datadrivendota/manage.py  scrapeheroes

# Gets hero images from steam, takes lore from wiki.  Complains about missing
# images on the command line.  Depends on scrapeheroes, because it looks at existing
# heroes with non-blank names.  Overwrites every time.
python datadrivendota/manage.py  scrapeloreandmugshot

# Relies on a file called 'stats.json' in the home dir.  Extract that file from gcfscape
# on a machine with dota installed, turn the vdf into json with steamodd vdf.loads.
# Overwrites existing every time.  Pulls backswings from wiki.  Might freak if the wiki
# has something unexpected (like the skeleton king -> wraith king change).
python datadrivendota/manage.py  importHeroStats


# You should only be doing this once, to restore from a blank DB.
# python datadrivendota/manage.py  scrapeRoles

# This does some unholy magic.  It takes the ability data jd feed from valve and
# a file called 'abilities.json' in the home dir and weaves the two to get ability data
# and match to the heroes that have them.
# Relies on the above running (because it pulls )
python datadrivendota/manage.py  scrapeabilitydata

# Pull in items.  Does not do components.  Is incomplete.
python datadrivendota/manage.py  scrapeitemdata
