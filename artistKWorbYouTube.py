from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBURLInfo, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
from dbUtils import utilsKWorbYouTube
from webUtils import removeTag
from fileUtils import getBaseFilename


class artistKWorbYouTube(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils   = utilsKWorbYouTube()
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
        title      = self.bsdata.find("span", {"class": "pagetitle"})        
        artistName = None
        if title is not None:
            artistName = title.text.split(" | ")[0].strip()
            artistName = artistName.replace("YouTube Statistics", "").strip()
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
            artistURL="https://kworb.net/youtube/artist/{0}.html".format(getBaseFilename(self.inputdata))
            auc = artistDBURLClass(url=artistURL)        
            return auc
        else:
            auc = artistDBURLClass(url=None, err="NoFile")        
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
        mediaType = "Videos"
        amc.media[mediaType] = []
        
        for table in self.bsdata.findAll("table"):
            trs = table.findAll("tr")
            ths = [th.text for th in table.findAll("th")]
            for tr in trs[1:]:
                td = tr.find('td')
                ref = td.find("a")
                name = td.text
                url  = None
                if ref is not None:
                    url = ref.attrs['href']
                
                #https://kworb.net/youtube/video/fRh_vgS2dFE.html
                trackURL = "https://kworb.net/youtube/video/{0}.html".format(getBaseFilename(url))

                songData = name.split(' - ')
                artistName = songData[0]
                trackName  = " - ".join(songData[1:])
                
                removes = []
                removes = ["(Official Music Video)", "(Official Lyric Video)", "(Official Video (Short Version))",
                           "(Official Video)", "[Lyric Video]", "(Video Version)", "[Official Music Video]",
                           "(Official Audio)", "(Shazam Version)", "(Explicit)", "(Dance Video)", "(Lyric Video)",
                           "[Official Video]", "(Official Dance Video)", '(Acoustic)', '(Audio)', '(Visualizer)',
                           '(Video Commentary)', '(VEVO Footnotes)', '(Choir Version)', '(Fan Lip Sync Version)',
                           '(Trailer)', '(Teaser)']
                for rmText in removes:
                    trackName = trackName.replace(rmText, "").strip()
                while trackName.find("  ") != -1:
                    trackName = trackName.replace("  ", " ")
                    if len(trackName) <= 1:
                        break
                
                if len(trackName.strip()) == 0:
                    continue

                amdc = artistDBMediaDataClass(album=trackName, url=trackURL, aclass=None, aformat=None, artist=artistName, code=None, year=None)
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