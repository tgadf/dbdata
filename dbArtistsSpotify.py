from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistSpotify import artistSpotify
from dbUtils import utilsBase

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsSpotify(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "Spotify"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistSpotify(self.disc)
        self.dutils = utilsBase(self.disc)
        self.debug  = debug