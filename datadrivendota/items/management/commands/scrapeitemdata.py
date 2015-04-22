from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from tempfile import TemporaryFile
from json import loads
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
from items.models import Item, ItemAttributes
from collections import defaultdict


class Command(BaseCommand):

    def handle(self, *args, **options):
        id_dict = defaultdict(dict)
        edited_json = {}

        # Get the item IDs from the local file.
        with open('json_files/items.json') as f:
            internal_json = loads(f.read())

        try:
            # Purge a junk field
            del internal_json['DOTAAbilities']['Version']
        except KeyError:
            # Probably manually deleted.
            pass

        for name, internal_dict in internal_json['DOTAAbilities'].iteritems():
            name = name[5:]
            edited_json[name] = internal_dict

        internal_json = edited_json
        for name, information_dict in internal_json.iteritems():
            print name
            id = information_dict['ID']
            id_dict[name]['internal_data'] = information_dict
            id_dict[name]['id'] = id
            i = Item.objects.get_or_create(steam_id=id)[0]
            i.save()
        #Get the JSON item data feed.
        #url = 'http://www.dota2.com/jsfeed/itemdata'
        with open('json_files/item_detail.json') as f:
            site_json = loads(f.read())

        #Do some cleanup
        for item in site_json['itemdata']:
            for attr in site_json['itemdata'][item]:
                if attr in ['attrib', 'desc']:
                    linelist = []
                    split_items = site_json[
                        'itemdata'
                    ][item][attr].split('<br />\n')
                    for line in split_items:
                        l = ' '.join(
                            BeautifulSoup(line).getText(separator=u' ').split()
                        )
                        linelist.append(l.replace("<br />", ""))
                    if attr == 'desc':
                        site_json['itemdata'][item][attr] = '\n'.join(linelist)
                    elif attr == 'attrib':
                        site_json['itemdata'][item][attr] = linelist
                    else:
                        exit("WTF!?")
                if attr in ['notes']:
                    insert_value = site_json[
                        'itemdata'
                    ][item][attr].replace("<br />", "")
                    site_json['itemdata'][item][attr] = insert_value

        for item in id_dict:
            if item != 'diffusal_blade_2' and item != 'tango_single':
                try:
                    id_dict[item]['external_data'] = site_json[
                        'itemdata'
                    ][item]
                except KeyError:
                    print "Could not find external data for {0}".format(item)

        for clean_item, data_dict in id_dict.iteritems():
            print clean_item

            #ugh, bad data conventions.
            if "dagon" in clean_item:
                continue

            try:
                item = Item.objects.get(steam_id=id_dict[clean_item]['id'])
                item.name = id_dict[clean_item]['external_data']['dname']
                item.internal_name = clean_item
                item.quality = id_dict[clean_item]['external_data']['qual']
                item.description = id_dict[clean_item]['external_data']['desc']
                item.notes = id_dict[clean_item]['external_data']['notes']
                item.cost = id_dict[clean_item]['external_data']['cost']
                if id_dict[clean_item]['external_data']['mc'] == 'false':
                    mc = 0
                else:
                    mc = id_dict[clean_item]['external_data']['mc']
                if id_dict[clean_item]['external_data']['cd'] == 'false':
                    cd = 0
                else:
                    cd = id_dict[clean_item]['external_data']['cd']
                item.mana_cost = mc
                item.cooldown = cd
                item.lore = id_dict[clean_item]['external_data']['lore']
                item.created = id_dict[clean_item]['external_data']['created']
                item.slug_name = slugify(
                    id_dict[clean_item]['external_data']['dname']
                )

                url = (
                    'http://media.steampowered.com'
                    '/apps/dota2/images/items/%s_lg.png' % item
                )
                lg_image = urlopen(url)
                tempfile = TemporaryFile()
                tempfile.write(lg_image.read())
                tempfile.seek(0)
                tempfile.read()
                filename = slugify(item.name)+'_large.png'
                item.mugshot.save(filename, File(tempfile))
                url = (
                    'http://media.steampowered.com'
                    '/apps/dota2/images/items/%s_eg.png' % item
                )
                eg_image = urlopen(url)
                tempfile = TemporaryFile()
                tempfile.write(eg_image.read())
                tempfile.seek(0)
                tempfile.read()
                filename = slugify(item.name)+'_small.png'
                item.thumbshot.save(filename, File(tempfile))

            except KeyError:
                item = Item.objects.get(steam_id=id_dict[clean_item]['id'])
                item.name = slugify(clean_item.replace("_", " ")).title()
                item.internal_name = clean_item
                item.slug_name = slugify(item.name)

                if 'recipe' in clean_item:
                    url = (
                        'http://media.steampowered.com'
                        '/apps/dota2/images/items/recipe_lg.png'
                    )
                    lg_image = urlopen(url)
                    tempfile = TemporaryFile()
                    tempfile.write(lg_image.read())
                    tempfile.seek(0)
                    tempfile.read()
                    filename = slugify(item.name)+'_large.png'
                    item.mugshot.save(filename, File(tempfile))
                    url = (
                        'http://media.steampowered.com'
                        '/apps/dota2/images/items/recipe_lg.png'
                    )
                    eg_image = urlopen(url)
                    tempfile = TemporaryFile()
                    tempfile.write(eg_image.read())
                    tempfile.seek(0)
                    tempfile.read()
                    filename = slugify(item.name)+'_small.png'
                    item.thumbshot.save(filename, File(tempfile))

        for clean_item in sorted(id_dict):
            print "SKIPPING Comp " + clean_item
            try:
                for attrib in id_dict[clean_item]['external_data']['attrib']:
                    ItemAttributes.objects.get_or_create(
                        item=Item.objects.get(internal_name=clean_item),
                        attribute=attrib
                    )
            except KeyError:
                pass
            except Item.DoesNotExist:
                print clean_item
