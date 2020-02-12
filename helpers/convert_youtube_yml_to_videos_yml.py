import sys
import os

import yaml

def convert_yaml(youtube_yaml):
    """Convert the Debian youtube uploading yaml to videos.yml for the IA uploaded"""
    # Lots of assumptions about the youtube data here
    output = {}
    output['default_metadata'] = {'mediatype': 'movies',
                                  'licenseurl': "http://creativecommons.org/licenses/by/3.0/",
                                  'language': "eng",
                                  'collection': 'PyConZA',
                                  'subject': "pyconza; pyconza2019; python"}
    videos = []
    output['videos'] = videos
    for yt_video in youtube_yaml['videos']:
        this_video = {}
        this_video['done'] = False
        this_video['upload'] = False
        this_video['metadata'] = {}
        this_video['filename'] = yt_video['file']
        this_video['metadata']['title'] = yt_video['title']
        desc = yt_video['description']
        if r'\n' in desc:
            desc = desc.replace(r'\n', '\n')
        if '\\\n    \\ ' in desc:
            desc = desc.replace('\\\n    \\ ','\n    ')
        author, ourdesc = desc.split('At: PyConZA 2019')
        author = author.split('by ')[1].split('\n')[0]
        this_video['metadata']['creator'] = author
        identifier = os.path.split(yt_video['file'])[-1]
        identifier = os.path.splitext(identifier)[0]
        identifier = identifier.replace(' ', '-').replace('_', '-')
        this_video['identifier'] = f'pyconza2019-{identifier}'
        if 'Scheduled start' in ourdesc:
            ourdesc, start = ourdesc.split('Scheduled start: ')
            this_video['metadata']['date'] = start.strip().split(' ')[0]
        else:
            this_video['metadata']['date'] = 'Unknown'
        this_video['metadata']['description'] = ourdesc.strip()
        videos.append(this_video)
    return output
        

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as f:
        youtube_data = yaml.safe_load(f)

    output = convert_yaml(youtube_data)
    with open('videos.yml', 'w') as f:
        yaml.dump(output, f, default_flow_style=False, default_style='', allow_unicode=True)

