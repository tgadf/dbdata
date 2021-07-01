from ioUtils import getFile
from fsUtils import isFile
from webUtils import getHTML, isBS4, isBS4Tag
from math import ceil, floor
from dbBase import dbBase


class artistDBIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    

class artistDBTagClass:
    def __init__(self, tag, err=None):
        self.tag = tag
        if not isBS4Tag(tag):
            self.err = "NoTag"
        
    def get(self):
        return self.__dict__
    

class artistDBTextClass:
    def __init__(self, tag, err=None):
        self.text  = None
        self.err   = None
        if isBS4Tag(tag):
            self.text  = tag.text
        else:
            self.err = "NoTag"
        
    def get(self):
        return self.__dict__
    

class artistDBLinkClass:
    def __init__(self, link, err=None):
        self.href  = None
        self.title = None
        self.text  = None
        self.err   = None
        
        if isBS4Tag(link):
            self.href  = link.attrs.get('href')
            self.title = link.attrs.get('title')
            self.text  = link.text
        else:
            self.err = "NoLink"
        
    def get(self):
        return self.__dict__
    
            
class artistDBURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistDBNameClass:
    def __init__(self, name=None, native=None, err=None):
        self.name = name
        if native is None:
            self.native = name
        else:
            self.native = native
        self.err  = err
        
    def get(self):
        return self.__dict__
        
        
class artistDBMetaClass:
    def __init__(self, title=None, url=None, err=None):
        self.title = title
        self.url   = url
        self.err   = err
                
    def get(self):
        return self.__dict__
    

class artistDBMediaClass:
    def __init__(self, err=None):
        self.media = {}
        self.err   = err
        
    def get(self):
        return self.__dict__
    

class artistDBMediaDataClass:
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
    

class artistDBMediaAlbumClass:
    def __init__(self, url=None, album=None, aformat=None, err=None):
        self.url     = url
        self.album   = album
        self.aformat = aformat
        self.err     = err        
        
    def get(self):
        return self.__dict__

    
class artistDBMediaCountsClass:
    def __init__(self, err=None):
        self.counts = {}
        self.err    = err
        
    def get(self):
        return self.__dict__
    

class artistDBPageClass:
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
    

class artistDBProfileClass:
    def __init__(self, profile=None, aliases=None, members=None, sites=None, groups=None, 
                 formed=None, related=None, notes=None, share=None,
                 genres=None, search=None, external=None, variations=None, err=None):
        self.profile    = profile
        self.aliases    = aliases
        self.members    = members
        self.sites      = sites
        self.formed     = formed
        self.related    = related
        self.notes      = notes
        self.share      = share
        self.genres     = genres
        self.search     = search
        self.external   = external
        self.variations = variations
        self.err        = err
        
    def get(self):
        return self.__dict__
    

class artistDBURLInfo:
    def __init__(self, name=None, url=None, ID=None, err=None):
        self.name = name
        self.url  = url
        self.ID   = ID
        self.err  = err
        
    def get(self):
        return self.__dict__
    
    

class artistDBDataClass:
    def __init__(self, artist=None, meta=None, url=None, ID=None, pages=None, profile=None, media=None, mediaCounts=None, err=None):
        self.artist      = artist
        self.meta        = meta
        self.url         = url
        self.ID          = ID
        self.pages       = pages
        self.profile     = profile
        self.media       = media
        self.mediaCounts = mediaCounts
        self.err         = err
        
        
    def show(self):
        print("Artist Data Class")
        print("-------------------------")
        if self.artist.native != self.artist.name:
            print("Artist:  {0} ({1})".format(self.artist.name, self.artist.native))
        else:
            print("Artist:  {0}".format(self.artist.name))
        print("Meta:    {0}".format(self.meta.title))
        print("         {0}".format(self.meta.url))
        print("URL:     {0}".format(self.url.url))
        print("ID:      {0}".format(self.ID.ID))
        print("Profile: {0}".format(self.profile.get()))
        print("Pages:   {0}".format(self.pages.get()))
        print("Media:   {0}".format(self.mediaCounts.get()))
        for mediaType,mediaTypeAlbums in self.media.media.items():
            print("   {0}".format(mediaType))
            for album in mediaTypeAlbums:
                print("      {0}".format(album.album))     
        
    def get(self):
        return self.__dict__
    
    
    


class artistDBBase:
    def __init__(self, debug=False):
        self.debug  = debug
        self.bsdata = None
        self.bsfile = None
        
        
    def checkData(self):
        if self.bsdata is None:
            raise ValueError("There is no BS4 data!")
        
        
    def getNamesAndURLs(self, content):
        data = []
        if content is not None:
            for ref in content.findAll("a"):
                url    = ref.attrs['href']
                name   = ref.text

                ID = None
                data.append(artistDBURLInfo(name=name, url=url, ID=ID))
        return data

        
    def getDataBase(self, inputdata):
        if isinstance(inputdata, str):
            if isFile(inputdata):
                self.bsfile = inputdata
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
        
        #return self.parse()