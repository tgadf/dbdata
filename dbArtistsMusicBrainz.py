from artistMusicBrainz import artistMusicBrainz
from dbUtils import utilsMusicBrainz
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile


##################################################################################################################
# Base Class
##################################################################################################################
class dbArtistsMusicBrainz:
    def __init__(self, debug=False):
        self.db     = "MusicBrainz"
        self.disc   = dbBase(self.db.lower())
        self.artist = artistMusicBrainz(self.disc)
        self.dutils = utilsMusicBrainz(self.disc)
        self.debug  = debug
        
        self.baseURL   = "https://musicbrainz.org/"
        self.searchURL = "https://musicbrainz.org/search?"

        self.ignores = {}
        self.ignores['/artist/51118c9d-965d-4f9f-89a1-0091837ccf54'] = '[nature sounds]'
        self.ignores['/artist/89ad4ac3-39f7-470e-963a-56509c546377'] = 'Various Artists'
        

    
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
    def getArtistURL(self, artistRef, page=1):
        baseURL = self.baseURL
        url     = urllib.parse.urljoin(baseURL, artistRef)
        if isinstance(page, int) and page > 1:
            pageURL = "?page={0}".format(page)
            url = "{0}{1}".format(url, pageURL)

        return url

        
    
    ##################################################################################################################
    #
    # Search Functions
    #
    ##################################################################################################################
    def parseSearchArtist(self, artist, data, force=False):
        if data is None:
            return None
        
        ## Parse data
        bsdata = getHTML(data)
        
        artistDB  = {}

        tables = bsdata.findAll("table")
        for table in tables:
            ths = table.findAll("th")
            headers = [x.text for x in ths]
            trs = table.findAll("tr")
            for tr in trs[1:]:
                tds    = tr.findAll("td")
                name   = tds[0].find('a').text
                href   = tds[0].find('a').attrs['href']
            
                if artistDB.get(href) is None:
                    artistDB[href] = {"N": 0, "Name": name}
                artistDB[href]["N"] += 1
        
    
        if self.debug:
            print("Found {0} artists".format(len(artistDB)))
                
        iArtist = 0
        iDown   = 0
        for href, hrefData in artistDB.items():
            if iDown > 20:
                break
            iArtist += 1

            discID   = self.dutils.getArtistID(href)
            
            uuid = href.split('/')[-1]

            m = md5()
            for val in uuid.split("-"):
                m.update(val.encode('utf-8'))
            hashval = m.hexdigest()
            discID  = str(int(hashval, 16))

            url      = self.getArtistURL(href)
            savename = self.dutils.getArtistSavename(discID)

            print(iArtist,'/',len(artistDB),'\t:',discID,'\t',url)
            
            if isFile(savename):
                if force is False:
                    continue

            iDown += 1
            self.dutils.downloadArtistURL(url, savename, force=force)
            
    
    def getSearchArtistURL(self, artist):
        baseURL = self.baseURL
        extra = "search?query={0}&type=artist&limit=100&method=indexed".format(quote(artist))
        url = urllib.parse.urljoin(baseURL, extra)         
        return url
    
        
    def searchForArtist(self, artist, force=False):
        print("\n\n===================== Searching For {0} =====================".format(artist))
        url = self.getSearchArtistURL(artist)
        if url is None:
            raise ValueError("URL is None!")
                    
        ## Download data
        data, response = self.downloadURL(url)
        if response != 200:
            print("Error downloading {0}".format(url))
            return False

        self.parseSearchArtist(artist, data, force)