from artistAllMusic import artistAllMusic
from dbUtils import utilsAllMusic
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsAllMusic:
    def __init__(self, debug=False):
        self.db     = "AllMusic"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistAllMusic(self.disc)
        self.dutils = utilsAllMusic(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.allmusic.com/"        
        self.searchURL = "https://www.allmusic.com/search/"

        
        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURLCredit(self, artistRef, page=1):
        url = "{0}/credits".format(artistRef)
        return url
    
    def getArtistURLCompostion(self, artistRef, page=1):
        url = "{0}/compositions".format(artistRef)
        return url
    
    def getArtistURLSong(self, artistRef, page=1):
        url = "{0}/songs".format(artistRef)
        return url
    
    def getArtistURLFromID(self, artistID, credit=False, song=False, composition=False):
        if str(artistID).startswith("mn"):
            artistRef = "{0}artist/{1}".format(self.baseURL, artistID)
        else:
            try:
                int(artistID)
                artistRef = "{0}artist/mn{1}".format(self.baseURL, artistID)
            except:
                raise ValueError("Not sure how to get URL from [{0}]".format(artistID))
                
        if credit is True:
            url = self.getArtistURLCredit(artistRef)
        elif song is True:
            url = self.getArtistURLSong(artistRef)
        elif composition is True:
            url = self.getArtistURLComposition(artistRef)
        else:
            url = self.getArtistURL(artistRef)
        return url
    
    def getArtistURL(self, artistRef, page=1):
        url = "{0}/discography/all".format(artistRef)
        return url
        
        if artistRef.startswith("http"):
            return artistRef
        else:
            baseURL = self.baseURL
            url     = urllib.parse.urljoin(baseURL, quote(artistRef))
            return url

        if artistRef.startswith("/artist/") is False:
            print("Artist Ref needs to start with /artist/")
            return None
        
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, quote(artistRef))
        url     = urllib.parse.urljoin(url, "?sort=year%2Casc&limit=500") ## Make sure we get 500 entries)
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
        return url

        
    
    ##################################################################################################################
    #
    # Search Functions
    #
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, maxArtists=99, force=False, debug=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "search-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist"})
            for li in lis:
                divs = li.findAll("div", {"class": "name"})
                for div in divs:
                    link     = div.find("a")
                    href     = link.attrs['href']
                    tooltip  = link.attrs['data-tooltip']
                    try:
                        from json import loads
                        tooltip = loads(tooltip)
                        artistID = tooltip['id']
                    except:
                        artistID = None
            
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
            
            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("artists/", quote(artist)))                  
        return url
    
        
    def searchForArtist(self, artist, maxArtists=99, force=False, debug=False):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        try:
            data, response = self.dutils.downloadURL(url)
        except:
            return False
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data, maxArtists, force, debug)
    
        
        
    ##################################################################################################################
    #
    # Search Functions (w/ Song)
    #
    ##################################################################################################################
    def searchForArtistSong(self, artist, artistID, force=False):
        print("\n\n===================== Searching Songs For {0} , {1} =====================".format(artist, artistID))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        try:
            data, response = self.dutils.downloadURL(url)
        except:
            return False
        if response != 200:
            print("Error downloading {0}".format(url))
            return False
    
        self.parseSearchArtistSong(artist, artistID, data, force)
        
      
    def parseSearchArtistSong(self, artist, artistID, data, force=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "search-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist"})
            for li in lis:
                divs = li.findAll("div", {"class": "name"})
                for div in divs:
                    link     = div.find("a")
                    href     = link.attrs['href']
                    tooltip  = link.attrs['data-tooltip']
                    try:
                        from json import loads
                        tooltip = loads(tooltip)
                        linkartistID = tooltip['id']
                    except:
                        linkartistID = None
            
                    if artistDB.get(href) is None:
                        artistDB[href] = {"N": 0, "Name": artist}
                    artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            discID   = self.dutils.getArtistID(href)
            if discID != artistID:
                continue
            url      = self.getArtistURLSong(href)
            savename = self.dutils.getArtistSavename(discID, song=True)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue
                    
            self.dutils.downloadArtistURL(url, savename, force=force)

    
        
        
    ##################################################################################################################
    #
    # Search Functions (w/ Composition)
    #
    ##################################################################################################################
    def searchForArtistComposition(self, artist, artistID, force=False):
        print("\n\n===================== Searching Composition For  {0} , {1} =====================".format(artist, artistID))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        try:
            data, response = self.dutils.downloadURL(url)
        except:
            return False
        if response != 200:
            print("Error downloading {0}".format(url))
            return False
    
        self.parseSearchArtistComposition(artist, artistID, data, force)
        
      
    def parseSearchArtistComposition(self, artist, artistID, data, force=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "search-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist"})
            for li in lis:
                divs = li.findAll("div", {"class": "name"})
                for div in divs:
                    link     = div.find("a")
                    href     = link.attrs['href']
                    tooltip  = link.attrs['data-tooltip']
                    try:
                        from json import loads
                        tooltip = loads(tooltip)
                        linkartistID = tooltip['id']
                    except:
                        linkartistID = None
            
                    if artistDB.get(href) is None:
                        artistDB[href] = {"N": 0, "Name": artist}
                    artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            discID   = self.dutils.getArtistID(href)
            if discID != artistID:
                continue
            url      = self.getArtistURLComposition(href)
            savename = self.dutils.getArtistSavename(discID, composition=True)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)
    
        
        
    ##################################################################################################################
    #
    # Search Functions (w/ Credit)
    #
    ##################################################################################################################
    def searchForArtistCredit(self, artist, artistID, force=False):
        print("\n\n===================== Searching For {0} , {1} =====================".format(artist, artistID))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        try:
            data, response = self.dutils.downloadURL(url)
        except:
            return 0
        if response != 200:
            print("Error downloading {0}".format(url))
            return False
    
        numDownload = self.parseSearchArtistCredit(artist, artistID, data, force)
        return numDownload
        
      
    def parseSearchArtistCredit(self, artist, artistID, data, force=False):
        if data is None:
            return None
        
        numDownload = 0
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}
        
        uls = bsdata.findAll("ul", {"class": "search-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist"})
            for li in lis:
                divs = li.findAll("div", {"class": "name"})
                for div in divs:
                    link     = div.find("a")
                    href     = link.attrs['href']
                    tooltip  = link.attrs['data-tooltip']
                    try:
                        from json import loads
                        tooltip = loads(tooltip)
                        linkartistID = tooltip['id']
                    except:
                        linkartistID = None
            
                    if artistDB.get(href) is None:
                        artistDB[href] = {"N": 0, "Name": artist}
                    artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
        
            discID   = self.dutils.getArtistID(href)
            if discID != artistID:
                continue
            url      = self.getArtistURLCredit(href)
            savename = self.dutils.getArtistSavename(discID, credit=True)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)
            numDownload += 1
            
        return numDownload