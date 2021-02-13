from artistKWorbiTunes import artistKWorbiTunes
from dbUtils import utilsKWorbiTunes
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fileUtils import getBaseFilename
from fsUtils import isFile, setDir, setFile
from searchUtils import findExt


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsKWorbiTunes:
    def __init__(self, debug=False):
        self.db     = "KWorbiTunes"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistKWorbiTunes(self.disc)
        self.dutils = utilsKWorbiTunes(self.disc)
        self.debug  = debug
        
        self.baseURL    = "https://kworb.net/"
        self.youtubeURL = "https://kworb.net/youtube"
        self.searchURL  = None


        
    ##################################################################################################################
    # iTunes
    ##################################################################################################################
    def downloadKWorbiTunesArtists(self,update=False):
        url      = "https://kworb.net/itunes/extended.html"
        savename = "kworb_itunesartists.p"
        if update is True:
            self.dutils.downloadArtistURL(url=url, savename=savename, force=True)

        bsdata = getHTML(savename)
        data   = []
        artistDir = self.disc.getArtistsDir()
        saveDir   = setDir(artistDir, "data")
        print(artistDir)
        for table in bsdata.findAll("table"):
            ths = [th.text for th in table.findAll("th")]
            for tr in table.findAll("tr")[1:]:
                item = dict(zip(ths, tr.findAll("td")))
                data.append(item)

        for item in data:
            info = item["Artist"]
            url  = info.find('a').attrs['href']
            name = info.find('a').text
            savename = setFile(saveDir, "{0}.p".format(getBaseFilename(url)))
            
            if isFile(savename):
                continue
                print("Y\t",savename,'\t',url,'\t',name)
            else:
                fullURL = "{0}/{1}".format(self.youtubeURL, quote(url))
                print("-\t",savename,'\t',fullURL,'\t',name)
                self.dutils.downloadArtistURL(url=fullURL, savename=savename, force=True)
    
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return