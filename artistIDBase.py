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
                raise ValueError("Not Ready!")
        return self.getArtistIDFromPatterns(self.s, self.patterns)