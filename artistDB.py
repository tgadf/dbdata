class artistDBIDClass:
    def __init__(self, ID=None, err=None):
        self.ID=ID
        self.err=err
        
    def get(self):
        return self.__dict__
    
            
class artistDBURLClass:
    def __init__(self, url=None, err=None):
        self.url = url
        self.err = err
        
    def get(self):
        return self.__dict__
        
        
class artistDBNameClass:
    def __init__(self, name=None, err=None):
        self.name = name
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
    def __init__(self, profile=None, aliases=None, members=None, sites=None, groups=None, search=None, variations=None, err=None):
        self.profile    = profile
        self.aliases    = aliases
        self.members    = members
        self.sites      = sites
        self.groups     = groups
        self.variations = variations
        self.search     = search
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
        print("AllMusic Artist Data Class")
        print("-------------------------")
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