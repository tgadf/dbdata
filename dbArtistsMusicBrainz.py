from artistMusicBrainz import artistMusicBrainz
from dbUtils import utilsMusicBrainz
from dbBase import dbBase
import urllib
from urllib.parse import quote
from webUtils import getHTML
from fsUtils import isFile, setFile, removeFile
from ioUtils import getFile, saveFile
from time import sleep



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
    def parseSearchArtist(self, artist, data, maxArtists=99, force=False, debug=False):
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
            if iArtist > maxArtists:
                break

            discID   = self.dutils.getArtistID(href)
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
        
        
    def assertDBModValExtraData(self, modVal, minPages=1, maxPages=None, allowMulti=False, test=True, clean=True):
        print("assertDBModValExtraData(",modVal,")")
        artistDBDir = self.disc.getArtistsDBDir()
        dbname  = setFile(artistDBDir, "{0}-DB.p".format(modVal))     
        dbdata  = getFile(dbname)
        nerrs   = 0
        #ignores = self.artistIgnoreList()

        
        for artistID,artistData in dbdata.items():
            first = True
            pages = artistData.pages
            if pages.more is True:
                npages = pages.pages
                if npages < minPages:
                    continue
                if maxPages is not None:
                    npages = min([npages, maxPages])
                artistRef = artistData.url.url
                #if artistData.artist.name in ignores:
                #    print("\tNot downloading artist in ignore list: {0}".format(artistData.artist.name))
                #    continue
                    
                #savename = self.dutils.getArtistSavename(artistID)
                #removeFile(savename)
                #print("\t---> {0} / {1}   {2}".format(1, pages.pages, savename))

                #print(artistID,'\t',npages,'\t')
                #continue
                    
                    
                for p in range(1, npages+1):
                    if p == 1:
                        url      = self.getArtistURL(artistRef)
                        savename = self.dutils.getArtistSavename(artistID)
                    else:
                        url      = self.getArtistURL(artistRef, p)
                        savename = self.dutils.getArtistSavename(artistID, p)
                    print("\t---> {0} / {1}   {2}".format(p, pages.pages, url))
                    
                    if clean is True:
                        if isFile(savename):
                            print("Removing {0}".format(savename))
                            removeFile(savename)
                        
                    if test is True:
                        print("\t\tWill download: {0}".format(url))
                        print("\t\tJust testing... Will not download anything.")
                        continue
                        
                    if not isFile(savename):
                        if first:
                            print("{0: <20}{1: <10}{2}".format(artistID,pages.tot,artistData.artist.name))
                            first = False

                        print("{0: <20}{1: <10}{2}".format(artistID, "{0}/{1}".format(p,pages.pages), url))
                        self.dutils.downloadArtistURL(url=url, savename=savename, force=True)
                        sleep(3)