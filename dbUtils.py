from hashlib import md5, blake2b, sha256, sha1
import urllib
from fsUtils import mkSubDir, setFile, isFile
from ioUtils import saveFile
from time import sleep
from urllib.parse import quote


class utilsBase:
    def __init__(self, disc=None, debug=False):
        self.disc      = disc
        self.debug     = debug
        if self.disc is not None:
            self.maxModVal = self.disc.getMaxModVal()
            self.artistDir = self.disc.getArtistsDir()
        else:
            self.maxModVal = None
            self.artistDir = None


    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    
    def getDiscIDHashMod(self, artistID, modval):
        if artistID is None:
            return None
        try:
            ival = int(artistID)
        except:
            return None
        return ival % modval
    
        
    def getArtistSavename(self, artistID, page=1, credit=False, unofficial=False):
        modValue  = self.getDiscIDHashMod(artistID=artistID, modval=self.maxModVal)
        if modValue is not None:
            outdir    = mkSubDir(self.artistDir, str(modValue))
            if isinstance(page, int) and page > 1:
                outdir = mkSubDir(outdir, "extra")
                savename  = setFile(outdir, artistID+"-{0}.p".format(page))
            elif credit is True:
                outdir = mkSubDir(outdir, "credit")
                savename  = setFile(outdir, artistID+".p")
            elif unofficial is True:
                outdir = mkSubDir(outdir, "unofficial")
                savename  = setFile(outdir, artistID+".p")
            else:
                savename  = setFile(outdir, artistID+".p")
                
            return savename
        return None
    
    
    def downloadURL(self, url):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 

        if self.debug:
            print("Now Downloading {0}".format(url))

        request=urllib.request.Request(url,None,headers) #The assembled request
        response = urllib.request.urlopen(request)
        data = response.read() # The data u need
        
        return data, response.getcode()
    

    def downloadArtistURL(self, url, savename, force=False, sleeptime=2):
        if isFile(savename):
            if self.debug:
                print("{0} exists.".format(savename))
            if force is False:
                return False
            else:
                print("Downloading again.")
                  
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False
            
        print("Saving {0} (force={1})".format(savename, force))
        saveFile(idata=data, ifile=savename)
        print("Done. Sleeping for {0} seconds".format(sleeptime))
        sleep(sleeptime)
        
        if isFile(savename):
            return True
        else:
            return False    
    

################################################################################################################
# All Music
################################################################################################################
class utilsAllMusic(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None

        data = href[pos+len(ival)+1:]
        pos  = data.rfind("-")
        artistIDURL = data[(pos+3):]       
        artistID = artistIDURL.split("/")[0]
        try:
            data = href[pos+len(ival)+1:]
            pos  = data.rfind("-")
            artistIDURL = data[(pos+3):]       
            artistID = artistIDURL.split("/")[0]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(artistID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(artistID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(artistID, href))
            
        return artistID  
    

################################################################################################################
# MusicBrainz
################################################################################################################
class utilsMusicBrainz(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        uuid = href.split('/')[-1]
        
        m = md5()
        for val in uuid.split("-"):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16))
        
              
        try:
            int(artistID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(artistID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(artistID, href))
            
        return artistID
    

################################################################################################################
# Discogs
################################################################################################################
class utilsDiscogs(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None
        
        try:
            data = href[pos+len(ival)+1:]
            pos  = data.find("-")
            artistID = data[:pos]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(artistID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(artistID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(artistID, href))
            
        return artistID  
    

################################################################################################################
# LastFM
################################################################################################################
class utilsLastFM(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        self.baseURL = "https://www.last.fm/music/"
        self.relURL  = "/music/"
        
        
    def quoteIt(self, href, debug=False):
        if href is not None:
            if "+" in href:
                if debug:
                    print("Running Quote on {0}".format(href))
                href = quote("+".join([quote(x) for x in href.split("+")]))
                if debug:
                    print("    Resulting in {0}".format(href))
        return href
        
    def getArtistID(self, href, debug=False):
        if href.startswith(self.baseURL):
            if debug:
                print("Removing {0} from url --> {1}".format(self.baseURL,href))
            href = href[len(self.baseURL):]        
        if href.startswith(self.relURL):
            if debug:
                print("Removing {0} from url --> {1}".format(self.relURL,href))
            href = href[len(self.relURL):]
        name = href.split("/+albums")[0]
        if name.endswith("/"):
            name = href[:-1]
        if debug:
            print("Raw URL: {0}".format(name))
        #name = self.quoteIt(name, debug=debug)
        if debug:
            print("Raw URL (Post Quote): {0}".format(name))
        if name is None:
            return None
        name = "{0}{1}".format(self.baseURL,name)
        if debug:
            print("Full URL: {0}".format(name))
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e11))
        return artistID
    

################################################################################################################
# RockCorner
################################################################################################################
class utilsRockCorner(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, name, debug=False):
        if name is None:
            return None
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e9))
        return artistID
    

################################################################################################################
# MusicStack
################################################################################################################
class utilsMusicStack(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, name, debug=False):
        raise ValueError("This isn't ready yet!")
        if name is None:
            return None
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e9))
        return artistID
    

################################################################################################################
# RateYourMusic
################################################################################################################
class utilsRateYourMusic(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, name, debug=False):
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e10))
        return artistID
    

################################################################################################################
# Deezer
################################################################################################################
class utilsDeezer(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, url, debug=False):
        artistID = url.split("/")[-1]
        try:
            str(int(artistID))
        except:
            print("Could not determine artistID from URL {0}".format(url))
        
        return artistID
    

################################################################################################################
# AlbumOfTheYear
################################################################################################################
class utilsAlbumOfTheYear(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None
        
        try:
            data = href[pos+len(ival)+1:]
            pos  = data.find("-")
            artistID = data[:pos]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(artistID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(artistID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(artistID, href))
            
        return artistID  
    

################################################################################################################
# AppleMusic
################################################################################################################
class utilsAppleMusic(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, name, debug=False):
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e10))
        return artistID
    

################################################################################################################
# CDandLP
################################################################################################################
class utilsCDandLP(utilsBase):
    def __init__(self, disc=None):
        super().__init__(disc)
        
        
    def getArtistID(self, name, debug=False):
        raise ValueError("This isn't ready yet!")
        if name is None:
            return None
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        artistID  = str(int(hashval, 16) % int(1e9))
        return artistID
    
    

################################################################################################################
#
# All Music
#
################################################################################################################
class allmusicUtils:
    def __init__(self):
        self.baseURL  = "https://www.allmusic.com/search/"    
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None

        try:
            data = href[pos+len(ival)+1:]
            pos  = data.rfind("-")
            discID = data[(pos)+3:]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(discID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(discID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(discID, href))
            
        return discID
    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, href):
        code = None
        if href is not None:
            try:
                code = href.split('/')[-1]
                code = str(int(code))
            except:
                return None
        else:
            return None
        
        return code
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)


    
    
################################################################################################################
#
# Last FM
#
################################################################################################################
class lastfmUtils:
    def __init__(self):
        self.baseURL  = "https://www.last.fm/search/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, name, debug=False):
        if name is None:
            return None
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e11))
            
        return discID
    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        return self.getArtistID(name)
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)


    
    
################################################################################################################
#
# MusicBrainz
#
################################################################################################################
class musicbrainzUtils:
    def __init__(self):
        self.baseURL  = "https://musicbrainz.org/search?"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        uuid = href.split('/')[-1]
        
        m = md5()
        for val in uuid.split("-"):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16))
        
              
        try:
            int(discID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(discID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(discID, href))
            
        return discID
    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, href):
        code = None
        if href is not None:
            try:
                uuid = href.split('/')[-1]
                m = md5()
                for val in uuid.split("-"):
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                code  = str(int(hashval, 16))
            except:
                return None
        else:
            return None
        
        return code
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)



        
################################################################################################################
#
# Discogs
#
################################################################################################################
class discogsUtils:
    def __init__(self):
        self.baseURL  = "https://www.discogs.com/search/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    

    ###############################################################################
    #
    # Artist Functions
    #
    ###############################################################################
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        name = artist
        if artist.endswith(")"):
            name = None
            for x in [-3,-4,-5]:
                if artist is not None:
                    continue
                if abs(x) > len(artist):
                    continue
                if artist[x] == "(":
                    try:
                        val = int(artist[(x+1):-1])
                        name = artist[:x].strip()
                    except:
                        continue

            if name is None:
                name = artist
                
        return name
    
        
    def getArtistID(self, href, debug=False):
        if href is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        ival = "/artist"
        pos = href.find(ival)
        if pos == -1:
            if debug:
                print("Could not find discID in {0}".format(suburl))
            return None

        try:
            data = href[pos+len(ival)+1:]
            pos  = data.find("-")
            discID = data[:pos]
        except:
            print("Could not extract discID from {0}".format(href))
            return None
        
        try:
            int(discID)
        except:
            if debug:
                print("DiscID {0} is not an integer".format(discID))
            return None

        if debug:
            print("Found ID {0} from {1}".format(discID, href))
            
        return discID
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, href):
        code = None
        if href is not None:
            try:
                code = href.split('/')[-1]
                code = str(int(code))
            except:
                return None
        else:
            return None
        
        return code
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)




################################################################################################################
#
# Ace Bootlegs
#
################################################################################################################
class acebootlegsUtils:
    def __init__(self):
        self.baseURL  = "https://www.acebootlegs.com/search/"    
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, name, debug=False):
        if name is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        b = sha1()
        for val in name.split(" "):
            b.update(val.encode('utf-8'))
        hashval = b.hexdigest()
        discID  = int(hashval, 16) % int(1e12)
        return discID
    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        if name is None:
            if debug:
                print("Could not get artist disc ID from None!")
            return None
        
        b = sha1()
        for val in name.split(" "):
            b.update(val.encode('utf-8'))
        hashval = b.hexdigest()
        code    = int(hashval, 16) % int(1e15)
        return code
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)



################################################################################################################
#
# Rate Your Music
#
################################################################################################################
class rateyourmusicUtils:
    def __init__(self):
        self.baseURL  = "https://www.rateyourmusic.com/search/"    
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, title, debug=False):
        if title.startswith("[Artist") and title.endswith("]"):
            try:
                discID = str(int(title[7:-1]))
            except:
                return None
            
            return discID
        
        return None

    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, href):
        code = None
        if href is not None:
            try:
                code = href.split('/')[-1]
                code = str(int(code))
            except:
                return None
        else:
            return None
        
        return code
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)






################################################################################################################
#
# DatPiff
#
################################################################################################################
class datpiffUtils:
    def __init__(self):
        self.baseURL  = "https://www.rateyourmusic.com/search/"    
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, name, debug=False):
        
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e7))
            
        return discID

    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e7))
            
        return discID
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)



################################################################################################################
#
# The Rocker Corner
#
################################################################################################################
class rockcornerUtils:
    def __init__(self):
        self.baseURL  = "https://www.rockcorner.com/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, name, debug=False):
        
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e9))
            
        return discID

    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e9))
            
        return discID
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)



################################################################################################################
#
# CD and LP
#
################################################################################################################
class cdandlpUtils:
    def __init__(self):
        self.baseURL  = "https://www.cdandlp.com/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, url, debug=False):
        try:
            url = url.replace("https://", "")
        except:
            return None
        
        m = md5()
        for val in reversed(url.split("/")):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e14))
            
        return discID

    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        m = md5()
        for val in reversed(name.split(" ")):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e14))
            
        return discID
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)






################################################################################################################
#
# MusicStack
#
################################################################################################################
class musicstackUtils:
    def __init__(self):
        self.baseURL  = "https://www.musicstack.com/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, name, debug=False):        
        m = md5()
        for val in name.split(" "):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e8))
        return discID

    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        m = md5()
        for val in reversed(name.split(" ")):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e7))
            
        return discID
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)






################################################################################################################
#
# MetalStorm
#
################################################################################################################
class metalstormUtils:
    def __init__(self):
        self.baseURL  = "https://www.metalstorm.com/"
        self.disc     = None
        

    def setDiscogs(self, disc):
        self.disc = disc
        
        
    def getBaseURL(self):
        return baseURL
    
        
    def getArtistID(self, url, debug=False):
        try:
            codeData = url.url.split("band_id=")[1]
            discID   = codeData.split("&")[0]
        except:
            discID   = None
        return discID
    
    
    def getArtistName(self, artist, debug=False):
        if artist is None:
            return "None"
        return artist
    

    ###############################################################################
    #
    # Album Functions
    #
    ###############################################################################
    def getAlbumID(self, name):
        m = md5()
        for val in reversed(name.split(" ")):
            m.update(val.encode('utf-8'))
        hashval = m.hexdigest()
        discID  = str(int(hashval, 16) % int(1e14))
            
        return discID
    
    
    def getArtistModVal(self, artistID):
        if self.disc is not None:
            modValue  = self.getDiscIDHashMod(discID=artistID, modval=self.disc.getMaxModVal())
            return modValue
        else:
            raise ValueError("Must set discogs()!")
            

    
    ###############################################################################
    #
    # Basic Artist IO Functions
    #
    ###############################################################################
    def getArtistSavename(self, discID):
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None
    
    

    ###############################################################################
    #
    # Discog Hash Functions
    #
    ###############################################################################
    def getHashVal(self, artist, href):
        m = md5()
        if artist: m.update(artist)
        if href:   m.update(href)
        retval = m.hexdigest()
        return retval

    def getHashMod(self, hashval, modval):
        ival = int(hashval, 16)
        return ival % modval

    def getDiscIDHashMod(self, discID, modval):
        if discID == None:
            return None
        try:
            ival = int(discID)
        except:
            return None
        return ival % modval

    def getArtistHashVal(self, artist, href):
        artist = makeStrFromUnicode(artist)
        hashval = getHashVal(artist, href)
        return hashval

    def getFileHashVal(self, ifile):
        fname = getBaseFilename(ifile)
        hname = makeStrFromUnicode(fname)
        hashval = getHashVal(hname, None)
        return hashval

    def getArtistHashMod(self, artist, href, modval):
        hashval = getArtistHashVal(artist,href)
        return getHashMod(hashval, modval)

    def getFileHashMod(self, ifile, modval):
        hashval = getFileHashVal(ifile)
        return getHashMod(hashval, modval)
























