from django.core.management.base import BaseCommand
from django.core.files import File
from django.utils.text import slugify
from tempfile import TemporaryFile
from json import loads
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
from items.models import Item, ItemAttributes, ItemComponents


class Command(BaseCommand):

    def handle(self, *args, **options):

#        import pdb; pdb.set_trace()
        id_dict = {}
        #Get the item IDs from the local file.
        with open('items.json') as f:
            id_json = loads(f.read())
            for item in id_json['items']:
                id = item['id']
                name=item['name']
                id_dict[name]=id
                i = Item.objects.get_or_create(steam_id=id)[0]
                i.save()
        #Get the JSON item data feed.
        #url = 'http://www.dota2.com/jsfeed/itemdata'
        with open('item_detail.json') as f:
            json = loads(f.read())

        #Do some cleanup
        for item in json['itemdata']:
            for attr in json['itemdata'][item]:
                if attr in ['attrib','desc']:
                    linelist = []
                    for line in json['itemdata'][item][attr].split('<br />\n'):
                        l = ' '.join(BeautifulSoup(line).getText(separator=u' ').split())
                        linelist.append(l.replace("<br />",""))
                    if attr == 'desc':
                        json['itemdata'][item][attr] = '\n'.join(linelist)
                    elif attr == 'attrib':
                        json['itemdata'][item][attr] = linelist
                    else:
                        exit("WTF!?")
                if attr in ['notes']:
                    json['itemdata'][item][attr] = json['itemdata'][item][attr].replace("<br />","")

        clean_items={}
        for item in json['itemdata']:
            if item != 'diffusal_blade_2' and item != 'tango_single':
                id = id_dict[item]
                clean_items[item] = json['itemdata'][item]
                clean_items[item]['id']=id

#
        for clean_item in clean_items:
            print clean_item
            item = Item.objects.get(steam_id=clean_items[clean_item]['id'])
            item.name = clean_items[clean_item]['dname']
            item.internal_name = clean_item
            item.quality = clean_items[clean_item]['qual']
            item.description = clean_items[clean_item]['desc']
            item.notes = clean_items[clean_item]['notes']
            item.cost = clean_items[clean_item]['cost']
            if clean_items[clean_item]['mc'] == 'false':
                mc = 0
            else: mc = clean_items[clean_item]['mc']
            if clean_items[clean_item]['cd'] == 'false':
                cd = 0
            else: cd = clean_items[clean_item]['cd']
            item.mana_cost = mc
            item.cooldown = cd
            item.lore = clean_items[clean_item]['lore']
            item.created = clean_items[clean_item]['created']
            item.slug_name = slugify(clean_items[clean_item]['dname'])

            url = 'http://media.steampowered.com/apps/dota2/images/items/%s_lg.png' % item
            lg_image = urlopen(url)
            tempfile = TemporaryFile()
            tempfile.write(lg_image.read())
            tempfile.seek(0)
            tempfile.read()
            filename = slugify(item.name)+'_large.png'
            item.mugshot.save(filename, File(tempfile))
            url = 'http://media.steampowered.com/apps/dota2/images/items/%s_eg.png' % item
            eg_image = urlopen(url)
            tempfile = TemporaryFile()
            tempfile.write(eg_image.read())
            tempfile.seek(0)
            tempfile.read()
            filename = slugify(item.name)+'_large.png'
            item.thumbshot.save(filename, File(tempfile))


        for clean_item in sorted(clean_items):
            print "Comp "+ clean_item
            if clean_items[clean_item]['components'] is not None:
                for comp in clean_items[clean_item]['components']:
                    if comp[0:6]!='recipe':
                        print comp
                        ItemComponents.objects.get_or_create(product=Item.objects.get(internal_name=clean_item),ingredient=Item.objects.get(internal_name=comp))
            if clean_items[clean_item]['attrib'] !=['']:
                for attrib in clean_items[clean_item]['attrib']:
                    ItemAttributes.objects.get_or_create(item=Item.objects.get(internal_name=clean_item),attribute=attrib)
