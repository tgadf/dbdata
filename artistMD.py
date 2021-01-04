from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4
from strUtils import fixName
from math import ceil, floor
from hashlib import md5

from dbBase import dbBase
from dbUtils import musicstackUtils

class artistMDIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistMDURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistMDNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
        self.err  = err
        
    def get(self):
        return self.__dict__
    

class artistMDMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistMDMediaDataClass:
    def __init__(self, album=None, url=None, aclass=None, aformat=None, artist=None, code=None, year=None, err=None):
        self.album   = album
        self.url     = url
        self.aclass  = aclass
        self.aformat = aformat
        self.artist  = artist
        self.code    = code
        self.year    = year
        self.err     = err
        
    def get(self):
        return self.__dict__
    

class artistMDMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistMDMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistMDPageClass:
    def __init__(self, ppp = None, tot = None, more=None, redo=None, err=None):
        self.ppp   = ppp
        self.tot   = tot
        if isinstance(ppp, int) and isinstance(tot, int):
            self.pages = int(ceil(tot/ppp))
        else:
            self.pages = None

        self.err   = err

        self.more  = more
        self.redo  = redo
        
    def get(self):
        return self.__dict__
    

class artistMDProfileClass:
    def __init__(self, profile=None, aliases=None, members=None, sites=None, groups=None, variations=None, err=None):
        self.profile    = profile
        self.aliases    = aliases
        self.members    = members
        self.sites      = sites
        self.groups     = groups
        self.variations = variations
        self.err        = err
        
    def get(self):
        return self.__dict__
    

class artistMDURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
        

class artistMDDataClass:
    def __init__(self, artist=None, url=None, ID=None, pages=None, profile=None, media=None, mediaCounts=None, err=None):
        self.artist      = artist
        self.url         = url
        self.ID          = ID
        self.pages       = pages
        self.profile     = profile
        self.media       = media
        self.mediaCounts = mediaCounts
        self.err         = err
        
    def get(self):
        return self.__dict__
        
        
    def show(self):
        print("MusicStack Artist Data Class")
        print("-------------------------")
        print("Artist: {0}".format(self.artist.name))
        print("URL:    {0}".format(self.url.url))
        print("ID:     {0}".format(self.ID.ID))
        print("Pages:  {0}".format(self.pages.get()))
        print("Media:  {0}".format(self.mediaCounts.get()))
        for mediaType,mediaTypeAlbums in self.media.media.items():
            print("   {0}".format(mediaType))
            for album in mediaTypeAlbums:
                print("      {0}".format(album.album))     


        
class artistMD(dbBase):
    def __init__(self, debug=False):
        self.debug  = debug
        self.data   = None
        self.dutils = musicstackUtils()
        
    def getData(self, inputdata):
        if isinstance(inputdata, str):
            if isFile(inputdata):
                try:
                    bsdata = getHTML(getFile(inputdata))
                except:
                    try:
                        bsdata = getHTML(getFile(inputdata, version=2))
                    except:
                        raise ValueError("Cannot read artist file: {0}".format(inputdata))
            else:
                try:
                    bsdata = getHTML(inputdata)
                except:
                    raise ValueError("Not sure about string input: {0} . It is not a file".format(inputdata))
        elif isBS4(inputdata):
            bsdata = inputdata
            pass
        else:
            raise ValueError("Not sure about input type: {0}".format(type(inputdata)))

        self.bsdata = bsdata
        
        return self.parse()
        
    def get(self):
        return self.__dict__
        
        
            
        
    def getNamesAndURLs(self, content):
        data = []
        if content is not None:
            for ref in content.findAll("a"):
                url    = ref.attrs['href']
                name   = ref.text

                ID = None
                data.append(artistMDURLInfo(name=name, url=url, ID=ID))
        return data





    #######################################################################################################################################
    ## Artist URL
    #######################################################################################################################################
    def getartistMDURL(self):
        auc = artistMDURLClass(url=None, err=None)
        return auc

    

    #######################################################################################################################################
    ## Artist ID
    #######################################################################################################################################
    def getartistMDDiscID(self, anc):
        try:
            artistName = anc.name
            artistID   = self.dutils.getArtistID(artistName)
        except:
            artistID = None
            
        if artistID is not None:
            aic = artistMDIDClass(ID=artistID, err=None)
        else:
            aic = artistMDIDClass(ID=None, err="IDError")
        return aic
    
    

    #######################################################################################################################################
    ## Artist Name
    #######################################################################################################################################
    def getartistMDName(self):
        h1s = self.bsdata.findAll("h1")        
        for h1 in h1s:
            name = h1.text
            anc = artistMDNameClass(name=name, err=None)
            return anc
        anc = artistMDNameClass(name=None, err="NoH1")
        return anc
    
    

    #######################################################################################################################################
    ## Artist Media
    #######################################################################################################################################
    def getartistMDMediaAlbum(self, td):
        amac = artistMDMediaAlbumClass()
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
    
    
    def getartistMDMedia(self):
        amc  = artistMDMediaClass()

        tables = self.bsdata.findAll("table", {"border": "0", "cellpadding": "5", "cellspacing": "0", "width": "100%"})
        for table in tables:
            trs = table.findAll("tr")
            mediaType = None
            for tr in trs:
                if tr.find('table') is not None:
                    continue
                b = tr.find('b')
                if b is not None:
                    mediaType = b.text
                    continue
                tds = tr.findAll("td")
                if len(tds) != 4:
                    continue

                album  = tds[0]
                try:
                    ref = album.find('a')
                    name = ref.text
                    url  = ref.attrs['href']
                except:
                    continue

                code = self.dutils.getAlbumID(url)
                label  = tds[1]
                year   = tds[2].text
                tracks = tds[3]

                amdc = artistMDMediaDataClass(album=name, url=url, aclass=None, aformat=None, artist=[], code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)        

            return amc

    

    #######################################################################################################################################
    ## Artist Media Counts
    #######################################################################################################################################        
    def getartistMDMediaCounts(self, media):
        
        amcc = artistMDMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc
        
    

    #######################################################################################################################################
    ## Artist Variations
    #######################################################################################################################################
    def getartistMDProfile(self):
        data = {}        
        apc  = artistMDProfileClass(profile=data.get("Formed"), aliases=data.get("Aliases"),
                                    members=data.get("Members"), groups=data.get("In Groups"),
                                    sites=data.get("Sites"), variations=data.get("Variations"))
        return apc


    
    #######################################################################################################################################
    ## Artist Pages
    #######################################################################################################################################
    def getartistMDPages(self):
        apc   = artistMDPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistMDPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistMDPageClass(err=err)
                return apc
            else:
                txt = x.text
                txt = txt.strip()
                txt = txt.replace("\n", "")
                retval = [tmp.strip() for tmp in txt.split('of')]

                try:
                    ppp   = int(retval[0].split('–')[-1])
                    tot   = int(retval[1].replace(",", ""))
                except:
                    err   = "int"
                    apc   = artistMDPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistMDPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistMDPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistMDPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistMDPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistMDPageClass()

    
    
    def parse(self):
        artist      = self.getartistMDName()
        url         = self.getartistMDURL()
        ID          = self.getartistMDDiscID(artist)
        pages       = self.getartistMDPages()
        profile     = self.getartistMDProfile()
        media       = self.getartistMDMedia()
        mediaCounts = self.getartistMDMediaCounts(media)
        
        err = [artist.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        adc = artistMDDataClass(artist=artist, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc