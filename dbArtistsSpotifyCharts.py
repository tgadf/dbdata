from dbArtistsBase import dbArtistsBase
from dbBase import dbBase
from artistSpotifyCharts import artistSpotifyCharts
from dbUtils import utilsSpotifyCharts

##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsSpotifyCharts(dbArtistsBase):
    def __init__(self, debug=False):
        self.db     = "SpotifyCharts"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistSpotifyCharts(self.disc)
        self.dutils = utilsSpotifyCharts()
        self.debug  = debug