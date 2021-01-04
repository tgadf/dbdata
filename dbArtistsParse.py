from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename

class dbArtistsPrimary(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force)
        dbdata   = self.getDBData(modVal, force)

        newData  = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            info     = self.artist.getData(ifile)            
            if info.ID.ID != artistID:
                if self.debug is True:
                    print("Error for {0}".format(info.meta.title))
                continue
            dbdata[artistID] = info
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
 
        
class dbArtistsCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setCredit()
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force)
        dbdata   = self.getDBData(modVal, force)
    
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
                    saveIt += len(iVal)
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
                
                
    
        
class dbArtistsExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setExtra()
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force)
        dbdata   = self.getDBData(modVal, force)
    
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
                    saveIt += len(iVal)
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
            
            

class dbArtistsAssertCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        
        self.metadata = {}
        
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
        
    def parseModVal(self, modVal):
        newFiles = self.getArtistFiles(modVal, force=True)
        force    = False
        dbdata   = self.getDBData(modVal, force=force)

        newData  = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            if isKnown is None:
                info     = self.artist.getData(ifile)
                meta     = info.meta
                self.metadata[meta.title] = meta.url        
                
                
    def getResults(self):
        return self.metadata