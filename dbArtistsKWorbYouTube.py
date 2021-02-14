from artistKWorbYouTube import artistKWorbYouTube
from dbUtils import utilsKWorbYouTube
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
class dbArtistsKWorbYouTube:
    def __init__(self, debug=False):
        self.db     = "KWorbYouTube"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistKWorbYouTube(self.disc)
        self.dutils = utilsKWorbYouTube(self.disc)
        self.debug  = debug
        
        self.baseURL    = "https://kworb.net/"
        self.youtubeURL = "https://kworb.net/youtube"
        self.searchURL  = None


        
    ##################################################################################################################
    # YouTube
    ##################################################################################################################
    def downloadKWorbYouTubeArtists(self,update=False):
        url      = "https://kworb.net/youtube/archive.html"
        savename = "kworb_youtubeartists.p"
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

        print("Found {0} YouTube Artists".format(len(data)))
        for i,item in enumerate(data):
            info = item["Artist"]
            url  = info.find('a').attrs['href']
            name = info.find('a').text
            savename = setFile(saveDir, "{0}.p".format(getBaseFilename(url)))
            
            if isFile(savename):
                continue
                print("Y\t",savename,'\t',url,'\t',name)
            else:
                fullURL = "{0}/{1}".format(self.youtubeURL, quote(url))
                print("{0}/{1}".format(i,len(data)),"\t-\t",savename,'\t',fullURL,'\t',name)
                self.dutils.downloadArtistURL(url=fullURL, savename=savename, force=True)
    
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return