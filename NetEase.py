import json
import re
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.72"}


def Search(word, Type, limit=5):
    # 设置搜索类型
    Type = Type.lower()
    TypeDict = {"playlists": 1000, "artists": 100, "mvs": 1004}

    # 设置参数，对API发送请求
    url = "http://music.163.com/api/search/pc"
    dt = {"s": word, "offset": "0", "limit": limit, "type": TypeDict[Type]}
    response = requests.post(url, data=dt, headers=headers)

    # 对结果进行解析，返回所有搜索到的歌单(歌手)的id和名称
    try:
        results = json.loads(response.text)["result"][Type]
    except KeyError:
        print("未找到相关内容！")
        return None
    return [(results[i]["id"], results[i]["name"]) for i in range(len(results))]


def GetSongID(ID, Type):
    # Type为playlist或artist
    url = f"https://music.163.com/{Type.lower()}?id={ID}"

    # 设置请求头，查看url源代码
    doc = requests.get(url, headers=headers).text

    # 正则表达式匹配每个SongId
    SongIdPattern = re.compile(r'<a href="/song\?id=(\d{1,20})">')
    songs = re.findall(SongIdPattern, doc)

    return songs


def GetArtistInfo(ArtistID):
    url = f"http://music.163.com/api/artist/albums/{ArtistID}?id={ArtistID}&offset=0&total=true&limit=1"
    doc = requests.get(url, headers=headers).text

    data = json.loads(doc)
    try:
        ArtistName = data["artist"]["name"]
        MusicCount = data["artist"]["musicSize"]
        AlbumCount = data["artist"]["albumSize"]
    except KeyError:
        return [0, '', 0, 0, 0]

    url = f"https://music.163.com/artist?id={ArtistID}"
    doc = requests.get(url, headers=headers).text
    UserIDPtn = re.compile(r'<a id="artist-home" href="/user/home\?id=(\d+?)" class="btn-rz f-tid">Ta的个人主页</a>')
    try:
        UserID = int(re.findall(UserIDPtn, doc)[0])
    except IndexError:
        UserID = 0

    return [ArtistID, ArtistName, MusicCount, AlbumCount, UserID]


def GetSongInfo(SongID):
    url = f"http://music.163.com/api/song/detail/?id={SongID}&ids=[{SongID}]"
    doc = requests.get(url, headers=headers).text
    data = json.loads(doc)

    try:
        SongName = data["songs"][0]["name"]
        AlbumPosition = data["songs"][0]["position"]
        AlbumID = int(data["songs"][0]["album"]["id"])
        MVID = int(data["songs"][0]["mvid"])
        ArtistIDs = [data["songs"][0]["artists"][i]["id"] for i in range(len(data["songs"][0]["artists"]))]
    except KeyError:
        return [SongID, "", 0, 0, 0, [0]]
    return [SongID, SongName, AlbumPosition, AlbumID, MVID, ArtistIDs]


def GetAlbumInfo(AlbumID):
    url = f"https://music.163.com/album?id={AlbumID}"
    doc = requests.get(url, headers=headers).text

    AlbumNamePtn = re.compile(r'<meta property="og:title" content="(.*?)" />')
    AlbumSizePtn = re.compile(r'<h3><span class="f-ff2">包含歌曲列表</span></h3><span class="sub s-fc3">(\d+?)首歌</span>')
    ArtistIDPtn = re.compile(r'<meta property="music:musician" content="https://music.163.com/artist\?id=(\d+?)"/>')
    AlbumPublishDatePtn = re.compile(r'<meta property="music:release_date" content="(\d{4}-\d{2}-\d{2})"/>')
    SongIDPtn = re.compile(r'<meta property="music:song" content="https://music.163.com/song\?id=(\d+?)"/>')

    try:
        AlbumName = re.findall(AlbumNamePtn, doc)[0]
        AlbumSize = int(re.findall(AlbumSizePtn, doc)[0])
        ArtistID = int(re.findall(ArtistIDPtn, doc)[0])
        AlbumPublishDate = re.findall(AlbumPublishDatePtn, doc)[0]
        SongIDs = list(map(int, re.findall(SongIDPtn, doc)))
    except IndexError:
        return [0, '', 0, '', 0, 0]

    return [AlbumID, AlbumName, AlbumSize, AlbumPublishDate, ArtistID, SongIDs]


def GetPlaylistInfo(PlaylistID):
    url = f"https://music.163.com/playlist?id={PlaylistID}"
    doc = requests.get(url, headers=headers).text

    PlaylistNamePtn = re.compile(r'"title": "(.*?)",')
    PlaylistLikesPtn = re.compile(r'data-count="(\d+?)"\ndata-res-action="fav"')
    PlaylistCommentsPtn = re.compile(r'<span id="cnt_comment_count">(\d+?)</span>')
    CreateDatePtn = re.compile(r'"pubDate": "(\d{4}-\d{2}-\d{2})T')
    TagPtn = re.compile(
        r'<a class="u-tag" href="/discover/playlist/\?cat=.*"><i>(.*?)</i></a>')
    UserIDPtn = re.compile(r'<a href="/user/home\?id=(\d+?)" class="s-fc7">')
    SongIDPtn = re.compile(r'<a href="/song\?id=(\d+?)">')

    PlaylistName = re.findall(PlaylistNamePtn, doc)[0]
    try:
        PlaylistLikes = int(re.findall(PlaylistLikesPtn, doc)[0])
    except IndexError:
        PlaylistLikes = 0
    try:
        PlaylistComments = int(re.findall(PlaylistCommentsPtn, doc)[0])
    except IndexError:
        PlaylistComments = 0
    CreateDate = re.findall(CreateDatePtn, doc)[0]
    Tag = "|".join(re.findall(TagPtn, doc))
    UserID = int(re.findall(UserIDPtn, doc)[0])
    SongIDs = list(map(int, re.findall(SongIDPtn, doc)))

    return [PlaylistID, PlaylistName, PlaylistLikes, PlaylistComments, CreateDate, Tag, UserID, SongIDs]


def GetUserInfo(UserID):
    url = f"https://music.163.com/user/home?id={UserID}"
    doc = requests.get(url, headers=headers).text

    UserNamePtn = re.compile(r'"title": "(.*?)",')
    LocationPtn = re.compile(r'<span>所在地区：(.*) </span>')
    FansPtn = re.compile(r'<strong id="fan_count">(\d+?)</strong>')
    FollowsPtn = re.compile(r'<strong id="follow_count">(\d+?)</strong>')
    ArtistIDPtn = re.compile(
        r'<div class="edit"><a href="/artist\?id=(\d+?)" hidefocus="true" class="u-btn2 u-btn2-1">')

    try:
        UserName = re.findall(UserNamePtn, doc)[0]
    except IndexError:
        return [UserID, '', '', 0, 0, 0]
    try:
        Location = re.findall(LocationPtn, doc)[0]
    except IndexError:
        Location = ''
    Fans = int(re.findall(FansPtn, doc)[0])
    Follows = int(re.findall(FollowsPtn, doc)[0])
    try:
        ArtistID = int(re.findall(ArtistIDPtn, doc)[0])
    except IndexError:
        ArtistID = 0

    return [UserID, UserName, Location, Fans, Follows, ArtistID]


def GetMVInfo(MVID):
    url = f"http://music.163.com/api/mv/detail?id={MVID}&type=mp4"
    doc = requests.get(url, headers=headers).text
    data = json.loads(doc)
    try:
        MVName = data["data"]["name"]
        MVLikes = data["data"]["likeCount"]
        MVComments = data["data"]["commentCount"]
        MVPublishDate = data["data"]["publishTime"]
        ArtistIDs = [data["data"]["artists"][i]["id"] for i in range(len(data["data"]["artists"]))]
    except KeyError:
        return [0, '', 0, 0, 0, 0]
    return [MVID, MVName, MVLikes, MVComments, MVPublishDate, ArtistIDs]
