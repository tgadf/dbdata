from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistLastFMAPI import artistLastFMAPI
from dbUtils import utilsLastFMAPI

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsLastFMAPI(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "LastFMAPI"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistLastFMAPI(self.disc)
        self.dutils = utilsLastFMAPI()
        self.debug  = debug