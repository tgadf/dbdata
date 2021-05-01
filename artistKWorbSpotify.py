from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBURLInfo, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
from dbUtils import utilsKWorbSpotify
from webUtils import removeTag
from fileUtils import getBaseFilename


class artistKWorbSpotify(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils   = utilsKWorbSpotify()
        self.inputdata = None
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        self.inputdata = inputdata
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        pages       = self.getPages()
        profile     = self.getProfile()
        media       = self.getMedia()
        mediaCounts = self.getMediaCounts(media)
        ID          = self.getID(artist, mediaCounts)
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

    ##############################################################################################################################
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        title      = self.bsdata.find("strong", {"class": "pagetitle"})
        artistName = None
        if title is not None:
            artistName = title.text.replace(" - Spotify Chart History", "")
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
    def getURL(self):
        if self.inputdata is not None:
            artistURL = "https://kworb.net/spotify/artist/{0}.html".format(getBaseFilename(self.inputdata))
        auc = artistDBURLClass(url=artistURL)        
        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, artist, mediaCounts):
        discID = self.dbUtils.getArtistID(artist.name, str(mediaCounts.counts))
        aic = artistDBIDClass(ID=discID)
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
        data    = {}
        apc = artistDBProfileClass(profile=data.get("Formed"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc

    
    
    ##############################################################################################################################
    ## Artist Media
    ##############################################################################################################################
    def getMedia(self):
        amc  = artistDBMediaClass()
        mediaType = "Singles"
        amc.media[mediaType] = []

        table = self.bsdata.find("table")
        if table is not None:
            ths = table.findAll("th")
            ths = [th.text for th in ths]
            trs = table.findAll("tr")
            
            for itr,tr in enumerate(trs[1:]):
                trackData = dict(zip(ths,tr.findAll("td")))

                trackYear = trackData["Peak Date"].text[:4]

                trackURL  = trackData["Track"].find("a")
                if trackURL is not None:
                    trackURL = trackURL.attrs['href']
                trackName = trackData["Track"].text

                trackArtists = []
                for trackArtistData in trackData["With"].findAll("a"):
                    trackArtistURL  = trackArtistData.find("a")
                    if trackArtistURL is not None:
                        trackArtistURL = trackArtistURL.attrs['href']
                    trackArtistName = trackData["Track"].text
                    trackArtists.append({"Artist": trackArtistName, "URL": trackArtistURL})
                
                code = self.dbUtils.getAlbumCode(name=trackName, url=trackURL)

                amdc = artistDBMediaDataClass(album=trackName, url=trackURL, aclass=None, aformat=None, artist=trackArtists, code=code, year=trackYear)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
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