from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Album, Artist
import musicbrainzngs
import json

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
    return render(request, 'Quiz/search.html', {'artists': artists, 'searchString': query})

def artist(request):
    query = request.GET.get('artist_query')
    if len(query) < 1:
        query='a74b1b7f-71a5-4011-9441-d0b5e4122711'
    results = musicbrainzngs.get_artist_by_id(query, includes=["release-groups"], release_type=["album", "ep"])
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
    try:
        image_list = musicbrainzngs.get_release_group_image_list(results["artist"]["release-group-list"][0]['id'])
        image_url = image_list['images'][0]['thumbnails']['large']
    except:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
    return render(request, 'Quiz/artist.html', {'albums': albums, 'artist':artist, 'image':image_url})



def quiz(request):
    query = request.GET.get('album_id')
    release_group = musicbrainzngs.get_release_group_by_id(query, includes=['releases'])
    release_index = 0
    for release in release_group['release-group']['release-list']: #avoid deluxe editions with additional tracks. 
        if "deluxe" in release['title'].lower() or "special edition" in release['title'].lower():
            release_index += 1
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
                break
            
    if release_index >= len(release_group['release-group']['release-list']):
        release_index = 0
    
    release = musicbrainzngs.get_release_by_id(release_group['release-group']['release-list'][release_index]['id'], includes=['recordings', 'artists'])
    title = release_group['release-group']['release-list'][release_index]['title']
    try:
        artist = release['release']['artist-credit'][0]['artist']['name']
    except:
        artist = "Unknown"
    try:
        image_list = musicbrainzngs.get_release_group_image_list(query)
        image_url = image_list['images'][0]['thumbnails']['large']
    except:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Album_cover_with_notes_03.svg/240px-Album_cover_with_notes_03.svg.png"
    tracks = []
    discs = len(release['release']['medium-list'])
    discInfoString = str(discs)
    for i in range(0, discs):
        discInfoString += "X" + str(len(release['release']['medium-list'][i]['track-list']))
        for track in release['release']['medium-list'][i]['track-list']:
            tracks.append(track['recording']['title'])

    json_tracks = json.dumps(tracks)
    return render(request, 'Quiz/quiz.html', {'tracks': json_tracks, 'cover': image_url, 'title': title, 'artist': artist, 'discs': discInfoString, 'album_id':query})


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

    
    return render(request, 'Quiz/albums.html', {'albums': albums, 'searchString': query})

def getAlbumArt(request):
    if request.is_ajax and request.method == "GET":
        query = request.GET.get('album_id')
        print(query)
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