from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistTidal import artistTidal
from dbUtils import utilsBase

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsTidal(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "Tidal"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistTidal(self.disc)
        self.dutils = utilsBase(self.disc)
        self.debug  = debug