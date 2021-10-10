from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass, artistDBTagClass
from strUtils import fixName
import json
from dbUtils import utilsAlbumOfTheYear
from hashlib import md5



class artistAlbumOfTheYear(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsAlbumOfTheYear()
        self.debug  = False
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(url.url)
        pages       = self.getPages()
        profile     = self.getProfile()        
        media       = self.getMedia(artist)
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
        script = self.bsdata.find("script", {"type": "application/ld+json"})
        if script is None:
            anc = artistDBNameClass(name=None, err = "NoJSON")
            return anc
            
        try:
            artist = json.loads(script.contents[0])["name"]
        except:
            anc = artistDBNameClass(name=None, err = "CouldNotCompileJSON")
            return anc
            
        anc = artistDBNameClass(name=artist, err=None)
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
        metalink = self.bsdata.find("meta", {"property": "og:url"})
        if metalink is None:
            auc = artistDBURLClass(err="NoLink")
            return auc
        
        try:
            url = metalink.attrs["content"]
        except:
            auc = artistDBURLClass(err="NoContent")
            return auc

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
        tot = 1
        apc   = artistDBPageClass(ppp=1, tot=tot, redo=False, more=False)
        return apc
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):      
        generalData = {}
        genreData   = None
        extraData   = None
        tagsData    = None
        
        artistInfo = self.bsdata.find("div", {"class": "artistTopBox info"})
        detailRows = artistInfo.findAll("div", {"class": "detailRow"})
        for row in detailRows:
            span = row.find("span")    
            if span is None:
                continue
            key  = span.text.strip() if span.text is not None else None
            key  = key[1:].strip() if (isinstance(key,str) and key.startswith("/")) else key
            refs = row.findAll("a")
            if len(refs) == 0:
                continue
            vals = [artistDBLinkClass(ref) for ref in refs] if (isinstance(refs, list) and len(refs) > 0) else None

            if key == "Genres":
                genreData = vals
            else:
                generalData[key] = vals
                
                
        relatedArtists = self.bsdata.find("div", {"class": "relatedArtists"})
        artistBlocks   = relatedArtists.findAll("div", {"class": "artistBlock"}) if relatedArtists is not None else None
        refs           = [artistBlock.find("a") for artistBlock in artistBlocks] if artistBlocks is not None else None
        if refs is not None:
            extraData = [artistDBLinkClass(ref) for ref in refs if ref is not None]        
                
                
        generalData = generalData if len(generalData) > 0 else None
                
        apc = artistDBProfileClass(general=generalData, genres=genreData, tags=tagsData, extra=extraData)
        return apc

    
    
    ##############################################################################################################################
    ## Artist Media
    ############################################################################################################################## 
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        mediaType = "Albums"
        
        albumsData = self.bsdata.findAll("div", {"class": "albumBlock"})
        for albumData in albumsData:
            ## Name
            albumName = albumData.find("div", {"class": "albumTitle"})
            albumTitle = None
            if albumName is not None:
                albumTitle = albumName.text        
                
            ## URL
            albumURL  = albumData.find("a")
            albumHREF = None
            if albumURL is not None:
                albumHREF = albumURL.attrs['href']
                  
            ## Year
            albumYear = None
            albumDate = albumData.find("div", {"class": "date"})
            if albumDate is not None:
                albumYear = albumDate.text

            mediaTypeData = albumData.find("div", {"class": "type"})
            if mediaTypeData:
                mediaType = mediaTypeData.text
            else:
                mediaType = "Albums"
                
            code = self.dutils.getAlbumCode(name=albumTitle, url=albumHREF)
                
            amdc = artistDBMediaDataClass(album=albumTitle, url=albumHREF, aclass=None, aformat=None, artist=[artist.name], code=code, year=albumYear)
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType].append(amdc)
            if self.debug:
                print("\t\tAdding Media ({0} -- {1})".format(album, url))  

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