from bs4 import BeautifulSoup
import urllib.request
import BandInfo
import os
from rich.console import Console
import sys

DIV_CLASS = 'charts_songname songActivityIndicator clk_loadPlaylist'


def get_divs(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.findAll("div", {"class": DIV_CLASS})


def get_song_name(html_div):
    return html_div.find('span').contents[0]


def process_divs(divs):
    songs = []
    for div in divs:
        song_id = div['data-songid']
        song_name = get_song_name(div)
        song_info = (song_id, song_name)
        songs.append(song_info)
    return songs


def get_song_ids(soup):
    divs = soup.findAll("div", {"class": DIV_CLASS})
    return process_divs(divs)


def get_html(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()
    return mystr


def download_songs(band_info):
    for song_id in band_info.song_list:
        with console.status(f'Downloading File: {song_id[1]}'):
            url = f'https://www.soundclick.com/playerV5/panels/audioStream.cfm?songID={song_id[0]}'
            try:
                fp = urllib.request.urlopen(url)
                bytes = fp.read()
            except:
                console.print(f'Unable to download {song_id[1]}')
            write_song_to_disk(bytes, song_id[1], band_name)


def write_song_to_disk(mp3, name, band_name):
    with console.status(f'Writing File: {name}'):
        if not os.path.isdir(band_name):
            os.mkdir(band_name)
        f = open(f"{band_name}/{name}.mp3", "wb")
        f.write(mp3)


def get_band_name(soup):
    id = 'sclkArtist_pageHead_name'
    return soup.find('div', {'id': id}).contents[0]


def get_confirmation():
    confirmation = ''
    while confirmation != 'y' or confirmation == 'Y':
        confirmation = console.input('Do you want to download them all? (y/n): ')
        if confirmation == 'n' or confirmation == 'N':
            sys.exit(0)


console = Console()
band_page = input("Enter Band Page: ")
html = get_html(band_page)
soup = BeautifulSoup(html, 'html.parser')
song_ids = get_song_ids(soup)

for song in song_ids:
    console.print(f'song: {song[1]} Found')
console.print(f'Found {len(song_ids)} songs')
get_confirmation()


band_name = get_band_name(soup)
band_info = BandInfo.BandInfo()

band_info.band_name = band_name
band_info.song_list = song_ids

download_songs(band_info)
