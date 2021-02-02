from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBURLInfo, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
from dbUtils import utilsRateYourMusic


class artistRateYourMusic(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsRateYourMusic()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(artist)
        pages       = self.getPages()
        profile     = self.getProfile()
        media       = self.getMedia(artist, url)
        mediaCounts = self.getMediaCounts(media)
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

    ##############################################################################################################################
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        artistData = self.bsdata.find("h1", {"class": "artist_name_hdr"})
        if artistData is None:
            anc = artistDBNameClass(err="No H1")
            return anc
        
        artistName = artistData.text.strip()
        if len(artistName) > 0:
            artist = fixName(artistName)
            anc = artistDBNameClass(name=artist, err=None)
        else:
            anc = artistDBNameClass(name=artist, err="Fix")
        
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
        artistData = self.bsdata.find("meta", {"property": "og:url"})
        if artistData is None:
            auc = artistDBURLClass(err=True)
            return auc
        
        url = artistData.attrs["content"]
        if url.find("/artist/") == -1:
            url = None
            auc = artistDBURLClass(url=url, err="NoArtist")
        else:
            auc = artistDBURLClass(url=url)

        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, artist):
        discID = self.dbUtils.getArtistID(artist.name)
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
        profile = self.bsdata.find("div", {"class": "artist_info"})
        
        headers = profile.findAll("div", {"class": "info_hdr"})
        content = profile.findAll("div", {"class": "info_content"})
        
        headers = [x.text for x in headers]
        content = [x.text for x in content]
        
        data = dict(zip(headers, content))
               
        apc = artistDBProfileClass(profile=data.get("Formed"), aliases=data.get("Aliases"),
                                 members=data.get("Members"), groups=data.get("In Groups"),
                                 sites=data.get("Sites"), variations=data.get("Variations"))
        return apc

    
    
    ##############################################################################################################################
    ## Artist Media
    ##############################################################################################################################
    def getMediaAlbum(self, td):
        amac = artistDBMediaAlbumClass()
        for span in td.findAll("span"):
            attrs = span.attrs
            if attrs.get("class"):
                if 'format' in attrs["class"]:
                    albumformat = span.text
                    albumformat = albumformat.replace("(", "")
                    albumformat = albumformat.replace(")", "")
                    amac.format = albumformat
                    continue
            span.replaceWith("")

        ref = td.find("a")
        if ref:
            amac.url   = ref.attrs['href']
            amac.album = ref.text
        else:
            amac.err = "NoText"

        return amac
    
    
    def getMedia(self, artist, url):
        amc  = artistDBMediaClass()

        mediadatas = self.bsdata.findAll("div", {"id": "discography"})
        for mediadata in mediadatas:
            h3s        = mediadata.findAll("h3", {"class": "disco_header_label"})
            categories = [x.text for x in h3s]

            sufs    = mediadata.findAll("div", {"class": "disco_showing"})
            spans   = [x.find("span") for x in sufs]
            ids     = [x.attrs['id'] for x in spans]
            letters = [x[-1] for x in ids]


            for mediaType,suffix in dict(zip(categories, letters)).items():
                categorydata = mediadata.find("div", {"id": "disco_type_{0}".format(suffix)})
                albumdatas   = categorydata.findAll("div", {"class": "disco_release"})
                for albumdata in albumdatas:
                    
                    ## Code
                    codedata = albumdata.attrs['id']
                    code     = codedata.split("_")[-1]
                    try:
                        int(code)
                    except:
                        code = None
                        
                    ## Title
                    mainline = albumdata.find("div", {"class": "disco_mainline"})
                    maindata = self.getNamesAndURLs(mainline)
                    try:
                        album = maindata[0].name
                    except:
                        album = None
                        
                    try:
                        albumurl = maindata[0].url
                    except:
                        albumurl = None


                    ## Year
                    yeardata = albumdata.find("span", {"class": "disco_year_y"})
                    if yeardata is None:
                        yeardata = albumdata.find("span", {"class": "disco_year_ymd"})
                        
                    year     = None
                    if yeardata is not None:
                        year = yeardata.text

                    ## Artists        
                    artistdata   = albumdata.findAll("span")[-1]
                    albumartists = self.getNamesAndURLs(artistdata)
                    if len(albumartists) == 0:
                        albumartists = [artistDBURLInfo(name=artist.name, url=url.url.replace("https://rateyourmusic.com", ""), ID=None)]


                    amdc = artistDBMediaDataClass(album=album, url=albumurl, aclass=None, aformat=None, artist=albumartists, code=code, year=year)
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