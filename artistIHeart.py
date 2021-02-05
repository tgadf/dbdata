from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
import json
from dbUtils import utilsIHeart
from hashlib import md5


class artistIHeart(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsIHeart()
        self.debug  = False
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL(meta)
        ID          = self.getID(url.url)
        pages       = self.getPages()
        profile     = self.getProfile()        
        media       = self.getMedia(artist)
        mediaCounts = self.getMediaCounts(media)
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

    ##############################################################################################################################
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        script = self.bsdata.find("script", {"data-name": "initial-state"})
        if script is None:
            anc = artistDBNameClass(name=None, err = "NoJSON")
            return anc
        
        try:
            jdata = json.loads(script.contents[0])
        except:
            anc = artistDBNameClass(name=None, err = "BadJSON")
            return anc
        

        artistName = None
        for artistID, artistData in jdata['artists']['artists'].items():
            artistName = artistData["artistName"]
            break

        if artistName is not None:
            anc = artistDBNameClass(name=artistName, err=None)
            return anc

        anc = artistDBNameClass(name=None, err = "NoArtistName")
        return anc

    
    

    ##############################################################################################################################
    ## Meta Information
    ##############################################################################################################################
    def getMeta(self):
        metatitle = self.bsdata.find("meta", {"property": "og:title"})
        metaurl   = self.bsdata.find("meta", {"property": "og:url"})

        title = None
        if metatitle is not None:
            title = metatitle.attrs['content']

        url = None
        if metatitle is not None:
            url = metaurl.attrs['content']

        amc = artistDBMetaClass(title=title, url=url)
        return amc
        

    ##############################################################################################################################
    ## Artist URL
    ##############################################################################################################################
    def getURL(self, meta):
        url = meta.url
        auc = artistDBURLClass(url=url)
        return auc
    
    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, url):
        artistID = self.dutils.getArtistID(url, debug=False)
        if artistID is not None:
            aic = artistDBIDClass(ID=artistID)
        else:
            aic = artistDBIDClass(ID=None, err="NoID")
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        apc   = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):              
        data = {}
        
        artistdiv  = self.bsdata.find("div", {"id": "tlmdata"})
        if artistdiv is not None:
            artistdata = artistdiv.attrs['data-tealium-data']
        else:
            artistdata = None
    
        if artistdata is not None:
            try:
                artistvals = json.loads(artistdata)
                genres     = artistvals["tag"]
            except:
                genres     = None

            if genres is not None:
                genres = genres.split(",")
            else:
                genres = None
        else:
            genres = None
        
       
        data["Profile"] = {'genre': genres, 'style': None}
               
        apc = artistDBProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc

    
    
    ##############################################################################################################################
    ## Artist Media
    ############################################################################################################################## 
    def getArtistMediaData(self, jdata):
        media = {"Albums": [], "Singles": []}
        for artistID, artistData in jdata['artists']['artists'].items():
            artistName = artistData["artistName"]
            artistBio  = artistData["artistBio"]
            albums     = artistData["albums"]
            tracks     = artistData["tracks"]

            mediaType = "Albums"
            for albumData in albums:
                albumID   = albumData['albumId']
                albumName = albumData['title']
                albumEpoch = albumData['releaseDate']
                amdc = artistDBMediaDataClass(album=albumName, url=None, aclass=None, aformat=None, artist=[artistName], code=albumID, year=albumEpoch)
                media[mediaType].append(amdc)

            mediaType = "Singles"
            for trackData in tracks:
                trackID   = trackData['trackId']
                trackName = trackData['title']
                amdc = artistDBMediaDataClass(album=trackName, url=None, aclass=None, aformat=None, artist=[artistName], code=trackID, year=None)
                media[mediaType].append(amdc)
        return media
        
    def getTrackMediaData(self, jdata):
        albums = []
        for artistID,artistData in jdata['albums'].items():
            if artistID == "albums":
                continue
            albumsData = artistData["albums"]
            for albumData in albumsData:
                albumID     = albumData["albumId"]
                artistName  = albumData["artistName"]
                albumName   = albumData["title"]
                albumTracks = albumData["tracks"]

                tracks = []
                for track in albumTracks:
                    trackID    = track['id']
                    trackTitle = track['title']
                    trackPos   = track['albumInfo'].get('trackNumber')
                    try:
                        int(trackPos)
                    except:
                        trackPos = -1

                    tracks.append({"ID": trackID, "Title": trackTitle, "Pos": trackPos})
        return None
                
        
        
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        script = self.bsdata.find("script", {"data-name": "initial-state"})
        if script is None:
            print("No media data")
            return amc
        
        try:
            jdata = json.loads(script.contents[0])
        except:
            print("Could not load JSON data")
            return amc

        mediaData = self.getArtistMediaData(jdata)
        for mediaType,mediaTypeData in mediaData.items():
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            for amdc in mediaTypeData:
                amc.media[mediaType].append(amdc)

        return amc
    
    

    ##############################################################################################################################
    ## Artist Media Counts
    ##############################################################################################################################
    def getMediaCounts(self, media):
        amcc = artistDBMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
        
        
        amcc.err = "No Counts"
        return amcc
        
        results = self.bsdata.findAll("ul", {"class": "facets_nav"})
        if results is None or len(results) == 0:
            amcc.err = "No Counts"
            return amcc
            
        for result in results:
            for li in result.findAll("li"):
                ref = li.find("a")
                if ref:
                    attrs = ref.attrs
                    span = ref.find("span", {"class": "facet_count"})
                    count = None
                    if span:
                        count = span.text
                        credittype    = attrs.get("data-credit-type")
                        creditsubtype = attrs.get("data-credit-subtype")
                        if credittype and creditsubtype:
                            if amcc.counts.get(credittype) == None:
                                amcc.counts[credittype] = {}
                            if amcc.counts[credittype].get(creditsubtype) == None:
                                try:
                                    amcc.counts[credittype][creditsubtype] = int(count)
                                except:
                                    amcc.counts[credittype][creditsubtype] = count
                                    amcc.err = "Non Int"

        return amcc