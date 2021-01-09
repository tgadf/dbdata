from fsUtils import setDir, isFile, setSubFile
from fileUtils import getBaseFilename
from ioUtils import getFile, saveFile
from searchUtils import findExt
from datetime import datetime, timedelta
from time import sleep, mktime, gmtime
from os import path

class dbArtistsBase:
    def __init__(self, dbArtists, basedir=None, debug=False):
        self.previousDays = 5
        self.force        = False
        
        #######################
        ## File Type
        #######################
        self.primary      = True
        self.credit       = False
        self.extra        = False
        self.unofficial   = False
            
        #######################
        ## General Imports
        #######################
        self.db        = dbArtists.db
        self.disc      = dbArtists.disc
        self.artist    = dbArtists.artist
        self.dutils    = dbArtists.dutils
        self.sleeptime = 2
        self.debug     = debug
        
        self.getArtistsDir       = self.disc.getArtistsDir
        self.getArtistsDBDir     = self.disc.getArtistsDBDir
        self.getDiscogDBDir      = self.disc.getDiscogDBDir
        
        
    def setCredit(self):
        self.credit     = True
        self.primary    = False
        self.extra      = False
        self.unofficial = False
    def setPrimary(self):
        self.credit     = False
        self.primary    = True
        self.extra      = False
        self.unofficial = False
    def setExtra(self):
        self.credit     = False
        self.primary    = False
        self.extra      = True
        self.unofficial = False
    def setUnofficial(self):
        self.credit     = False
        self.primary    = False
        self.extra      = False
        self.unofficial = True
        
        
        
        
    ##################################################################################################################
    # I/O DB Data
    ##################################################################################################################
    def getArtistNumAlbums(self, artistData):
        numAlbums = sum([len(x) for x in artistData.media.media.values()])
        return numAlbums
    
    def saveDBData(self, modVal, dbdata, newData=None):
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        if newData is not None:
            print("Saving {0} new artist IDs to {1}".format(newData, dbname))
            print("Saving {0} total artist IDs to {1}".format(len(dbdata), dbname))
        else:
            print("Saving {0} total artist IDs to {1}".format(len(dbdata), dbname))
        dbNumAlbums = sum([self.getArtistNumAlbums(artistData) for artistData in dbdata.values()])
        print("Saving {0} total artist media".format(dbNumAlbums))
        saveFile(idata=dbdata, ifile=dbname)
        
        
    def getDBData(self, modVal, force=False):
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        if self.credit is True or self.extra is True:
            force=False
        if force is False:
            dbdata = getFile(dbname, version=3)
            print("  ===> Found {0} previous data for ModVal={1}".format(len(dbdata), modVal))
        else:
            print("  ===> Forcing Reloads of ModVal={0}".format(modVal))
            dbdata = {}
        return dbdata
    
        
        
        
    ##################################################################################################################
    # Files For Parsing
    ##################################################################################################################
    def getModValDir(self, modVal):
        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
        artistDBDir = self.disc.getArtistsDBDir()                
        dirVal = setDir(artistDir, str(modVal))
        if self.credit is True:
            dirVal = setDir(dirVal, "credit")
        elif self.extra is True:
            dirVal = setDir(dirVal, "extra")
        elif self.unofficial is True:
            dirVal = setDir(dirVal, "unofficial")
        return dirVal
    
    
    def getAllFiles(self, dirVal):
        files  = findExt(dirVal, ext='.p')
        return files
        
        
    def getArtistFiles(self, modVal, previousDays=None, force=False):
        if previousDays is None:
            previousDays = self.previousDays
            
        dirVal = self.getModValDir(modVal)
        files  = self.getAllFiles(dirVal)
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        
        now    = datetime.now()
        if isFile(dbname):
            lastModified = datetime.fromtimestamp(path.getmtime(dbname))
            if force is True:
                lastModified = None
        else:
            lastModified = None

        newFiles = None
        if lastModified is None:
            newFiles = files
            print("  ===> Parsing all {0} files for modval {1}".format(len(newFiles), modVal))
        else:
            numNew    = [ifile for ifile in files if (now-datetime.fromtimestamp(path.getmtime(ifile))).days < previousDays]
            numRecent = [ifile for ifile in files if datetime.fromtimestamp(path.getmtime(ifile)) > lastModified]
            newFiles  = list(set(numNew).union(set(numRecent)))
            print("  ===> Found new {0} files (< {1} days) to parse for modval {2}".format(len(newFiles), previousDays, modVal))
        return newFiles
    
    


    
    ##################################################################################################################
    # Collect Metadata About Artists
    ##################################################################################################################
    def createArtistMetadata(self, modVal):
        dbdata = self.getDBData(modVal)
    
        artistIDMetadata = {k: [v.artist.name, v.url.url] for k,v in dbdata.items()}
        for artistID,artistData in dbdata.items():
            if artistData.profile.variations is not None:
                artistIDMetadata[artistID].append([v2.name for v2 in artistData.profile.variations])
            else:
                artistIDMetadata[artistID].append([artistData.artist.name])        
        
        savename = self.disc.getArtistsDBModValMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        saveFile(idata=artistIDMetadata, ifile=savename, debug=False)
        
        
    def createAlbumMetadata(self, modVal):
        dbdata = self.getDBData(modVal)
        
        artistIDMetadata = {}
        for artistID,artistData in dbdata.items():
            artistIDMetadata[artistID] = {}
            for mediaName,mediaData in artistData.media.media.items():
                albumURLs  = {mediaValues.code: mediaValues.url for mediaValues in mediaData}
                albumNames = {mediaValues.code: mediaValues.album for mediaValues in mediaData}
                artistIDMetadata[artistID][mediaName] = [albumNames, albumURLs]      
        
        savename = self.disc.getArtistsDBModValAlbumsMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        saveFile(idata=artistIDMetadata, ifile=savename, debug=False)