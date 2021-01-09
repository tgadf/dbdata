from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename
from fsUtils import isFile
from ioUtils import getFile, saveFile


#################################################################################################################################
#
# Primary
#
#################################################################################################################################
class dbArtistsPrimary(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
        
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
            
 
        
#################################################################################################################################
#
# Credit
#
#################################################################################################################################
class dbArtistsCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setCredit()
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
                
                
    
#################################################################################################################################
#
# Extra
#
#################################################################################################################################
class dbArtistsExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setExtra()
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, force=True)
        dbdata   = self.getDBData(modVal, force=False)
    
        newData = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
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
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
            
            

#################################################################################################################################
#
# Assert Credit (Find Credit For AllMusic)
#
#################################################################################################################################
class dbArtistsAssertCredit(dbArtistsBase):
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
    
    def downloadUnknownArtistCredits(self):
        for artistID,artistIDData in self.metadata.items():
            savename = self.dutils.getArtistSavename(artistID, credit=True)
            if isFile(savename):
                continue
            title  = artistIDData["title"]
            title  = title.replace("Artist Search for ", "")
            title  = title.replace(" | AllMusic", "")
            artist = title[1:-1]
            if len(artist) < 1:
                continue
            self.dbArtists.searchForArtistCredit(artist=artist, artistID=artistID)
            

            
            
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