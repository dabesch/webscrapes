from bs4 import BeautifulSoup
import requests
import json


# Create the artist string to search
def artistToSearch(artist):
    """
    :param artist: The artist you wish to return all albums for
    :return: returns a cleaned url string for that artist
    """
    azlyrics = 'https://www.azlyrics.com/'
    i = artist.lower()[0]
    artist = artist.replace(' ', '').lower()
    return f'{azlyrics}{i}/{artist}.html'


# Get Albums
def artistPage(artist):
    """
    :param artist: The artist you wish to return all albums for
    :return: a bs4 object which needs further processing, but only album title and tracks
    """
    url = artistToSearch(artist)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    albums = soup.find('div', id='listAlbum').find_all(['div', 'a'])
    return albums


def extractSong(url):
    """
    :param url: the url of a song which to scrape
    :return: returns a text string of the song selected
    """
    response = requests.get(url)
    songsoup = BeautifulSoup(response.text, 'lxml')
    # credit to kokosxD for a simplier way of scraping the song page
    lyrics = songsoup.find("div", {"class": "col-xs-12 col-lg-8 text-center"}).find_all("div")[6].get_text()
    lines = lyrics.splitlines()[2:]
    return "\n".join(lines)


def albumDict(albums):
    """
    :param albums:
    :return: a dictionary object with all details of the album with the lyrics of each song
    """
    testDict = dict()
    for a in albums:
        if a.name == 'div':
            if len(a.contents) > 1:
                albumName = a.b.contents[0].replace('"', '')  # remove extra quotations
                year = a.contents[-1]
                year = int(''.join([i for i in year if i.isdigit()]))  # this can be improved
            else:
                albumName = a.contents[0]
                year = 'unknown'
        else:
            href = a.get('href')
            testDict[a.contents[0]] = href.replace('..', 'https://www.azlyrics.com')
    finalDict = dict(album=albumName, year=year, tracks=testDict)

    # Process each href and replace with lyrics
    for key in finalDict['tracks'].keys():
        href = finalDict['tracks'][key]
        finalDict['tracks'][key] = extractSong(href)

    return finalDict


# write to JSON for reading later
def albumToJSON(dictionary, filename, append=True):
    if append:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            data.append(dictionary)
    else:
        data = dictionary
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    print('JSON write complete')


# create dict
def splitAlbums(albums, filename):
    """

    :param albums: the album object which needs splitting into seperate albums for processing
    :param filename: the name of the final json file, this file is appended to as the script runs, to allow for failure
    :return: creates a json file
    """
    ind = [albums.index(i) for i in list(albums) if i.name == 'div']
    for i in ind:
        if i != ind[-1]:
            i2 = ind.index(i)
            albumToJSON(albumDict(albums[i: ind[i2 + 1]]), filename)
        else:
            albumToJSON(albumDict(albums[i:]), filename)


# Example of use
def artistScrape(artist, jsonFile):
    """
    Runs the whole script with the artist name and the final filename
    """
    albums = artistToSearch(artist)
    splitAlbums(albums, jsonFile)
