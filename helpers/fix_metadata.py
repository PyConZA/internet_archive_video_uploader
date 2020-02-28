from internetarchive import get_item

with open('urls', 'r') as f:
    for line in f.readlines():
        old_pycon_url = 'https://za.pycon.org'
        pycon2018_url = 'https://2018.za.pycon.org'
        ia_url, fake_pycon_url = line.split(' - ')
        ia_item = ia_url.replace('https://archive.org/details/', '')
        item = get_item(ia_item)
        description = item.item_metadata['metadata']['description']
        old_description = description
        if old_pycon_url not in description:
            print('Skipping', ia_url)
            continue
        description = description.replace(old_pycon_url, pycon2018_url)
        if old_description != description:
            print('Modifying', ia_url)
            added_date = item.item_metadata['metadata']['publicdate']
            itemdate = added_date.split('T')[0]
            print(itemdate)
            #continue
            item.modify_metadata({'description': description})
            item.modify_metadata({'date': itemdate})
