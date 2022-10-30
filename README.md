# Plex Move
Move location of Plex media items by genre


## Install 
```sh 
pip install -r requirements
```

## Edit config.ini
```sh
copy config-sample.ini config.ini

# edit config.ini 
vi config.ini 
```

## Usage

```
python plexmove.py -h

usage: plexmove.py [-h] [--section SECTION] [--genre GENRE] [--todir TODIR]

Move location of Plex media items by genres

options:
  -h, --help         show this help message and exit
  --section SECTION  section of Plex library
  --genre GENRE      genre to be select
  --todir TODIR      dir to ../
```
