from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Album, Artist
import musicbrainzngs
import json
import requests

musicbrainzngs.set_useragent("TestSearch", "0.1", "test.com")

# Create your views here.

def home(request):
    return render(request, 'Quiz/home.html')

def search(request):
    query = request.GET.get('query')
    if len(query) < 1:
        query='pink floyd'
    results = musicbrainzngs.search_artists(query)
    artists = []
    for artist_result in results['artist-list']:
        new_artist = Artist()
        new_artist.name = artist_result['name']
        new_artist.artist_id = artist_result['id']
        try:
            new_artist.type = artist_result['type']
        except:
            new_artist.type = "Unknown"
        try:
            new_artist.area = ", " + artist_result['country']
        except:
            new_artist.area = ""
        new_artist.image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
        artists.append(new_artist)
    if len(artists) == 0:
        isEmpty = True
    else:
        isEmpty = False
    return render(request, 'Quiz/search.html', {'artists': artists, 'searchString': query, 'empty':isEmpty})

def artist(request):
    query = request.GET.get('artist_query')
    if len(query) < 1:
        query='69ee3720-a7cb-4402-b48d-a02c366f2bcf'
    if "/artist/" in query:
        query = query[query.find("/artist/")+8:]
    try:
        results = musicbrainzngs.get_artist_by_id(query, includes=["release-groups"], release_type=["album", "ep"])
        error = False
    except:
        results = musicbrainzngs.get_artist_by_id('69ee3720-a7cb-4402-b48d-a02c366f2bcf', includes=["release-groups"], release_type=["album", "ep"])
        error = True
    artist = results["artist"]["name"]
    albums = []
    for release_group in results["artist"]["release-group-list"]:
        new_album = Album()
        new_album.title = release_group["title"]
        new_album.type = release_group["type"]
        new_album.album_id = release_group["id"]
        new_album.date = ", " + release_group["first-release-date"][:4]
        new_album.image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
        albums.append(new_album)

    # albums.sort(key=lambda albums: albums.date, reverse=True)
    if len(albums) == 0:
        isEmpty = True
    else:
        isEmpty = False
    try:
        image_list = musicbrainzngs.get_release_group_image_list(results["artist"]["release-group-list"][0]['id'])
        image_url = image_list['images'][0]['thumbnails']['large']
    except:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
    return render(request, 'Quiz/artist.html', {'albums': albums, 'artist':artist, 'image':image_url, 'empty':isEmpty, 'error':error})



def quiz(request):
    query = request.GET.get('album_id')
    isGroup = False
    release_group_id = ""
    try:
        if "/release/" in query:
            release_id = query[query.find("/release/")+9:]
            release = musicbrainzngs.get_release_by_id(release_id, includes=['recordings', 'artists'])
        else:
            if "/release-group/" in query:
                release_group_id = query[query.find("/release-group/")+15:]
                release_group = musicbrainzngs.get_release_group_by_id(release_group_id, includes=['releases'])
                release = get_release_from_release_group(release_group)
                isGroup = True
            else:
                try:
                    release_group = musicbrainzngs.get_release_group_by_id(query, includes=['releases'])
                    release_group_id = query
                    release = get_release_from_release_group(release_group)
                    isGroup = True
                except:
                    release = musicbrainzngs.get_release_by_id(query, includes=['recordings', 'artists'])
        error = False
    except:
        release = musicbrainzngs.get_release_by_id("a1170afd-e95f-3975-ad26-e04c70d6a42b", includes=['recordings', 'artists'])
        error = True
    try:
        if isGroup and is_url_image("https://coverartarchive.org/release-group/"+release_group_id+"/front.jpg"):
            image_url = "https://coverartarchive.org/release-group/"+release_group_id+"/front.jpg"
        else:
            image_list = musicbrainzngs.get_image_list(release['release']['id'])
            image_url = image_list['images'][0]['thumbnails']['large']
    except:
        if isGroup and is_url_image("https://coverartarchive.org/release-group/"+release_group_id+"/front.jpg"):
            image_url = "https://coverartarchive.org/release-group/"+release_group_id+"/front.jpg"
        else:
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
    title = release['release']['title']
    try:
        artist = release['release']['artist-credit'][0]['artist']['name']
    except:
        artist = "Unknown"
    tracks = []
    discs = len(release['release']['medium-list'])
    discInfoString = str(discs)
    for i in range(0, discs):
        discInfoString += "X" + str(len(release['release']['medium-list'][i]['track-list']))
        for track in release['release']['medium-list'][i]['track-list']:
            tracks.append(track['recording']['title'])

    json_tracks = json.dumps(tracks)
    return render(request, 'Quiz/quiz.html', {'tracks': json_tracks, 'cover': image_url, 'title': title, 'artist': artist, 'discs': discInfoString, 'album_id':query, 'error':error})

def get_release_from_release_group(release_group):
    release_index = 0
    acceptable_index = -1
    for release in release_group['release-group']['release-list']: #avoid deluxe editions with additional tracks. 
        if "deluxe" in release['title'].lower() or "special edition" in release['title'].lower():
            release_index += 1
        elif release['quality'].lower() == 'high':
            break
        else:
            try:
                disambiguation = release['disambiguation'].lower()
            except:
                disambiguation = 'this seems perfectly acceptable'
            if disambiguation.find('deluxe') > -1: 
                    release_index +=1
            elif disambiguation.find('special') > -1:
                    release_index +=1
            else:
                if(acceptable_index<0):
                    acceptable_index = release_index
                release_index +=1
            
    if release_index >= len(release_group['release-group']['release-list']):
        release_index = acceptable_index
    release = musicbrainzngs.get_release_by_id(release_group['release-group']['release-list'][release_index]['id'], includes=['recordings', 'artists'])
    return release

def album_search(request):
    query = request.GET.get('query')
    results = musicbrainzngs.search_release_groups(query, type = "album", status = "official")
    albums = []
    for release in results["release-group-list"]:
        new_album = Album()
        new_album.title = release["title"]
        new_album.album_id = release["id"]
        try:
            new_album.artist = release["artist-credit"][0]["name"]
        except:
            new_album.artist = "Unknown Artist"
        try:
            new_album.date = ", " + release["disambiguation"]
        except:
            new_album.date = ""
        try:
            new_album.type = ", " + release["type"]
        except:
            new_album.type = "Type Unknown"
        
        new_album.image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
        albums.append(new_album)

    if len(albums) == 0:
        isEmpty = True
    else:
        isEmpty = False
    return render(request, 'Quiz/albums.html', {'albums': albums, 'searchString': query, 'empty':isEmpty})

def getAlbumArt(request):
    if request.is_ajax and request.method == "GET":
        query = request.GET.get('album_id')
        try:
            image_list = musicbrainzngs.get_release_group_image_list(query)
            image_url = image_list['images'][0]['thumbnails']['large']
        except:
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
        return JsonResponse({"url":image_url}, status = 200)
    
def sendID(request):
    if request.is_ajax and request.method == "POST":
        query = request.GET.get('album_id')
        print(query)
        try:
            image_list = musicbrainzngs.get_release_group_image_list(query)
            image_url = image_list['images'][0]['thumbnails']['large']
        except:
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
        return JsonResponse({"url":image_url}, status = 200)

def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["Content-Type"] in image_formats:
      return True
    try:
        if ".jpg" in r.headers["Location"]:
            return True
    except:
        return False
    return False