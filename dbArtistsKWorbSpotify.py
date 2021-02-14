from artistKWorbSpotify import artistKWorbSpotify
from dbUtils import utilsKWorbSpotify
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
class dbArtistsKWorbSpotify:
    def __init__(self, debug=False):
        self.db     = "KWorbSpotify"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistKWorbSpotify(self.disc)
        self.dutils = utilsKWorbSpotify(self.disc)
        self.debug  = debug
        
        self.baseURL    = "https://kworb.net/"
        self.spotifyURL = "https://kworb.net/spotify"


        
    ##################################################################################################################
    # Spotify
    ##################################################################################################################
    def downloadKWorbSpotifyArtists(self,update=False):
        url      = "https://kworb.net/spotify/artists.html"
        savename = "kworb_spotifyartists.p"
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

        print("Found {0} Spotify Artists".format(len(data)))
        for i,item in enumerate(data):
            info = item["Artist"]
            url  = info.find('a').attrs['href']
            name = info.find('a').text
            savename = setFile(saveDir, "{0}.p".format(getBaseFilename(url)))
            if isFile(savename):
                continue
                print("Y\t",savename,'\t',url,'\t',name)
            else:
                fullURL = "{0}/{1}".format(self.spotifyURL, url)
                print("{0}/{1}".format(i,len(data)),"\t-\t",savename,'\t',fullURL,'\t',name)
                #dbArtistsKWorb().dutils.downloadArtistURL(url=fullURL, savename=savename, force=True)


        
    ##################################################################################################################
    # YouTube
    ##################################################################################################################
    def downloadKWorbSpotifyYouTubeArtists(self,update=False):
        url      = "https://kworb.net/youtube/archive.html"
        savename = "kworb_youtubeartists.p"
        if update is True:
            self.dutils.downloadArtistURL(url=url, savename=savename, force=True)

        bsdata = getHTML(savename)
        data   = []
        artistDir = self.disc.getArtistsDir()
        saveDir   = setDir(artistDir, "youtube")
        print(artistDir)
        for table in bsdata.findAll("table"):
            ths = [th.text for th in table.findAll("th")]
            for tr in table.findAll("tr")[1:]:
                item = dict(zip(ths, tr.findAll("td")))
                data.append(item)

        print(data)
                
        if False:
            bsdata = getHTML(savename)
            artistDir = self.disc.getArtistsDir()
            saveDir   = setDir(artistDir, "youtube")
            for div in bsdata.findAll("div", {"class": "subcontainer"}):
                if div.find("span", {"class": "pagetitle"}) is None:
                    continue
                for ref in div.findAll("a"):
                    href = ref.attrs['href']
                    url  = "{0}/{1}".format(self.youtubeURL, href)
                    savename = "{0}/{1}".format(saveDir, href.replace(".html", ".p"))
                    if isFile(savename):
                        print("Y\t",savename,'\t',url)
                    else:
                        print("-\t",savename,'\t',url)
                        #dbArtistsKWorb().dutils.downloadArtistURL(url=fullURL, savename=savename, force=True)


            for ifile in findExt(saveDir, ".p"):
                bsdata = getHTML(ifile)
                for table in bsdata.findAll("table"):
                    trs = table.findAll("tr")
                    for tr in trs[1:]:
                        ref  = tr.find("a")
                        href = ref.attrs['href']
                        name = ref.text
                        url  = "{0}/{1}".format(self.youtubeURL, href)
                        savename = "{0}/{1}".format(setDir(saveDir, "artist"), href.replace(".html", ".p"))
                        print(url,savename)

                        if isFile(savename) is False:
                            data, code = downloadURL(url)
                            from ioUtils import getFile, saveFile
                            saveFile(idata=data, ifile=savename)
                            sleep(3)
                            break                    
    
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def searchForArtist(self, artist):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        return