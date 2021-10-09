from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from strUtils import fixName
from dbUtils import musicbrainzUtils
from hashlib import md5


class artistMusicBrainz(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.utils = musicbrainzUtils()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(url)
        pages       = self.getPages()
        profile     = self.getProfile()
        media       = self.getMedia()
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
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        artistData = self.bsdata.find("div", {"class": "artistheader"})
        if artistData is None:
            anc = artistDBNameClass(err=True)
            return anc
        
        h1 = artistData.find("h1")
        if h1 is None:
            anc = artistDBNameClass(err="NoH1")
            
        ref = self.getNamesAndURLs(h1)
        try:
            artistName = ref[0].name
            anc = artistDBNameClass(name=artistName, err=None)
        except:
            anc = artistDBNameClass(err="TxtErr")
        
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
        artistData = self.bsdata.find("div", {"class": "artistheader"})
        if artistData is None:
            auc = artistDBURLClass(err=True)
            return auc
        
        h1 = artistData.find("h1")
        if h1 is None:
            auc = artistDBURLClass(err="NoH1")
            
        ref = self.getNamesAndURLs(h1)
        try:
            artistURL = ref[0].url
            auc = artistDBURLClass(url=artistURL, err=None)
        except:
            auc = artistDBURLClass(err="TxtErr")

        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, suburl):
        discID = self.utils.getArtistID(suburl.url)
        aic = artistDBIDClass(ID=discID)
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        apc   = artistDBPageClass()
        from numpy import ceil
        bsdata = self.bsdata

        try:
            pages  = bsdata.find("ul", {"class": "pagination"})
            lis    = pages.findAll("li")
            txts   = [li.text for li in lis]
            npages = 0
            for item in txts:
                try:
                    npages = max([npages, int(item)])
                except:
                    continue
                    
            apc   = artistDBPageClass(ppp=100, tot=100*npages, redo=False, more=True)
        except:
            apc   = artistDBPageClass(ppp=100, tot=1, redo=False, more=False)
            
        return apc
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):   
        ##
        ## Artist information
        ##
        artistInformation = {}
        properties = self.bsdata.find("dl", {"class": "properties"})
        if properties is not None:
            dds = properties.findAll("dd")
            for val in dds:
                attrs = val.attrs.get('class')
                if isinstance(attrs, list) and len(attrs) == 1:
                    attrKey = attrs[0]
                    refs    = val.findAll('a')
                    attrVal = [artistDBTextClass(val)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
                    artistInformation[attrKey] = attrVal

                    
        ##
        ## Genres
        ##
        genreList = self.bsdata.find("div", {"class": "genre-list"})
        genreData = [artistDBLinkClass(ref) for ref in genreList.findAll("a")] if genreList is not None else None

        
        ##
        ## Tags
        ##
        tagList = self.bsdata.find("div", {"id": "sidebar-tag-list"})
        tagData = [artistDBLinkClass(ref) for ref in tagList.findAll("a")] if tagList is not None else None

        
        ##
        ## External Links
        ##
        externalLinks = {}
        externalLinksList = self.bsdata.find("ul", {"class": "external_links"})
        if externalLinksList is not None:
            lis = externalLinksList.findAll("li")
            for li in lis:
                attrs = li.attrs.get('class')
                if isinstance(attrs, list) and len(attrs) == 1:
                    attrKey = attrs[0]
                    refs    = li.findAll('a')
                    attrVal = [artistDBTextClass(li)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
                    externalLinks[attrKey] = attrVal
                    
                    
        ##
        ## Extra
        ##
        tabs        = self.bsdata.find("div", {"class": "tabs"})
        refs        = tabs.findAll("a") if tabs is not None else None
        tabLinks    = [artistDBLinkClass(ref) for ref in refs] if refs is not None else None
        keys        = [x.text for x in tabLinks] if tabLinks is not None else None
        vals        = tabLinks
        tabsData    = dict(zip(keys, vals)) if (isinstance(keys, list) and all(keys)) else None
        extraData   = tabsData

                    
        apc = artistDBProfileClass(general=artistInformation, tags=tagData, genres=genreData, extra=extraData, external=externalLinks)
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
    
    
    def getMedia(self):
        amc  = artistDBMediaClass()
        
        
        mediaTypes = [x.text for x in self.bsdata.findAll("h3")]
        tables     = dict(zip(mediaTypes, self.bsdata.findAll("table")))

        for mediaType, table in tables.items():
            headers = [x.text for x in table.findAll("th")]
            trs = table.findAll('tr')
            for tr in trs[1:]:
                tds = tr.findAll("td")

                ## Year
                idx  = headers.index("Year")
                year = tds[idx].text

                ## Title
                idx    = headers.index("Title")
                refs   = [x.attrs['href'] for x in tds[idx].findAll('a')]
                if len(refs) == 0:
                    raise ValueError("No link for album")
                url    = refs[0]
                album  = tds[idx].text

                    
                m = md5()
                uuid = url.split("/")[-1]
                for val in uuid.split("-"):
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                code = int(hashval, 16)
                

                ## Artist
                idx     = headers.index("Artist")
                artists = []
                for artistVal in tds[idx].findAll('a'):
                    url = artistVal.attrs['href']
                    name = artistVal.text
                    m = md5()
                    uuid = url.split("/")[-1]
                    for val in uuid.split("-"):
                        m.update(val.encode('utf-8'))
                    hashval = m.hexdigest()
                    artists.append({"name": name, "url": url})
                       

                amdc = artistDBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=artists, code=code, year=year)
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