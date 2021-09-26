from dbArtistsBase import dbArtistsBase
from fsUtils import isFile
from fileUtils import getBaseFilename
from timeUtils import timestat
from ioUtils import saveFile
from time import sleep
import urllib
from webUtils import getHTML

#################################################################################################################################
# Assert Unofficial (Find Unofficial For Discogs)
#################################################################################################################################
class dbArtistsAssertUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.dbUnofficial = dbArtistsUnofficial(dbArtists)
        self.metadata = {}
        print("dbArtistsAssertUnofficial({0})".format(self.db))
        try:
            self.masterIgnoreData = self.getMasterIgnoreData()
            self.unofficialIgnores = self.masterIgnoreData[self.db]["Name"]
            print("  --> Found {0} {1} Artist IDs To Ignore".format(len(self.unofficialIgnores), self.db))
        except:
            self.unofficialIgnores = []

        self.metadata = {}
                
    
    def getMetadata(self):
        return self.metadata
    
    def createUnofficialMetadata(self, modVal=None):
        modVals = [modVal] if modVal is not None else range(100)
            
        ts = timestat("Creating Unofficial Files Metadata")
        for modVal in modVals:
            tsDBData = timestat("Finding Pages/URL/MediaCounts Data For ModVal={0}".format(modVal))
            dbData = self.getDBData(modVal)
            dbArtistURLMedia = {artistID: {"Name": artistData.artist.name,
                                           "URL": artistData.url.url,
                                           "MediaCounts": artistData.mediaCounts.counts.get('Unofficial')} for artistID,artistData in dbData.items()}
            tsDBData.stop()
            
            tsMedia = timestat("Finding Artists With Unofficial MediaCounts From {0} Artists For ModVal={1}".format(len(dbArtistURLMedia), modVal))
            unofficialData = {artistID: artistData for artistID,artistData in dbArtistURLMedia.items() if artistData["MediaCounts"] is not None}
            tsMedia.stop()
            
            tsIgnore = timestat("Removing Ignored Artists From {0} Artists For ModVal={1}".format(len(unofficialData), modVal))
            ignoreData = {artistID: artistData for artistID,artistData in unofficialData.items() if artistData["Name"] not in self.unofficialIgnores}
            tsIgnore.stop()
            
            tsUnofficial = timestat("Finding Known Unofficial Artists From {0} Unofficial Artists For ModVal={1}".format(len(ignoreData), modVal))
            unofficialFiles = {getBaseFilename(ifile): ifile for ifile in self.dbUnofficial.getArtistUnofficialFiles(modVal, expr=None, force=True)}
            missingUnofficialIDs = {artistID: artistData for artistID,artistData in ignoreData.items() if unofficialFiles.get(artistID) is None}
            #return ignoreData, unofficialFiles, missingUnofficialIDs, unofficialData, dbArtistURLMedia
            tsUnofficial.stop()
            
            tsMeta = timestat("Saving Metadata From {0}/{1}/{2}/{3} Artists For ModVal={4}".format(len(missingUnofficialIDs), len(ignoreData), len(unofficialData),len(dbArtistURLMedia),modVal))
            self.metadata[modVal] = missingUnofficialIDs
            tsMeta.stop()
        ts.stop()
        
    
    def downloadMissingArtistUnofficial(self):
        ts = timestat("Downloading Missing Artist Unofficial Files")
        for modVal,modValData in self.metadata.items():
            tsMod = timestat("Downloading {0} Missing Artist Unofficial Files For ModVal={1}".format(len(modValData), modVal))
            N = len(modValData)
            for i,(artistID,artistPageData) in enumerate(modValData.items()):
                artistName = artistPageData["Name"]
                artistURL  = artistPageData["URL"]
                
                print("="*100)
                print("{0}/{1}:  [{2}] / [{3}]".format(i,N,artistName,artistURL))
                url        = self.dbArtists.getArtistURL(artistURL, unofficial=True)
                savename   = self.dutils.getArtistSavename(artistID, unofficial=True)
                
                if isFile(savename):
                    continue

                try:
                    self.dutils.downloadArtistURL(url, savename)
                except:
                    print("Error downloading {0}".format(url))
                        
            tsMod.stop()
        ts.stop()
        
        
        
#################################################################################################################################
# Unofficial
#################################################################################################################################
class dbArtistsUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setUnofficial()
        self.dbArtists = dbArtists
        
    def parse(self, modVal, expr, force=False, debug=False):
        ts = timestat("Parsing ModVal={0} Unofficial Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistUnofficialFiles(modVal, expr, force)
        tsFiles.stop()

        N = len(newFiles)
        modValue = 50 if N >= 100 else 10
        if N > 0:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata   = self.getDBData(modVal, force)
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Unofficial Files For ModVal={1}".format(N, modVal))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
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
            
        tsParse.stop()
        
        print("Found {0} Unofficial Artist Records For ModVal={1}".format(newData, modVal))
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)