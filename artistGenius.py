from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass, artistDBTagClass
from strUtils import fixName
import regex
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
    def isLatin(self, value):
        if regex.search(r'\p{IsLatin}', value):
            return True
        return False
    
    def getKorean(self, value):
        return regex.compile(r"\s\([\p{IsHangul}]+\)").search(value)
    def getThai(self, value):
        return regex.compile(r"\s\([\p{IsThai}]+\)").search(value)
    def getHebrew(self, value):
        return regex.compile(r"\s\([\p{IsHebrew}]+\)").search(value)
    def getRussian(self, value):
        return regex.compile(r"\s\([\p{IsCyrillic}]+\)").search(value)
    def getJapanChina(self, value):
        return regex.compile(r"\s\([\p{IsHan}\p{IsBopo}\p{IsHira}\p{IsKatakana}]+\)").search(value)
    
    
    def splitNativeName(self, artistName):
        names = artistName.split()
        ## Rough syntax for non-Latin name with Latin name in ()
        if not self.isLatin(names[0]) and names[-1].endswith(")"):
            native = []
            latin  = []
            for i,name in enumerate(names):
                if name.startswith("("):
                    for latinname in names[i:]:
                        latin.append(latinname.replace("(", "").replace(")", ""))
                    break
                native.append(name)

            native = " ".join(native)
            latin  = " ".join(latin)
            return latin,native
        elif self.isLatin(names[0]) and names[-1].endswith(")"):
            for getlang in [self.getKorean, self.getThai, self.getJapanChina, self.getRussian, self.getHebrew]:
                result = getlang(artistName)
                if result is not None:
                    span   = result.span()
                    latin  = artistName[:span[0]]
                    native = artistName[(span[0]+2):(span[1]-1)]
                    return latin,native
                
            for key in ['GRC', 'band', 'FRA', 'Producer', 'Band', 'Russia', 'rapper', 'QC', 'Rapper', 'DEU', 'DNK', 'RUS', 'PRT', 'UK', 'Rap', 'KOR', 'HRV', 'RU', 'SA', 'GR', 'BLR', 'BEL', 'ARG', 'SWE', 'Rock', 'producer', 'Electronic', 'BE', 'CAN', 'Canada', 'rap', 'POL', 'Musical artist', 'UKR', 'FR', 'CA', 'trumpeter', 'Gospel Singer-Songwriter', 'grunge', 'US', 'psytrance', 'NOR', 'USA', 'FI', 'JP', 'Hip-Hop', 'DJ', 'IRL', 'DE', 'Sweden', 'group', 'KC', 'Pop', 'Aus', 'Thai Artist', 'dancehall reggae', 'Group', 'vocal group', 'BRA', 'BGR', 'PL', 'MAR', 'Producers', 'Prod']:
                if artistName.endswith(" ({0})".format(key)):
                    artistName = artistName.replace(" ({0})".format(key), "")
            return artistName,None
        else:
            return artistName,None
            
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
        
        latinName,nativeName = self.splitNativeName(artistName)
        anc = artistDBNameClass(name=latinName, native=nativeName, err=None)
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
        if url is None:
            aic = artistDBIDClass(ID=None, err="NoURL")
            return aic
            
        artistID = self.dutils.getArtistID(url, debug=False)
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
        apc = artistDBProfileClass()
        return apc            
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