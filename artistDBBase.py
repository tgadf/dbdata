from ioUtils import getFile
from fsUtils import isFile
from fileInfo import fileInfo
from webUtils import getHTML, isBS4, isBS4Tag

from dbBase import dbBase

from datetime import datetime
from math import ceil, floor
from copy import copy, deepcopy


class artistDBIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
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
    

class artistDBTagClass:
    def __init__(self, tag, err=None):
        self.bstag = None
        self.err   = None
        
        if isBS4Tag(tag):
            self.bstag = deepcopy(tag)
        else:
            self.err = "NoTag"
            
    def getTag(self):
        return self.bstag
        
    def get(self):
        return self.__dict__
    

class artistDBTextClass:
    def __init__(self, text, err=None):        
        self.err   = None
        self.text = deepcopy(text.text.strip()) if isBS4Tag(text) else text.strip()
            
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
    def __init__(self, general=None, genres=None, tags=None, external=None, extra=None, err=None):
        self.general  = general
        self.genres   = genres
        self.tags     = tags
        self.external = external
        self.extra    = extra
        self.err      = err
        
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
    

class artistDBFileInfoClass:
    def __init__(self, info, err=None):
        self.called = datetime.now()
        if isinstance(info, fileInfo):
            self.created  = info.created
            self.filename = info.ifile
        else:
            self.created  = None
            self.filename = None
            self.err      = "NoFileInfo"
        
    def get(self):
        return self.__dict__
    

class artistDBDataClass:
    def __init__(self, artist=None, meta=None, url=None, ID=None, pages=None, profile=None, media=None, mediaCounts=None, info=None, err=None):
        self.artist      = artist
        self.meta        = meta
        self.url         = url
        self.ID          = ID
        self.pages       = pages
        self.profile     = profile
        self.media       = media
        self.mediaCounts = mediaCounts
        self.info        = info
        
        
    def show(self):
        print("Artist Data Class")
        print("-------------------------")
        if self.artist.native != self.artist.name:
            print("Artist:  {0} ({1})".format(self.artist.name, self.artist.native))
        else:
            print("Artist:  {0}".format(self.artist.name))
        print("Meta:    {0}".format(self.meta.title))
        print("         {0}".format(self.meta.url))
        print("Info:    {0}".format(self.info.filename))
        print("         {0}".format(self.info.created))
        print("         {0}".format(self.info.called))
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
        self.fInfo  = None
        
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
                self.fInfo  = fileInfo(self.bsfile)
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