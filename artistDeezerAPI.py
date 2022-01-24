from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from dbUtils import utilsDeezerAPI

class artistDeezerAPI(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsDeezerAPI()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        if self.dbdata is not None:
            return self.dbdata
        if not isinstance(self.bsdata, dict):
            raise ValueError("Could not parse Deezer API data")
            
                
        artist = self.bsdata

        artistTracks = artist["Tracks"]
        artistAlbums = artist["Albums"]
        artistName   = artist["Name"]
        artistID     = artist["ID"]
        artistURL    = artist["URL"]
        generalData  = {"Type": artist["Type"]}


        mediaData = {}
        mediaName = "Tracks"
        mediaData[mediaName] = []
        for code, artistTrack in artistTracks.items():
            album        = artistTrack["Name"]
            albumURL     = artistTrack["URL"]
            albumArtists = [artistName]

            amdc = artistDBMediaDataClass(album=album, url=albumURL, artist=albumArtists, code=code, year=None)
            mediaData[mediaName].append(amdc)


        mediaData = {}
        mediaName = "Albums"
        mediaData[mediaName] = []
        for code, artistAlbum in artistAlbums.items():
            album        = artistAlbum["Name"]
            albumURL     = artistAlbum["URL"]
            albumArtists = [artistName]

            amdc = artistDBMediaDataClass(album=album, url=albumURL, artist=albumArtists, code=code, year=None)
            mediaData[mediaName].append(amdc)


        artist      = artistDBNameClass(name=artistName, err=None)
        meta        = artistDBMetaClass(title=None, url=artistURL)
        url         = artistDBURLClass(url=artistURL)
        ID          = artistDBIDClass(ID=artistID)
        pages       = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        profile     = artistDBProfileClass(general=generalData)
        media       = artistDBMediaClass()
        media.media = mediaData
        mediaCounts = self.getMediaCounts(media)
        info        = self.getInfo()
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, info=info)
        
        return adc
    
    
    ##############################################################################################################################
    ## File Info
    ##############################################################################################################################
    def getInfo(self):
        afi = artistDBFileInfoClass(info=self.fInfo)
        return afi
    
    

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