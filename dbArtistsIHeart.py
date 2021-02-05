from artistIHeart import artistIHeart
from dbUtils import utilsIHeart
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsIHeart:
    def __init__(self, debug=False):
        self.db     = "IHeart"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistIHeart(self.disc)
        self.dutils = utilsIHeart(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.iheart.com"
        self.searchURL = "https://www.iheart.org/search"

        
        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        if artistRef.startswith("/"):
            url = "{0}{1}".format(self.baseURL, artistRef)
        else:
            url = "{0}/{1}".format(self.baseURL, artistRef)
            
        if url.endswith("/"):
            url = "{0}{1}".format(url, "albums")
        else:
            url = "{0}/{1}".format(url, "albums")
            
        return url

        
    
    ##################################################################################################################
    #
    # Search Functions
    #
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, maxArtists=99, force=False, debug=False):
        return
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}

        for div in bsdata.findAll("div", {"class": "section"}):
            refs = div.findAll("a")
            for ref in refs:
                if ref.find("img") is not None:
                    continue
                href = ref.attrs['href']
                artist = ref.text
                
                if href.startswith("/artist/") is False:
                    continue
                
                #print(artist,"\t",href)
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": artist}
                artistDB[href]["N"] += 1
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
            if iArtist > maxArtists:
                break
        
            discID   = self.dutils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.dutils.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            #continue
            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        return
        baseURL = self.searchURL
        url = "{0}/?q={1}".format(self.searchURL, artist.replace(" ","+"))
        #url = urllib.parse.urljoin(baseURL, "{0}{1}".format("artists/", quote(artist)))                  
        return url
    
        
    def searchForArtist(self, artist, maxArtists=99, force=False, debug=False):
        print("This doesn't work...")
        return
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