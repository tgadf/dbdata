import re
from hashlib import md5

class artistIDBase:
    def __init__(self, debug=False):
        self.debug = debug
        self.err   = None

    def extractID(self, sval):
        groups   = None if sval is None else sval.groups()
        artistID = None if groups is None else str(groups[0])
        return artistID

    def extractGroups(self, sval):
        groups   = None if sval is None else sval.groups()
        return groups

    def testFormat(self, s):
        self.err = None
        if s is None:
            self.err = "None"            
        elif not isinstance(s, str):
            self.err = type(s)

    def getErr(self):
        return self.err


    def getArtistIDFromPatterns(self, s, patterns):
        s = str(s)

        ######################################################    
        ## Test For Format
        ######################################################
        self.testFormat(s)
        if self.err is not None:
            return None

        ######################################################    
        ## Pattern Matching
        ######################################################
        for pattern in patterns:
            artistID = self.extractID(re.search(pattern, s))
            if artistID is not None:
                return artistID

        self.err = "NoMatch"
        return None
    
    
    
##########################################################################
## Discogs
##########################################################################
class artistIDDiscogs(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns  = [r'https://www.discogs.com/artist/([\d]+)-([^/?]+)']
        patterns += [r'https://www.discogs.com/artist/([\d]+)']
        patterns += [r'/artist/([\d]+)']
        patterns += [r'artist/([\d]+)']
        patterns += [r'([\d]+)-([^/?]+)']
        patterns += [r'([\d]+)']
        self.patterns = patterns

    def getArtistID(self, s):
        self.s = str(s)
        return self.getArtistIDFromPatterns(self.s, self.patterns)
    
    
##########################################################################
## AllMusic
##########################################################################
class artistIDAllMusic(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns  = [r'https://www.allmusic.com/artist/mn([\d]+)-([^/?]+)']
        patterns += [r'https://www.allmusic.com/artist/mn([\d]+)']
        patterns += [r'/artist/mn([\d]+)']
        patterns += [r'artist/mn([\d]+)']
        patterns += [r'mn([\d]+)-([^/?]+)']
        patterns += [r'mn([\d]+)']
        self.patterns = patterns

    def getArtistID(self, s):
        self.s = str(s)
        return self.getArtistIDFromPatterns(self.s, self.patterns)
    
    
##########################################################################
## Deezer
##########################################################################
class artistIDDeezer(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns  = [r'https://www.deezer.com/artist/([\d]+)']
        patterns += [r'/artist/([\d]+)']
        patterns += [r'artist/([\d]+)']
        patterns += [r'([\d]+)']
        self.patterns = patterns

    def getArtistID(self, s):
        self.s = str(s)
        return self.getArtistIDFromPatterns(self.s, self.patterns)
    
    
##########################################################################
## Genius
##########################################################################
class artistIDGenius(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns = [r'https://genius.com/artists/*']
        self.patterns = patterns

    def getArtistID(self, s):
        self.s = str(s)
        
        ######################################################    
        ## Test For Format
        ######################################################
        self.testFormat(s)
        if self.err is not None:
            return None
        
        for pattern in self.patterns:
            if re.search(pattern) is not None:
                return self.getArtistIDFromPatterns(self.s, self.patterns)
        return None
    

##########################################################################
## MusicBrainz
##########################################################################
class artistIDMusicBrainz(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns  = [r'https://musicbrainz.org/artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'/artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        self.patterns = patterns
        
    def getArtistID(self, s):
        self.s = str(s)
        
        ######################################################    
        ## Test For Format
        ######################################################
        self.testFormat(s)
        if self.err is not None:
            return None

        ######################################################    
        ## Pattern Matching
        ######################################################
        for pattern in self.patterns:
            groups = self.extractGroups(re.search(pattern, s))
            if groups is not None:
                m = md5()
                for val in groups:
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                artistID = str(int(hashval, 16))
                return artistID
            
            
##########################################################################
## LastFM
##########################################################################
class artistIDLastFM(artistIDBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        patterns  = [r'https://musicbrainz.org/artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'/artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'artist/([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        patterns += [r'([\w]+)-([\w]+)-([\w]+)-([\w]+)-([\w]+)']
        self.patterns = patterns
        
    def quoteIt(self, href, debug=False):
        retval = href
        if href is not None:
            retval = href if "+" not in href else quote("+".join([quote(x) for x in href.split("+")]))
        return retval
        
        
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
    
    
    def getArtistID(self, s):
        self.s = str(s)
        
        ######################################################    
        ## Test For Format
        ######################################################
        self.testFormat(s)
        if self.err is not None:
            return None

        ######################################################    
        ## Pattern Matching
        ######################################################
        for pattern in self.patterns:
            groups = self.extractGroups(re.search(pattern, s))
            if groups is not None:
                m = md5()
                for val in groups:
                    m.update(val.encode('utf-8'))
                hashval = m.hexdigest()
                artistID = str(int(hashval, 16))
                return artistID
