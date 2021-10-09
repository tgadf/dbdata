from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBURLInfo, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass, artistDBTagClass
from strUtils import fixName
from dbUtils import utilsKWorbiTunes
from webUtils import removeTag
from fileUtils import getBaseFilename


class artistKWorbiTunes(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils   = utilsKWorbiTunes()
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
        media       = self.getMedia(artist.name)
        mediaCounts = self.getMediaCounts(media)
        ID          = self.getID(artist, mediaCounts)
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
    ## Artist Name
    ##############################################################################################################################
    def getName(self):        
        title      = self.bsdata.find("span", {"class": "pagetitle"})        
        artistName = None
        if title is not None:
            artistName = title.text.split(" | ")[0].strip()
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
            artistURL = "https://kworb.net/itunes/artist/{0}.html".format(getBaseFilename(self.inputdata))
            auc = artistDBURLClass(url=artistURL)        
            return auc
        else:
            auc = artistDBURLClass(url=None, err="NoInput")        
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
        apc = artistDBProfileClass()
        return apc            

    
    
    ##############################################################################################################################
    ## Artist Media
    ##############################################################################################################################
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        
        mediaType = "Albums"
        amc.media[mediaType] = []

        for table in self.bsdata.findAll("table"):
            trs = table.findAll("tr")
            for itr,tr in enumerate(trs):
                tds = tr.findAll("td")
                for itd,td in enumerate(tds):
                    div=td.find("div", {"class": "wrap"})
                    if div is not None:
                        name = div.text
                        if name.startswith("Album: "):
                            mediaType = "Album"
                            title = name[7:]
                        else:
                            mediaType = "Single"
                            title = name
                        if amc.media.get(mediaType) is None:
                            amc.media[mediaType] = []
                
                        code = self.dbUtils.getAlbumCode(name=title, url=mediaType)

                        amdc = artistDBMediaDataClass(album=title, url=None, aclass=None, aformat=None, artist=artist, code=code, year=None)
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