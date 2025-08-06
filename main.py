# Jellytion
# The MIT License (MIT)
# Copyright (c) 2025 Jonathan Chiu

import requests
import json
import sys
import re
from datetime import datetime
from configparser import ConfigParser
import os

config = {}
debug = 0
debug = 0
jellyfin_headers = {}
notion_headers = {}

def fetch_config():
    progress = build_progress(0, 1)
    print(progress, 'Fetching config file...')

    config = ConfigParser()

    progress = build_progress(1, 1)
    if os.path.exists('config.ini'):
        config.read('config.ini', encoding='utf-8')
        print(progress)
    elif os.path.exists('config_default.ini'):
        print(progress, 'Failed to fetch config.ini, using config_default.ini.')
        config.read('config_default.ini', encoding='utf-8')
    else:
        print(progress, 'Failed to fetch config file.')
        sys.exit(1)

    progress = build_progress(0, 1)
    print(progress, 'Validating config file...')

    config_optional_map = {
        'global': {
            'debug': 0,
            'offline': 0
        }
    }
    config_mandatory_map = {
        # 'jellyfin': ['url', 'api_key', 'adult_path'],
        'jellyfin': ['url', 'api_key', 'movie_dir_name', 'tv_dir_name', 'short_dir_name', 'adult_dir_name'],
        'notion': ['api_key', 'database_id']
    }

    for section, options in config_optional_map.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, default_value in options.items():
            if not config.has_option(section, key):
                config.set(section, key, str(default_value))

    for section, keys in config_mandatory_map.items():
        if not config.has_section(section):
            print(progress, f'Failed to find section: {section}')
            sys.exit(1)
        for key in keys:
            if not config.has_option(section, key) or not config.get(section, key).strip():
                print(progress, f'Failed to find option: {section}.{key}')
                sys.exit(1)

    progress = build_progress(1, 1)
    print(progress)

    return config

def fetch_notion_database(database_id):
    index = 0
    progress = build_progress(index, index + 1)

    database = []

    if debug == 0 and (offline == 1 or offline == 3):
        print(progress, 'Fetching local Notion database...')
        try:
            with open('notion_database.json', 'r') as file:
                database = json.load(file)
        except FileNotFoundError:
            print(progress, 'Failed to fetch local Notion database.')
            sys.exit(1)

        progress = build_progress(1, 1)
        print(progress)

        return database

    print(progress, 'Fetching Notion database...')
    url = 'https://api.notion.com/v1/databases/' + database_id + '/query'
    has_more = True
    start_cursor = None

    while has_more:
        index = index + 1
        progress = build_progress(index, index + 1)
        payload = {}
        if start_cursor:
            payload['start_cursor'] = start_cursor

        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            database.extend(data['results'])
            has_more = data.get('has_more', False)
            start_cursor = data.get('next_cursor', None)
            print(progress)
        else:
            print(progress, f'Failed to fetch Notion database. {response.json()}')
            sys.exit(1)

    with open('notion_database.json', 'w') as file:
        json.dump(database, file, indent=4)

    index = index + 1
    progress = build_progress(index, index)
    print(progress)

    return database

def fetch_jellyfin_library():
    progress = build_progress(0, 1)

    library_dict = {}

    if debug == 0 and (offline == 2 or offline == 3):
        print(progress, 'Fetching local Jellyfin library...')

        try:
            with open('jellyfin_library_dict.json', 'r') as file:
                library_dict = json.load(file)
        except FileNotFoundError:
            print(progress, 'Failed to fetch local Jellyfin library.')
            sys.exit(1)

        progress = build_progress(1, 1)
        print(progress)

        return library_dict

    print(progress, 'Fetching Jellyfin library...')
    url = config['jellyfin']['url'] + '/Items'
    params = {
        'recursive': 'true',
        # 'includeItemTypes': 'Season',
        'includeItemTypes': 'Movie, Series, Season, Episode',
        'fields': 'Genres, ParentId, Path, ProviderIds, Tags',
        # 'fields': 'AirTime, CanDelete, CanDownload, ChannelInfo, Chapters, Trickplay, ChildCount, CumulativeRunTimeTicks, CustomRating, DateCreated, DateLastMediaAdded, DisplayPreferencesId, Etag, ExternalUrls, Genres, HomePageUrl, ItemCounts, MediaSourceCount, MediaSources, OriginalTitle, Overview, ParentId, Path, People, PlayAccess, ProductionLocations, ProviderIds, PrimaryImageAspectRatio, RecursiveItemCount, Settings, ScreenshotImageTags, SeriesPrimaryImage, SeriesStudio, SortName, SpecialEpisodeNumbers, Studios, Taglines, Tags, RemoteTrailers, MediaStreams, SeasonUserData, ServiceName, ThemeSongIds, ThemeVideoIds, ExternalEtag, PresentationUniqueKey, InheritedParentalRatingValue, ExternalSeriesId, SeriesPresentationUniqueKey, DateLastRefreshed, DateLastSaved, RefreshState, ChannelImage, EnableMediaSourceDisplay, Width, Height, ExtraIds, LocalTrailerCount, IsHD, SpecialFeatureCount',
        'sortBy': 'Name'
    }
    response = requests.get(url, headers=jellyfin_headers, params=params)
    if response.status_code == 200:
        progress = build_progress(1, 1)
        print(progress)
        library = response.json()
    else:
        print(progress, f'Failed to fetch Jellyfin library. {response.json()}')
        sys.exit(1)

    progress = build_progress(0, 1)
    print(progress, 'Creating Jellyfin library dictionary...')

    library_dict = {}
    library_id_dict = {}
    library_id_dict = {}
    for item in library['Items']:
        if item['Type'] == 'Movie' or item['Type'] == 'Series':
            tmdb_id = item['ProviderIds']['Tmdb']
            library_dict[tmdb_id] = {
                'Name': item['Name'],
                'Type': item['Type'],
                # 'ParentId': item['ParentId'],
                'Path': item['Path'],
                'Genres': item['Genres'],
                'Tags': item['Tags']
            }
            if item['Type'] == 'Series':
                jellyfin_id = item['Id']
                library_id_dict[jellyfin_id] = {
                    'Name': item['Name'],
                    'Tmdb': tmdb_id
                }
    for item in library['Items']:
        if item['Type'] == 'Season':
            jellyfin_series_id = item['SeriesId']
            tmdb_id = library_id_dict[jellyfin_series_id]['Tmdb']
            library_dict[tmdb_id]['Seasons'] = library_dict[tmdb_id].get('Seasons', {})
            library_dict[tmdb_id]['Seasons'][item['Name']] = {}
            library_id_dict[item['Id']] = {
                'Name': item['Name'],
                'Tmdb': tmdb_id
            }
    for item in library['Items']:
        if item['Type'] == 'Episode':
            jellyfin_season_id = item['SeasonId']
            tmdb_id = library_id_dict[jellyfin_season_id]['Tmdb']
            season_name = library_id_dict[jellyfin_season_id]['Name']
            library_dict[tmdb_id]['Seasons'][season_name]['Episodes'] = library_dict[tmdb_id]['Seasons'][season_name].get('Episodes', [])
            library_dict[tmdb_id]['Seasons'][season_name]['Episodes'].append(item['Name'])
    for tmdb_id, item in library_dict.items():
        if item['Type'] == 'Series':
            for season_name, season_item in item['Seasons'].items():
                season_item['EpisodeCount'] = len(season_item['Episodes'])

    with open('jellyfin_library.json', 'w') as file:
        json.dump(library, file, indent=4)
    with open('jellyfin_library_dict.json', 'w') as file:
        json.dump(library_dict, file, indent=4)
    with open('jellyfin_id_dict.json', 'w') as file:
        json.dump(library_id_dict, file, indent=4)

    progress = build_progress(1, 1)
    print(progress)

    return library_dict

def sync(notion_database, jellyfin_library):
    total = len(notion_database)
    updated_s = 0
    updated_f = 0
    updated_f_list = []
    skipped_s = 0
    skipped_n = 0
    skipped_n_list = []
    for index, notion_item in enumerate(notion_database):
        progress = build_progress(index + 1, total)

        name_parts = [part['plain_text'] for part in notion_item['properties']['名称']['title']]
        name = ''.join(name_parts)
        tmdb_id = str(notion_item['properties']['TMDB ID']['number'])

        jellyfin_item = jellyfin_library.get(tmdb_id)
        if jellyfin_item:
            if config['jellyfin']['adult_dir_name'] in jellyfin_item['Path']:
                adult = True
            else:
                adult = False

            if config['jellyfin']['movie_dir_name'] in jellyfin_item['Path']:
                kind = config['jellyfin']['movie_dir_name']
            elif config['jellyfin']['tv_dir_name'] in jellyfin_item['Path']:
                kind = config['jellyfin']['tv_dir_name']
            elif config['jellyfin']['short_dir_name'] in jellyfin_item['Path']:
                kind = config['jellyfin']['short_dir_name']
            elif config['jellyfin']['adult_dir_name'] in jellyfin_item['Path']:
                kind = config['jellyfin']['adult_dir_name']

            genres = jellyfin_item['Genres']
            tags = []
            for tag in jellyfin_item['Tags']:
                tag = re.sub(r'^\s+|,|\s+$', '', tag)
                if tag not in tags:
                    tags.append(tag)

            if jellyfin_item['Type'] == 'Series':
                season_name = notion_item['properties']['名称']['title'][2]['text']['content']
                episode_count = jellyfin_item['Seasons'][season_name]['EpisodeCount']
                current_episode = notion_item['properties']['当前']['number']
                if current_episode == None:
                    current_episode = 0
            else:
                episode_count = None
                current_episode = None

            properties = build_notion_properties(kind, genres, tags, adult, episode_count, current_episode)

            if is_properties_different(notion_item['properties'], properties):
                is_updated = update_notion_item(notion_item['id'], properties, progress, name)
                if is_updated:
                    updated_s += 1
                else:
                    updated_f += 1
                    updated_f_list.append(name)
            else:
                print(progress, f'Skipped item (s): {name}')
                skipped_s += 1
        else:
            print(progress, f'Skipped item (n): {name}')
            skipped_n += 1
            skipped_n_list.append(name)

    print(f'Updated items: {updated_s}')
    print(f'Failed items: {updated_f}')
    if updated_f:
        print(f'Failed items list: {updated_f_list}')
    print(f'Skipped items (s): {skipped_s}')
    print(f'Skipped items (n): {skipped_n}')
    if skipped_n:
        print(f'Skipped items (n) list: {skipped_n_list}')

def build_notion_properties(kind, genres, tags, adult, episode_count, current_episode):
    properties = {
        '种类': {
            'select': {
                'name': kind
            }
        },
        '成人': {
            'checkbox': adult
        },
        '类型': {
            'multi_select': [
                {
                    'name': genre
                } for genre in genres
            ]
        },
        '标签': {
            'multi_select': [
                {
                    'name': tag
                } for tag in tags
            ]
        }
    }
    if episode_count != None:
        properties['集数'] = {
            'number': episode_count
        }
    if current_episode != None:
        properties['当前'] = {
            'number': current_episode
        }
    return properties

def is_properties_different(notion_properties, properties):
    for key, value in properties.items():
        if key not in notion_properties:
            return True
        notion_value = notion_properties[key]
        if key == '种类':
            if notion_value['select']['name'] != value['select']['name']:
                return True
        elif key == '成人':
            if notion_value['checkbox'] != value['checkbox']:
                return True
        elif key == '类型' or key == '标签':
            notion_names = [item['name'] for item in notion_value['multi_select']]
            names = [item['name'] for item in value['multi_select']]
            if notion_names != names:
                return True
        elif key == '集数' or key == '当前':
            if notion_value['number'] != value['number']:
                return True
    return False

def build_progress(index, total):
    progress_bar_len = 50

    progress_bar = '|' + '-' * int(index / total * progress_bar_len) + ' ' * (progress_bar_len - int(index / total * progress_bar_len)) + '|'
    progress_percent = '0' * (len(str(total)) - len(str(index))) + str(index) + '/' + str(total)

    progress = progress_bar + ' ' + progress_percent
    return progress

def update_notion_item(page_id, properties, progress, name):
    url = 'https://api.notion.com/v1/pages/' + page_id
    data = {
        'properties': {
            **properties
        }
    }
    response = requests.patch(url, headers=notion_headers, data=json.dumps(data))
    if response.status_code == 200:
        print(progress, f'Updated item: {name}')
        return True
    else:
        print(progress, f'Failed to update item: {name} {response.json()}')
        return False

def main():
    print('Jellytion\nThe MIT License (MIT)\nCopyright (c) 2025 Jonathan Chiu')

    global config, debug, offline, jellyfin_headers, notion_headers

    config = fetch_config()
    print(json.dumps({section: dict(config[section]) for section in config.sections()}, ensure_ascii=False))

    debug = int(config['global']['debug'])
    offline = int(config['global']['offline'])

    jellyfin_headers = {
        'X-Emby-Token': config['jellyfin']['api_key'],
        'Content-Type': 'application/json'
    }
    notion_headers = {
        'Authorization': 'Bearer ' + config['notion']['api_key'],
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    if debug == 0:
        notion_database = fetch_notion_database(config['notion']['database_id'])
        jellyfin_library = fetch_jellyfin_library()
        sync(notion_database, jellyfin_library)
        with open('last_complete_run_time.txt', 'w') as file:
            file.write(datetime.now().strftime('%Y-%m-%d at %H:%M:%S'))
    if debug == 1 or debug == 3:
        fetch_notion_database(config['notion']['database_id'])
    if debug == 2 or debug == 3:
        fetch_jellyfin_library()

    print('Run complete!')

if __name__ == '__main__':
    main()
