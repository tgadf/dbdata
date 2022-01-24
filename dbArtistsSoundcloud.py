from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistSoundcloud import artistSoundcloud
from dbUtils import utilsBase

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsSoundcloud(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "Soundcloud"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistSoundcloud(self.disc)
        self.dutils = utilsBase(self.disc)
        self.debug  = debug