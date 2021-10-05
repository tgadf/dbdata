from dbArtistsBase import dbArtistsBase
from fsUtils import isFile
from fileUtils import getBaseFilename
from timeUtils import timestat
from ioUtils import saveFile
from time import sleep
import urllib
from webUtils import getHTML

from dbArtistsLastFM import dbArtistsLastFM
from dbArtistsDiscogs import dbArtistsDiscogs
from dbArtistsMusicBrainz import dbArtistsMusicBrainz

#################################################################################################################################
# Assert Extra  (All DBs)
#################################################################################################################################
class dbArtistsAssertExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        print("dbArtistsAssertExtra({0})".format(self.db))
        
        if not isinstance(dbArtists, (dbArtistsDiscogs,dbArtistsMusicBrainz,dbArtistsLastFM)):
            raise ValueError("{0} DB is not allowed".format(type(dbArtists)))
        try:
            self.masterIgnoreData = self.getMasterIgnoreData()
            self.extraIgnores = self.masterIgnoreData[self.db]["Name"]
            print("  --> Found {0} AllMusic Song IDs To Ignore".format(len(self.extraIgnores)))
        except:
            self.extraIgnores = []
            #raise ValueError("Could not load AllMusic Credit Ignores data!")

        self.metadata = {}
                
    
    def getMetadata(self):
        return self.metadata
    
    def getNumPages(self, pages):
        if isinstance(self.dbArtists, dbArtistsLastFM):
            retval = pages.tot
        elif isinstance(self.dbArtists, (dbArtistsDiscogs,dbArtistsMusicBrainz)):
            retval = pages.pages
        else:
            raise ValueError("Unsure how to get number of pages for {0}".format(type(dbArtists)))
            
        return 1 if retval is None else retval
    
    def createExtraMetadata(self, modVal=None):
        modVals = [modVal] if modVal is not None else range(100)
            
        ts = timestat("Creating Extra Files Metadata")
        for modVal in modVals:            
            tsDBData = timestat("Finding Pages/URL Data For ModVal={0}".format(modVal))
            dbData = self.getDBData(modVal)
            dbArtistURLPages = {artistID: {"Name": artistData.artist.name, "URL": artistData.url.url, "Pages": self.getNumPages(artistData.pages)} for artistID,artistData in dbData.items()}
            tsDBData.stop()
            
            tsPages = timestat("Finding Artists With More Pages From {0} Artists For ModVal={1}".format(len(dbArtistURLPages), modVal))
            pagesData = {artistID: artistData for artistID,artistData in dbArtistURLPages.items() if artistData["Pages"] > 1}
            tsPages.stop()
            
            tsIgnore = timestat("Removing Ignored Artists From {0} Artists For ModVal={1}".format(len(pagesData), modVal))
            ignoreData = {artistID: artistData for artistID,artistData in pagesData.items() if artistData["Name"] not in self.extraIgnores}
            tsIgnore.stop()
            
            tsMeta = timestat("Saving Metadata From {0}/{1}/{2} For ModVal={3}".format(len(ignoreData), len(pagesData),len(dbArtistURLPages),modVal))
            self.metadata[modVal] = ignoreData
            tsMeta.stop()
        ts.stop()
        
    
    def downloadMissingArtistExtras(self, maxPages=None):
        ts = timestat("Downloading Missing Artist Extra Files")
        for modVal,modValData in self.metadata.items():
            tsMod = timestat("Downloading {0} Missing Artist Extra Files For ModVal={1}".format(len(modValData), modVal))
            N = len(modValData)
            for i,(artistID,artistPageData) in enumerate(modValData.items()):
                artistName = artistPageData["Name"]
                artistURL  = artistPageData["URL"]
                pages      = artistPageData["Pages"]
                print("="*100)
                print("{0}/{1}:  [{2}] / [{3}]".format(i,N,artistName,artistURL))
                for j,page in enumerate(range(pages)):
                    if maxPages is not None:
                        if j > maxPages:
                            continue
                    url      = self.dbArtists.getArtistURL(artistURL, page=page)
                    savename = self.dutils.getArtistSavename(artistID, page=page)
                    if isFile(savename):
                        continue

                    print("{0}/{1}:  [{2}] / [{3}] / [{4}-{5}]".format(i,N,artistName,artistURL,j,pages))
                    
                    try:
                        self.dutils.downloadArtistURL(url, savename)
                    except:
                        print("Error downloading {0}".format(url))
                        
            tsMod.stop()
        ts.stop()

        
#################################################################################################################################
# Extra
#################################################################################################################################
class dbArtistsExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setExtra()
        
    def parse(self, modVal, expr='< 0 Days', force=True, debug=False):
        ts = timestat("Parsing ModVal={0} Extra Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistExtraFiles(modVal, expr, force=force)
        tsFiles.stop()

        N = len(newFiles)
        modValue = 50 if N >= 100 else 10
        if N > 0:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata   = self.getDBData(modVal, force)
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Extra Files For ModVal={1}".format(N, modVal))
        
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
            artistID = getBaseFilename(ifile)
            if len(artistID.split("-")) != 2:
                print("Error with extra file: {0}".format(ifile))
                continue
                
            try:
                artistID = artistID.split("-")[0]
            except:
                print("Error with extra file: {0}".format(ifile))
                continue
                
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
            
        tsParse.stop()
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        return newData > 0