from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename
from fsUtils import isFile, setFile, setDir
from ioUtils import getFile, saveFile
from timeUtils import timestat
from sys import prefix
import urllib
from time import sleep
from webUtils import getHTML

#################################################################################################################################
# Primary
#################################################################################################################################
class dbArtistsPrimary(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
    def parse(self, modVal, expr, force=False, debug=False):
        ts = timestat("Parsing ModVal={0} Primary Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistPrimaryFiles(modVal, expr, force)
        tsFiles.stop()

        N = len(newFiles)
        modValue = 250 if N >= 1000 else 50
        if N > 0:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata   = self.getDBData(modVal, force)
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Files For ModVal={1}".format(N, modVal))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
                
            artistID = getBaseFilename(ifile)
            info     = self.artist.getData(ifile)
            if debug:
                print("\t",ifile,' ==> ',info.ID.ID,' <-> ',artistID)
            if info.ID.ID != artistID:
                if debug is True:
                    print("Error for {0}  ID={1}  FileID={2}".format(info.meta.title,info.ID.ID,artistID))
                    1/0
                continue
            dbdata[artistID] = info
            newData += 1
        tsParse.stop()
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
        
        ts.stop()
        
        return newData > 0


#################################################################################################################################
# Parse From Raw HTML
#################################################################################################################################
class dbArtistsRawHTML(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
            
    def parse(self, expr, force=False, debug=False):
        ts = timestat("Parsing Raw HTML Files")
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistRawHTMLFiles(expr, force)
        tsFiles.stop()
        if debug:
            print("Parsing {0} Raw HTML Files From Expr[{1}]".format(len(newFiles), expr))

        N = len(newFiles)
        modValue = 250 if N >= 500 else 50
        tsParse = timestat("Parsing {0} Raw HTML Files".format(N))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N or debug:
                print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
            
            if debug:
                print("{0}/{1}\tParsing {2}".format(i,N,ifile))
            htmldata = getFile(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            if debug:
                print("  ---> ID={0}".format(artistID))
            savename = self.dutils.getArtistSavename(artistID)
            saveFile(idata=htmldata, ifile=savename, debug=False)        
        
        tsParse.stop()
        ts.stop()
        
        
#################################################################################################################################
# Parse From Raw Files
#################################################################################################################################
class dbArtistsRawFiles(dbArtistsBase):
    def __init__(self, dbArtists, datatype):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.datatype  = datatype
        self.dbArtists = dbArtists
        
    def parse(self, expr, force=False, debug=False):
        ts = timestat("Parsing ModVal={0} Credit Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistRawFiles(datatype=self.datatype, expr=expr, force=force)
        tsFiles.stop()
            
        N = len(newFiles)
        tsParse = timestat("Parsing {0} New Raw Files".format(N))
        
        newData = 0
        modValue = 250 if N >= 500 else 50
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
            htmldata = getFile(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            if artistID is None:
                continue
            savename = self.dutils.getArtistSavename(artistID)
            if savename is None:
                continue
            saveFile(idata=htmldata, ifile=savename, debug=False)
            newData += 1
            
        print("Created {0}/{1} New Artist Files".format(newData, N))
        tsParse.stop()



#################################################################################################################################
# Assert Song (Find Song For AllMusic)
#################################################################################################################################
class dbArtistsAssertSong(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        #self.dbSong = dbArtistsSong(dbArtists)
        print("dbArtistsAssertSong({0})".format(self.db))
        try:
            self.masterIgnoreData = self.getMasterIgnoreData()
            self.songIgnores = self.masterIgnoreData["AllMusic"]["Song"]
            print("  --> Found {0} AllMusic Song IDs To Ignore".format(len(self.songIgnores)))
        except:
            self.songIgnores = []
            #raise ValueError("Could not load AllMusic Credit Ignores data!")
        self.metadata = {}
                
    
    def getMetadata(self):
        return self.metadata
    
    def createSongMetadata(self, modVal=None):
        modVals = [modVal] if modVal is not None else range(100)
            
        ts = timestat("Creating AllMusic Song Metadata")
        for modVal in modVals:
            
            tsDBData = timestat("Finding Known Credit Artists For ModVal={0}".format(modVal))
            dbData = self.getDBData(modVal)
            dbArtistURLs    = {artistID: {"Name": artistData.artist.name, "URL": artistData.url.url} for artistID,artistData in dbData.items()}
            tsDBData.stop()            

            tsCredit = timestat("Finding Known Credit Artists From {0} Artists For ModVal={1}".format(len(dbArtistURLs), modVal))
            creditArtistIDs = {artistID: artistData for artistID,artistData in dbArtistURLs.items() if artistData["URL"] is not None and artistData["URL"].endswith("/credits")}
            tsCredit.stop()
            
            tsIgnore = timestat("Removing IDs To Ignore From {0} Primary Files For ModVal={0}".format(len(creditArtistIDs), modVal))
            availableArtistIDs = {artistID: artistData for artistID,artistData in creditArtistIDs.items() if artistID not in self.songIgnores}
            tsIgnore.stop()
            
            tsMeta = timestat("Finding Metadata For {0}/{1}/{2} Missing ArtistIDs for ModVal={3}".format(len(availableArtistIDs), len(creditArtistIDs), len(dbArtistURLs), modVal))
            self.metadata[modVal] = availableArtistIDs
            tsMeta.stop()
        ts.stop()

    
    def downloadUnknownArtistSongs(self):
        newIgnores = []
        for modVal,modValMetadata in self.metadata.items():
            N = len(modValMetadata)
            ts = timestat("Downloading {0} Unknown Song Files For ModVal={1}".format(N, modVal))
            for i,(artistID,artistIDData) in enumerate(modValMetadata.items()):
                savename = self.dutils.getArtistSavename(artistID, song=True)
                
                href   = artistIDData["URL"]
                artist = artistIDData["Name"]
                if isFile(savename):
                    continue

                ## Replace /credits with /songs
                href = "/".join(href.split('/')[:-1] + ["songs", "all"])
                    
                ## Create Full URL
                url = urllib.parse.urljoin(self.dbArtists.baseURL, href)
                print("\n")
                print("="*100)
                print("{0}/{1}:  [{2}] / [{3}]".format(i,N,artist,url))
                

                data, response = self.dutils.downloadURL(url)
                if response == 200:
                    bsdata = getHTML(data)
                    if len(bsdata.findAll("th", {"class": "title-composer"})) > 0:
                        print("  ---> Saving Data To {0}".format(savename))
                        saveFile(idata=data, ifile=savename)
                        sleep(3)
                        continue
                
                sleep(3)
                newIgnores.append(artistID)
                        
                
                if i == 20:
                    break
            ts.stop()
            
        print("New IDs To Ignore")
        print(newIgnores)
        tsUpdate = timestat("Adding {0} ArtistIDs To Master Song Ignore List".format(len(newIgnores)))
        self.updateMasterIgnoreSongData(newIgnores)
        tsUpdate.stop()    
    
    
#################################################################################################################################
#
# Unofficial
#
#################################################################################################################################
class dbArtistsUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setUnofficial()
        self.dbArtists = dbArtists
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force=True)
        dbdata   = self.getDBData(modVal, force=False)
    
        newData = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            info     = self.artist.getData(ifile)
            
            currentKeys = []
            if dbdata.get(artistID) is not None:
                currentKeys = list(dbdata[artistID].media.media.keys())
            else:
                dbdata[artistID] = info
                newData += 1
                continue
            
            keys = list(set(list(info.media.media.keys()) + currentKeys))
            for k in keys:
                v = info.media.media.get(k)
                if v is None:
                    continue
                iVal  = {v2.code: v2 for v2 in v}
                dVal  = dbdata[artistID].media.media.get(k)
                if dVal is None:
                    Tretval = iVal
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        return newData > 0

        
#################################################################################################################################
#
# Assert Compositions (Find Compositions For AllMusic)
#
#################################################################################################################################
class dbArtistsAssertComposition(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        self.ignores={}
    
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        savename = self.disc.getArtistsDBModValMetadataFilename(modVal)
        print(savename)
        1/0

        newFiles = self.getArtistFiles(modVal, force=True)
        force    = False
        dbdata   = self.getDBData(modVal, force=force)

        newData  = 0
        for j,ifile in enumerate(newFiles):
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            if isKnown is None:
                info     = self.artist.getData(ifile)
                meta     = info.meta
                self.metadata[artistID] = {"title": meta.title, "url": meta.url}
                
    def getResults(self):
        return self.metadata
    
    def downloadUnknownArtistCompositions(self):
        for artistID,artistIDData in self.metadata.items():
            if artistID in self.ignores.keys():
                print("Ignoring {0} artistID".format(artistID))
                continue
            savename = self.dutils.getArtistSavename(artistID, composition=True)
            if isFile(savename):
                continue
            title  = artistIDData["title"]
            title  = title.replace("Artist Search for ", "")
            title  = title.replace(" | AllMusic", "")
            artist = title[1:-1]
            if len(artist) < 1:
                continue
            self.dbArtists.searchForArtistComposition(artist=artist, artistID=artistID)
            1/0
        

            

            
            
#################################################################################################################################
#
# Assert Extra (Find Credit For AllMusic)
#
#################################################################################################################################
class dbArtistsAssertExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        dbdata   = self.getDBData(modVal, force=False)
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.pages is None:
                continue
            if pages.pages == 1:
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useURL=True):
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useName=True):
                continue
            self.metadata[artistID] = {"Name": artistData.artist.name, "URL": artistData.url.url, "Pages": list(range(2,pages.pages+1))}
                
    def getResults(self):
        return self.metadata
    
    def downloadMissingArtistExtras(self, force=False):
        print("Found {0} artists to get".format(len(self.metadata)))
        for artistID,artistPageData in self.metadata.items():
            artistName = artistPageData["Name"]
            artistURL  = artistPageData["URL"]
            pages      = artistPageData["Pages"]
            for page in pages:
                url      = self.dbArtists.getArtistURL(artistURL, page=page)
                savename = self.dutils.getArtistSavename(artistID, page=page)
                if isFile(savename) and force is False:
                    continue
                #vals = {artistURL: artistName}
                #import json
                try:
                    self.dutils.downloadArtistURL(url, savename)
                except:
                    print("Error downloading {0}".format(url))
            

            
            
#################################################################################################################################
#
# Assert Unofficial (Find Credit For Discogs)
#
#################################################################################################################################
class dbArtistsAssertUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        dbdata   = self.getDBData(modVal, force=False)
        for artistID,artistData in dbdata.items():
            mediaCounts = artistData.mediaCounts
            if mediaCounts.counts.get("Unofficial") is None:
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useURL=True):
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useName=True):
                continue
            self.metadata[artistID] = {"Name": artistData.artist.name, "URL": artistData.url.url}
                
    def getResults(self):
        return self.metadata
    
    def downloadMissingArtistUnofficials(self, force=False):
        print("Found {0} artists to get".format(len(self.metadata)))
        for artistID,artistPageData in self.metadata.items():
            artistName = artistPageData["Name"]
            artistURL  = artistPageData["URL"]
            url        = self.dbArtists.getArtistURL(artistURL, unofficial=True)
            savename   = self.dutils.getArtistSavename(artistID, unofficial=True)
            if isFile(savename) and force is False:
                continue
            try:
                self.dutils.downloadArtistURL(url, savename)
            except:
                print("Error downloading {0}".format(url))