from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
from dbUtils import utilsRockCorner
from hashlib import md5


class artistRockCorner(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsRockCorner()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(artist.name)
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
        artistData = self.bsdata.find("section", {"id": "artist-info"})
        if artistData is None:            
            anc = artistDBNameClass(err=True)
            return anc
        
        h1 = artistData.find("h1")
        if h1 is None:
            anc = artistDBNameClass(err="NoH1")
            return anc
            
        artistName = h1.text
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
        artistData = self.bsdata.find("meta", {"property": "og:url"})
        if artistData is None:
            auc = artistRMURLClass(err=True)
            return auc
        
        url = artistData.attrs["content"]
        if url.find("/artist/") == -1:
            url = None
            auc = artistRMURLClass(url=url, err="NoArtist")
        else:
            auc = artistRMURLClass(url=url)

        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, name):
        artistID = self.dutils.getArtistID(name)
        aic = artistDBIDClass(ID=artistID)
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
        data   = {}
        apc = artistDBProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
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
    
    
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        
        mediaType = "Albums"
        amc.media[mediaType] = []
        
        artistSection = self.bsdata.find("section", {"id": "album-artist"})
        if artistSection is None:
            pass
            #raise ValueError("Cannot find Artist Section")
        else:
            articles = artistSection.findAll("article")
            for ia,article in enumerate(articles):
                ref = article.find('a')
                if ref is None:
                    raise ValueError("No ref in article")
                albumURL = ref.attrs['href']

                caption = ref.find("figcaption")
                if caption is None:
                    raise ValueError("No figcaption in article")

                b = caption.find("b")
                if b is None:
                    raise ValueError("No bold in caption")

                i = caption.find("i")
                if i is None:
                    raise ValueError("No italics in caption")

                albumName = b.text
                albumYear = i.text


                m = md5()
                for val in albumURL.split("/"):
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                code  = str(int(hashval, 16) % int(1e9))

                artists = [artist.name]

                amdc = artistDBMediaDataClass(album=albumName, url=albumURL, aclass=None, aformat=None, artist=artists, code=code, year=albumYear)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)
        
   
        mediaType = "Songs"
        amc.media[mediaType] = []
        
        singlesSection = self.bsdata.find("ol", {"id": "songs-list"})
        if singlesSection is None:
            pass
            #raise ValueError("Cannot find Singles Section")
        else:
            lis = singlesSection.findAll("li")
            for li in lis:
                ref = li.find('a')
                if ref is None:
                    raise ValueError("No ref in article")
                albumURL = ref.attrs['href']

                b = ref.find("b")
                if b is None:
                    raise ValueError("No bold in ref")

                albumName = b.text
                albumYear = None


                m = md5()
                for val in albumURL.split("/"):
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                code  = str(int(hashval, 16) % int(1e10))

                artists = [artist.name]

                amdc = artistDBMediaDataClass(album=albumName, url=albumURL, aclass=None, aformat=None, artist=artists, code=code, year=albumYear)
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