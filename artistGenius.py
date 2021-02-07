from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
import json
from dbUtils import utilsGenius
from hashlib import md5


class artistGenius(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsGenius()
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
        jdata = None
        for meta in self.bsdata.findAll("meta"):
            content = meta.attrs['content']
            if content.startswith("{") and content.endswith("}"):
                try:
                    jdata = json.loads(content)
                except:
                    continue
                break

        artistName = None
        if jdata is not None:
            try:
                artistName = jdata['artist']['name']
            except:
                anc = artistDBNameClass(name=None, err = "BadJSON")
                return anc
        else:
            anc = artistDBNameClass(name=None, err = "NoJSON")
            return anc
        
        anc = artistDBNameClass(name=artistName, err=None)
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
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        jdata = None
        for meta in self.bsdata.findAll("meta"):
            content = meta.attrs['content']
            if content.startswith("{") and content.endswith("}"):
                try:
                    jdata = json.loads(content)
                except:
                    continue
                break

        if jdata is not None:

            try:
                artistName = jdata['artist']['name']
            except:
                artistName = None
                
            mediaType = "Albums"
            if jdata.get('artist_albums') is not None:
                for albumData in jdata['artist_albums']:
                    albumName = albumData['name']
                    albumID   = albumData['id']
                    try:
                        albumYear = albumData['release_date_components']['year']
                    except:
                        albumYear = None

                    if amc.media.get(mediaType) is None:
                        amc.media[mediaType] = []
                    amdc = artistDBMediaDataClass(album=albumName, url=None, aclass=None, aformat=None, artist=[artistName], code=albumID, year=albumYear)
                    amc.media[mediaType].append(amdc)


            mediaType = "Singles"
            if jdata.get('artist_songs') is not None:
                for songData in jdata['artist_songs']:
                    songName = songData['title']
                    songID   = songData['id']

                    if amc.media.get(mediaType) is None:
                        amc.media[mediaType] = []
                    amdc = artistDBMediaDataClass(album=songName, url=None, aclass=None, aformat=None, artist=[artistName], code=songID, year=None)
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