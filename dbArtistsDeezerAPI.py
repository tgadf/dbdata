from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistDeezerAPI import artistDeezerAPI
from dbUtils import utilsDeezerAPI

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDeezerAPI(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "DeezerAPI"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDeezerAPI(self.disc)
        self.dutils = utilsDeezerAPI()
        self.debug  = debug