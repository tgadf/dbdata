from artistDiscogs import artistDiscogs
from dbUtils import utilsDiscogs
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsDiscogs:
    def __init__(self, debug=False):
        self.db     = "Discogs"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistDiscogs(self.disc)
        self.dutils = utilsDiscogs(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.discogs.com/"
        self.searchURL = "https://www.discogs.com/search/"

        self.ignores = {}
        

    
    ##################################################################################################################
    #
    # Ignores
    #
    ##################################################################################################################
    def isIgnore(self, url, name, useURL=True, useName=False):
        if useName is True:
            if url in list(self.ignores.values()):
                return True
        elif useURL is True:
            if url in list(self.ignores.keys()):
                return True
        return False


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1, credit=False, unofficial=False):
        if artistRef.startswith("/artist/") is False:
            print("Artist Ref needs to start with /artist/")
            return None
        
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        url     = urllib.parse.urljoin(url, "?sort=year%2Casc&limit=500") ## Make sure we get 500 entries)
        if unofficial is True:
            url     = urllib.parse.urljoin(url, "?type=Unofficial") ## Make sure we get 500 entries)
        if credit is True:
            url     = urllib.parse.urljoin(url, "?type=Credits") ## Make sure we get 500 entries)
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url 
    
        
    
    ##################################################################################################################
    # Search Functions
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, maxArtists=99, force=False, debug=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}

        h4s = bsdata.findAll("h4")
        
        for ih4,h4 in enumerate(h4s):
            spans = h4.findAll("span")
            ref   = None
            if len(spans) == 0:
                ref = h4.find("a")
            else:
                ref = spans[0].find("a")
                
            if ref is None:
                continue
                
            try:
                href   = ref.attrs.get('href')
                artist = ref.text.strip()
            except:
                print("Could not get artist/href from {0}".format(ref))
                continue
                
            if not href.endswith("?anv="):
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": artist}
                artistDB[href]["N"] += 1
                
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for ia,(href, hrefData) in enumerate(artistDB.items()):
            iArtist += 1
            if iArtist > maxArtists:
                break
            if href.startswith("/artist") is False:
                if debug:
                    print("href [{0}] does not start with /artist".format(href))
                continue
        
            discID   = self.dutils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.dutils.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',len(discID),'\t',url)
            if isFile(savename):
                if force is False:
                    if debug:
                        print("--> File exists.")
                    continue

            if debug:
                print("Downloading {0} to {1} (Force={2})".format(url, savename, force))
            retval = self.dutils.downloadArtistURL(url, savename, force=force, debug=True)
            #retval = self.dutils.downloadArtistURL(url, savename, force=force, sleeptime=self.sleeptime, 
            if debug:
                print("Finished Downloading: Result is {0}".format(retval))
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL        
        url = urllib.parse.urljoin(baseURL, "{0}{1}{2}".format("?q=", quote(artist), "&limit=25&type=artist"))
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