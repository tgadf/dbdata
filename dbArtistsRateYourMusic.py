from artistRateYourMusic import artistRateYourMusic
from dbUtils import utilsRateYourMusic
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setDir
from searchUtils import findPatternExt
from ioUtils import getFile, saveFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsRateYourMusic:
    def __init__(self, debug=False):
        self.db     = "RateYourMusic"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistRateYourMusic(self.disc)
        self.dutils = utilsRateYourMusic(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.rateyourmusic.com/"        
        self.searchURL = None


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        return url

        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return
    
    
    ##################################################################################################################
    # Parse Downloaded Files
    ##################################################################################################################
    def parseDownloadedFiles(self, previousDays=None, force=False):
        artistDir = self.disc.getArtistsDir()
        files     = self.getArtistRawHTMLFiles(previousDays=None, force=False)
        return
        dataDir   = setDir(artistDir, "data")
        files     = findPatternExt(dataDir, pattern="Rate Your Music", ext=".html")
        for ifile in files:
            htmldata = getFile(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            savename = self.dutils.getArtistSavename(artistID)
            saveFile(idata=htmldata, ifile=savename, debug=False)