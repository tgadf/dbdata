from artistDeezer import artistDeezer
from dbUtils import utilsDeezer
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile
import json



##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDeezer:
    def __init__(self, debug=False):
        self.db     = "Deezer"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDeezer(self.disc)
        self.dutils = utilsDeezer(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.deezer.com/"
        self.searchURL = "https://www.deezer.com/search/"

        self.ignores = {}


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistID, page=1):
        url = "https://www.deezer.com/us/artist/{0}/top_track".format(artistID)
        return url
    
        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, maxArtists=99, force=False, debug=False):
        if data is None:
            print("Data is None!")
            return None
        
        ## Parse data
        bsdata = getHTML(data)

        jdata = None
        for script in bsdata.findAll("script"):
            if len(script.contents) == 0:
                continue

            if script.contents[0].startswith("window.__DZR_APP_STATE__ = "):        
                try:        
                    jdata = json.loads(script.contents[0].replace("window.__DZR_APP_STATE__ = ", ""))
                except:
                    continue
                    
            if jdata is not None:
                break
                
        if jdata is None:
            print("Could not find JSON data in search results")
            return


        artistDB = {}
        for result in jdata["TOP_RESULT"]:
            try:
                artistID   = result["ART_ID"]
                artistName = result["ART_NAME"]
            except:
                print("No data in {0}".format(result))
                continue

            url = self.getArtistURL(artistID)
            if artistDB.get(url) is None:
                artistDB[url] = {"N": 0, "Name": artistName, "ID": artistID}
            artistDB[url]["N"] += 1
            if self.debug:
                print("[{0}]  ,  [{1}]".format(artistID, artistName))

        for result in jdata["ARTIST"]['data']:    
            try:
                artistID   = result["ART_ID"]
                artistName = result["ART_NAME"]
            except:
                print("No data in {0}".format(result))
                continue
            

            url = self.getArtistURL(artistID)
            if artistDB.get(url) is None:
                artistDB[url] = {"N": 0, "Name": artistName, "ID": artistID}
            artistDB[url]["N"] += 1
            if self.debug:
                print("[{0}]  ,  [{1}]".format(artistID, artistName))

                
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))

        iArtist = 0
        for url, hrefData in artistDB.items():
            iArtist += 1
            if iArtist > maxArtists:
                break

            artistID = hrefData["ID"]
            savename = self.dutils.getArtistSavename(artistID)
            name     = hrefData['Name']

            print(iArtist,'/',len(artistDB),'\t:',artistID,'\t',name,'\t',savename)

            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)

    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL    
        url = urllib.parse.urljoin(baseURL, "{0}".format(quote(artist))) 
        return url
    
        
    def searchForArtist(self, artist, maxArtists=99, force=False, debug=False):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.dutils.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data, maxArtists, force, debug)
                
        
    
    ##################################################################################################################
    # Extra Data
    ##################################################################################################################
    def artistIgnoreList(self):
        ignores  = ["Downloads", "Various Artists"]
        ignores += ["Glee", "Disney", "Sesame Street", "Nashville Cast"]
        ignores += ["Various Artists", "Vários intérpretes", "Various Interprets"]
        ignores += ["original score", "Downloads", "Glee Cast", "Sound Ideas", "Rain Sounds"]
        ignores += ["101 Strings", "TBS RADIO 954kHz", "Armin van Buuren ASOT Radio", "Piano Tribute Players"]
        ignores += ["Yoga Music", "GTA San Andreas"]

        return ignores