from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
import json
from dbUtils import utilsDeezer
from hashlib import md5


class artistDeezer(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsDeezer()
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
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

    ##############################################################################################################################
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        h1 = self.bsdata.find("h1", {"id": "naboo_artist_name"})
        if h1 is None:
            anc = artistDBNameClass(name=None, err = "NoH1")
            return anc
        
        span = h1.find("span", {"itemprop": "name"})
        if span is None:
            anc = artistDBNameClass(name=None, err = "NoSpan")
            return anc
 
        artist = span.text
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
        h1 = self.bsdata.find("h1", {"id": "naboo_artist_name"})
        if h1 is None:
            auc = artistDBURLClass(url=None, err = "NoH1")
            return auc
        
        ref = h1.find("a")
        if ref is None:
            auc = artistDBURLClass(url=None, err = "NoSpan")
            return auc
 
        url = ref.attrs['href']
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
    def getMediaSingles(self):
        mediaType = "Singles"
        media = []
        
        div = self.bsdata.find("div", {"class": "naboo-head-artist-music"})
        if div is None:
            if self.debug:
                print("No tracks!")
            return media
            
           
        table = div.find("table")
        if table is None:
            if self.debug:
                print("No track table")
            return media
            
        trs = table.findAll("tr")
        if self.debug:
            print("Found {0} track rows".format(len(trs)))
        for itr,tr in enumerate(trs):
            if self.debug:
                print("  ",itr,'/',len(trs),'\t',len(tr.findAll("td")))
            
            track  = tr.find("td", {"class": "track"})
            title  = None
            if track is not None:
                span  = track.find("span", {"itemprop": "name"})
                if span is not None:
                    title = span.text.strip()
    
            artist = tr.find("td", {"class": "artist"})
            artistURL = None
            artistName = None
            if artist is not None:
                ref = artist.find("a", {"itemprop": "byArtist"})
                if ref:
                    artistURL  = ref.attrs['href']
                    artistName = ref.text
        
            album  = tr.find("td", {"class": "album"})
            albumURL  = None
            albumName = None
            if album is not None:
                ref = album.find("a", {"itemprop": "inAlbum"})
                if ref:
                    albumURL  = ref.attrs['href']
                    albumName = ref.text
                   
            if self.debug:
                print("Album Data: [Title={0}] , [URL={1}] , [Artist={2}]".format(title, albumURL, artistName))
            if not all([title,albumURL,artistName]):
                continue
                
            code = self.dutils.getAlbumCode(name=title, url=albumURL)

            #print(title,'\t',albumURL,'\t',artistName)
            amdc = artistDBMediaDataClass(album=title, url=albumURL, aclass=None, aformat=None, artist=[artistName], code=code, year=None)        
            media.append(amdc)
    
        return media
    
    
    def getMediaAlbums(self):
        mediaType = "Albums"
        media = []
        
        div = self.bsdata.find("div", {"class": "naboo_discography_album"})
        if div is None:
            if self.debug:
                print("No tracks!")
            return media
            
        table = div.find("table")
        if table is None:
            if self.debug:
                print("No album table")
            return media
            
        trs = table.findAll("tr")
        if self.debug:
            print("Found {0} track rows".format(len(trs)))
        for itr,tr in enumerate(trs):
            if self.debug:
                print("  ",itr,'/',len(trs),'\t',len(tr.findAll("td")))
            
            track  = tr.find("td", {"class": "track"})
            title  = None
            if track is not None:
                span  = track.find("span", {"itemprop": "name"})
                if span is not None:
                    title = span.text.strip()
    
            artist = tr.find("td", {"class": "artist"})
            artistURL = None
            artistName = None
            if artist is not None:
                ref = artist.find("a", {"itemprop": "byArtist"})
                if ref:
                    artistURL  = ref.attrs['href']
                    artistName = ref.text
        
            album  = tr.find("td", {"class": "album"})
            albumURL  = None
            albumName = None
            if album is not None:
                ref = album.find("a", {"itemprop": "inAlbum"})
                if ref:
                    albumURL  = ref.attrs['href']
                    albumName = ref.text
                   
            if self.debug:
                print("Album Data: [Title={0}] , [URL={1}] , [Artist={2}]".format(title, albumURL, artistName))
            if not all([title,albumURL,artistName]):
                continue
                
            code = self.dutils.getAlbumCode(name=title, url=albumURL)

            #print(title,'\t',albumURL,'\t',artistName)
            amdc = artistDBMediaDataClass(album=title, url=albumURL, aclass=None, aformat=None, artist=[artistName], code=code, year=None)        
            media.append(amdc)
    
        return media
    
    
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        
        amc.media["Singles"] = self.getMediaSingles()
        amc.media["Albums"]  = self.getMediaAlbums()
        
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