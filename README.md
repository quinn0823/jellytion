# Jellytion

Jellyfin → Notion

---

## Note

It is currently highly personal. I'm trying to make the code more configurable, moving some config items to the external file `config.ini`. The private content, such as API keys, has been moved. Next, the property names of Notion will also be moved.

## Requirements

- [Python 3.6+](https://www.python.org/downloads/)
- Python package: `requests`

## Usage

> [!WARNING]
> For privacy reasons, please do not make modifications directly on `config_default.ini`. Please create a copy of it, and rename it `config.ini`.

1. Clone the repository or download the source.
    ```
    git clone https://github.com/quinn0823/jellytion.git
    ```
1. Complete the config file `config.ini` (or `config_default.ini`, not recommended).
1. Install the dependencies.
    ```
    pip install -r requirements.txt
    ```
1. Change directory to the source folder and run the script.
    ```
    cd jellytion
    python main.py
    ```

---

Updated Date: November 24, 2025

Published Date: November 24, 2025

The MIT License (MIT)

Copyright © 2025 Jonathan Chiu
