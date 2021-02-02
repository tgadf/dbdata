from artistLastFM import artistLastFM
from dbUtils import utilsLastFM
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile



##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsLastFM:
    def __init__(self, debug=False):
        self.db     = "LastFM"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistLastFM(self.disc)
        self.dutils = utilsLastFM(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://www.last.fm/"
        self.searchURL = "https://www.last.fm/search/" #artists?q=Ariana+Grande

        self.ignores = {}


        
    ##################################################################################################################
    # Artist URL
    ##################################################################################################################
    def getArtistURL(self, artistRef, page=1):
        #print("getArtistURL(",artistRef,")")
        if artistRef.startswith("http"):
            url = artistRef
        else:
            baseURL = self.baseURL
            if artistRef.startswith("/") is True:
                #print("Join", end="\t")
                #url     = urllib.parse.urljoin(baseURL, quote(artistRef[1:]))
                url     = urllib.parse.urljoin(baseURL, artistRef[1:])
                #print(url)
            else:
                #url     = urllib.parse.urljoin(baseURL, quote(artistRef))
                url     = urllib.parse.urljoin(baseURL, artistRef)
            #print(url)
                
            if url.endswith("/") is False:
                url     = "{0}{1}".format(url, "/+albums?order=release_date")
            else:
                url     = "{0}{1}".format(url, "+albums?order=release_date")
                
            #print(url)
        
        if isinstance(page, int) and page > 1:
            pageURL = "&page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)
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
        
        artistDB  = {}
        uls = bsdata.findAll("ul", {"class": "artist-results"})
        for ul in uls:
            lis = ul.findAll("li", {"class": "artist-result"})
            for li in lis:
                h4 = li.find("h4")
                if h4 is None:
                    print("No artist information here!")
                    continue
                ref = h4.find('a')
                if ref is None:
                    print("No artist link information here")
                    continue
                attrs = ref.attrs
                href  = attrs['href']
                title = attrs['title']
                text  = ref.text
                artistID = self.dutils.getArtistID(href)                
                
                if self.debug:
                    print("[{0}]  ,  [{1}]  ,  [{2}]  ,  [{3}]".format(text, artistID, href, title))
        
                #print(name,'\t',url,'\t',artistID)
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": title}
                artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        for href, hrefData in artistDB.items():
            iArtist += 1
            if iArtist > maxArtists:
                break
        
            artistID = self.dutils.getArtistID(href)
            url      = self.getArtistURL(href)
            savename = self.dutils.getArtistSavename(artistID)
            name     = hrefData['Name']

            print(iArtist,'/',len(artistDB),'\t:',artistID,'\t',name,'\t',href)
            
            if isFile(savename):
                if force is False:
                    continue

            self.dutils.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.searchURL
        url = urllib.parse.urljoin(baseURL, "{0}{1}".format("artists?q=", quote(artist))) 
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
        
    def assertDBModValExtraData(self, modVal, maxPages=None, allowMulti=False, test=True):
        mulArts             = multiartist()        
        
        print("assertDBModValExtraData(",modVal,")")
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs   = 0
        ignores = self.artistIgnoreList()

        
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.more is True:
                npages = pages.tot
                if maxPages is not None:
                    npages = min([npages, maxPages])
                artistRef = artistData.url.url
                print(artistID,'\t',artistData.artist.name)
                if artistData.artist.name in ignores:
                    print("\tNot downloading artist in ignore list: {0}".format(artistData.artist.name))
                    continue
                    
                
                multiValues = mulArts.getArtistNames(artistData.artist.name)
                if len(multiValues) > 1:
                    if allowMulti is False:
                        print("\tNot downloading multis: {0}".format(multiValues.keys()))
                        continue
                
                if sum([x == artistData.artist.name for x in self.artistIgnoreList()]) > 0:
                    print("Hi {0}".format(artistData.artist.name))
                    continue
                    
                for p in range(2, npages+1):
                    url      = self.getArtistURL(artistRef, p)
                    savename = self.getArtistSavename(artistID, p)
                    print(artistID,'\t',url,'\t',savename)
                    print("\t---> {0} / {1}".format(p, npages))
                    if test is True:
                        print("\t\tWill download: {0}".format(url))
                        print("\t\tJust testing... Will not download anything.")
                        continue
                    if not isFile(savename):
                        self.downloadArtistURL(url=url, savename=savename, force=True)
                        sleep(3)