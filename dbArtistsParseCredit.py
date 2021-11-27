from dbArtistsBase import dbArtistsBase
from fsUtils import isFile

from fileUtils import getBaseFilename
from timeUtils import timestat
from time import sleep
import urllib
from webUtils import getHTML
        
        
#################################################################################################################################
# Assert Credit (Find Credit For AllMusic)
#################################################################################################################################
class dbArtistsAssertCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.dbCredit  = dbArtistsCredit(dbArtists)
        print("dbArtistsAssertCredit({0})".format(self.db))
        try:
            self.masterIgnoreData = self.getMasterIgnoreData()
            self.creditIgnores = self.masterIgnoreData["AllMusic"]["Credit"]
            print("  --> Found {0} AllMusic Credit IDs To Ignore".format(len(self.creditIgnores)))
        except:
            self.creditIgnores = []
            #raise ValueError("Could not load AllMusic Credit Ignores data!")
        self.metadata = {}
                
    
    def getMetadata(self):
        return self.metadata
    
    def createCreditMetadata(self, modVal=None):
        modVals = [modVal] if modVal is not None else range(100)
            
        ts = timestat("Creating AllMusic Credit Metadata")
        for modVal in modVals:
            tsFiles = timestat("Finding Primary Files For ModVal={0}".format(modVal))
            modValPrimaryFiles = self.getArtistPrimaryFiles(modVal, expr=None, force=True)
            tsFiles.stop()
            
            tsIgnore = timestat("Removing IDs To Ignore From {0} Primary Files For ModVal={0}".format(len(modValPrimaryFiles), modVal))
            modValPrimaryGoodFiles = [ifile for ifile in modValPrimaryFiles if getBaseFilename(ifile) not in self.creditIgnores]
            tsIgnore.stop()
            
            tsDBData = timestat("Finding Known Artists From {0} Primary/Good Files For ModVal={1}".format(len(modValPrimaryGoodFiles), modVal))
            dbData = self.disc.getDBModValData(modVal)
            missingArtistIDFiles = [ifile for ifile in modValPrimaryFiles if dbData.get(getBaseFilename(ifile)) is None]
            tsDBData.stop()
            
            tsCredit = timestat("Finding Known Credit Artists From {0} Unknown Artists For ModVal={1}".format(len(missingArtistIDFiles), modVal))
            creditFiles = {getBaseFilename(ifile): ifile for ifile in self.dbCredit.getArtistCreditFiles(modVal, expr=None, force=True)}
            missingCreditIDs = [ifile for ifile in missingArtistIDFiles if creditFiles.get(getBaseFilename(ifile)) is None]
            tsCredit.stop()
            
            tsMeta = timestat("Finding Metadata For {0}/{1}/{2}/{3} Missing ArtistIDs for ModVal={4}".format(len(missingCreditIDs), len(missingArtistIDFiles), len(modValPrimaryGoodFiles), len(modValPrimaryFiles), modVal))
            metaData = {getBaseFilename(ifile): self.artist.getData(ifile).meta for ifile in missingCreditIDs}
            self.metadata[modVal] = {artistID: {"title": meta.title, "url": meta.url} for artistID,meta in metaData.items()}
            tsMeta.stop()
        ts.stop()
                
    
    def downloadUnknownArtistCredits(self):
        newIgnores = []
        for modVal,modValMetadata in self.metadata.items():
            N = len(modValMetadata)
            ts = timestat("Downloading {0} Unknown Credit Files For ModVal={1}".format(N, modVal))
            for i,(artistID,artistIDData) in enumerate(modValMetadata.items()):
                savename = self.dutils.getArtistSavename(artistID, credit=True)
                if isFile(savename):
                    continue
                title  = artistIDData["title"]
                title  = title.replace("Artist Search for ", "")
                title  = title.replace(" | AllMusic", "")
                title  = title.replace("Songs, Albums, Reviews, Bio & More", "").strip()
                title  = title[1:] if title.startswith('"') else title
                title  = title[:-1] if title.endswith('"') else title
                artist = title
                print("{0}/{1}:  [{2}]".format(i,N,artist))
                if len(artist) < 1:
                    continue
                numDownload = self.dbArtists.searchForArtistCredit(artist=artist, artistID=artistID)
                if numDownload == 0:
                    newIgnores.append(artistID)
            ts.stop()
            
        print("New IDs To Ignore")
        print(newIgnores)
        tsUpdate = timestat("Adding {0} ArtistIDs To Master Credit Ignore List".format(len(newIgnores)))
        self.updateMasterIgnoreCreditData(newIgnores)
        tsUpdate.stop()
 
        
#################################################################################################################################
# Credit
#################################################################################################################################
class dbArtistsCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setCredit()
        self.dbArtists = dbArtists
        
    def parse(self, modVal, expr, force=False, debug=False):
        ts = timestat("Parsing ModVal={0} Credit Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistCreditFiles(modVal, expr, force)
        tsFiles.stop()

        N = len(newFiles)
        modValue = 500 if N >= 1000 else 100
        if N > 0:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata   = self.getDBData(modVal, force)
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Credit Files For ModVal={1}".format(N, modVal))
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
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        tsParse.stop()