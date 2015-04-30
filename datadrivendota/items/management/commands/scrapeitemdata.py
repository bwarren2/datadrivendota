from collections import defaultdict
from io import BytesIO
import requests
from json import loads
from BeautifulSoup import BeautifulSoup

from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify

from items.models import Item, ItemAttributes


class Command(BaseCommand):

    def handle(self, *args, **options):

        id_dict = self.name_dict()
        site_json = self.site_json()
        id_dict = self.dict_merge(id_dict, site_json)

        for clean_item, data_dict in id_dict.iteritems():
            print clean_item
            item = self.make_item(clean_item, data_dict)
            self.add_images(item, clean_item)

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

    def load_json(self):
        """
        Do some pre-treatment of the items json file
        """
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

        return edited_json

    def name_dict(self):
        """
        Swap dict indices to be name-keyed.  Useful for merging.
        """
        id_dict = defaultdict(dict)
        for name, information_dict in self.load_json().iteritems():
            id = information_dict['ID']
            id_dict[name]['internal_data'] = information_dict
            id_dict[name]['id'] = id

        return id_dict

    def site_json(self):
        """
        Pre-treat a local copy of the item js feed.
        """
        # Get the JSON item data feed.
        # url = 'http://www.dota2.com/jsfeed/itemdata'
        with open('json_files/item_detail.json') as f:
            site_json = loads(f.read())

        # Do some cleanup
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

        return site_json

    def dict_merge(self, id_dict, site_json):
        """
        Merge the two item dicts on their common name component.
        """
        for item in id_dict:
            try:
                id_dict[item]['external_data'] = site_json['itemdata'][item]
            except KeyError:
                pass
                # print "Could not find external data for {0}".format(item)
        return id_dict

    def get_name(self, name, item):
        """
        Here's the problem:
        Items are keyed an underscore name which is unique.
        But that name is not always the best public name (ex. 'blink')
        But the dname (public name) is not unique)
        So we take the longest one and turn it pretty.
        """
        names = []
        names.append(name)

        try:
            names.append(item['internal_data']['ItemAliases'])
        except:
            pass

        try:
            names.append(item['external_data']['dname'])
        except:
            pass

        names.sort(key=lambda x: len(x), reverse=True)

        return names[0].replace('_', ' ').title()

    def make_item(self, clean_item, data_dict):
        # import pprint
        # pprint.PrettyPrinter().pprint(data_dict)

        item, created = Item.objects.get_or_create(
            steam_id=data_dict['id']
        )

        public_name = self.get_name(clean_item, data_dict)

        item.name = public_name
        item.internal_name = clean_item
        item.slug_name = slugify(public_name)

        try:
            item.quality = data_dict['external_data']['qual']
            item.description = data_dict['external_data']['desc']
            item.notes = data_dict['external_data']['notes']
            item.cost = data_dict['external_data']['cost']

            cd = self.parse_var(
                {'long_name': 'AbilityCooldown', 'short_name': 'cd'},
                data_dict,
                public_name
            )

            mc = self.parse_var(
                {'long_name': 'AbilityManaCost', 'short_name': 'mc'},
                data_dict,
                public_name
            )

            item.mana_cost = mc
            item.cooldown = cd
            item.lore = data_dict['external_data']['lore']
            item.created = data_dict['external_data']['created']

        except KeyError:
            # Some things, like recipes, don't get external data entries.
            pass

        return item

    def add_images(self, item, clean_item):
        if 'recipe' in clean_item:
            url = (
                'http://media.steampowered.com'
                '/apps/dota2/images/items/recipe_lg.png'
            )

            holder = BytesIO(requests.get(url).content)
            _ = holder.seek(0)  # Catch to avoid printing

            filename = slugify(item.name)+'_large.png'
            item.mugshot.save(filename, File(holder))

            url = (
                'http://media.steampowered.com'
                '/apps/dota2/images/items/recipe_lg.png'
            )

            holder = BytesIO(requests.get(url).content)
            _ = holder.seek(0)  # Catch to avoid printing

            filename = slugify(item.name)+'_small.png'
            item.thumbshot.save(filename, File(holder))

        else:
            url = (
                'http://media.steampowered.com'
                '/apps/dota2/images/items/{0}_lg.png'.format(clean_item)
            )
            holder = BytesIO(requests.get(url).content)
            _ = holder.seek(0)  # Catch to avoid printing
            filename = slugify(item.name)+'_large.png'
            item.mugshot.save(filename, File(holder))

            url = (
                'http://media.steampowered.com'
                '/apps/dota2/images/items/{0}_eg.png'.format(clean_item)
            )
            holder = BytesIO(requests.get(url).content)
            _ = holder.seek(0)  # Catch to avoid printing
            filename = slugify(item.name)+'_small.png'
            item.thumbshot.save(filename, File(holder))

    def parse_var(self, var_dct, data_dict, public_name):
        """
        Valve has a bad habit of one-lining with space separation certain vars,
        like cooldown or manacost.  Here, we extract a per-level value.
        """
        try:
            datum = data_dict['internal_data'][var_dct['long_name']]
            if ' ' in datum:
                # print datum.split(' '), list(datum), datum.split(' ') != list(datum)
                # Fuck valve's inlining of multiple values

                try:
                    # Level is last char
                    level = int(public_name[-1])-1  # Level is last char
                    datum = datum.split(' ')[level]
                except ValueError:
                    datum = datum.split(' ')[0]
            else:
                pass
        except KeyError:
            if data_dict['external_data'][var_dct['short_name']] == 'false':
                datum = 0
            else:
                datum = data_dict['external_data'][var_dct['short_name']]

        return int(float(datum))
