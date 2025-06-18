# Jellytion

Jellyfin → Notion

---

## Note

It is currently highly personal. I'm trying to make the code more configurable, moving some config items to the external file `config.ini`. The private content, such as API keys, has been moved. Next, the property names of Notion will also be moved.

## Requirements

- Python 3.6+
- Python package: `requests`

## Configuration

``` ini
[global]
; Optional
; 1 = Fetch and save Notion database only; 2 = Fetch and save Jellyfin library only; 3 = Fetch and save both only
debug = 0
; 1 = Use local Notion database; 2 = Use local Jellyfin library; 3 = Use both local files
offline = 0

[jellyfin]
; Mandatory
url = JELLYFIN_DOMAIN
api_key = JELLYFIN_API_KEY
adult_path = PATH_TO_JELLYFIN_ADULT_LIBRARY

[notion]
; Mandatory
api_key = NOTION_API_KEY
database_id = NOTION_DATABASE_ID
```

## Usage

> [!WARNING]
> For privacy reasons, please do not make modifications directly on `config_default.ini`. Please create a copy of it, and rename it `config.ini`.

1. Clone this repository.
2. Complete the config file: `config.ini` (or `config_default.ini`, not recommended)
3. Run the script
    - Universal
        1. Run `pip3 install -r requirements.txt`
        2. Run `python3 main.py`
    - Windows: Double-click `script/run.cmd` or `script/run3.cmd` to run the all-in-one script.

---

Updated Date: May 17, 2025

The MIT License (MIT)

Copyright © 2025 Jonathan Chiu
