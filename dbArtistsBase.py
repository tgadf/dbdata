from fsUtils import setDir, isFile, setSubFile, setFile
from fileUtils import getBaseFilename
from timeUtils import timestat
from ioUtils import getFile, saveFile
from searchUtils import findExt
from sys import prefix
from datetime import datetime, timedelta
from time import sleep, mktime, gmtime
from os import path
from pandas import Series

from searchUtils import filesFromDir
from recentFilesUtils import recentFiles

class dbArtistsBase:
    def __init__(self, dbArtists, basedir=None, debug=False):
        self.previousDays  = None
        self.previousHours = None
        self.force         = False
        
        #######################
        ## File Type
        #######################
        self.primary      = True
        self.credit       = False
        self.song         = False
        self.composition  = False
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
        self.credit      = True
        self.primary     = False
        self.extra       = False
        self.unofficial  = False
        self.song        = False
        self.composition = False
    def setPrimary(self):
        self.credit      = False
        self.primary     = True
        self.extra       = False
        self.unofficial  = False
        self.song        = False
        self.composition = False
    def setExtra(self):
        self.credit      = False
        self.primary     = False
        self.extra       = True
        self.unofficial  = False
        self.song        = False
        self.composition = False
    def setUnofficial(self):
        self.credit      = False
        self.primary     = False
        self.extra       = False
        self.unofficial  = True
        self.song        = False
        self.composition = False
    def setSong(self):
        self.credit      = False
        self.primary     = False
        self.extra       = False
        self.unofficial  = False
        self.song        = True
        self.composition = False
    def setComposition(self):
        self.credit      = False
        self.primary     = False
        self.extra       = False
        self.unofficial  = False
        self.song        = False
        self.composition = True
        
        
        
        
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
        dbdata = Series(dbdata) if isinstance(dbdata, dict) else dbdata:
            
        saveFile(idata=dbdata, ifile=dbname)
        
        
    def getDBData(self, modVal, force=False, debug=False):
        dbname = self.disc.getArtistsDBModValFilename(modVal)
        dbdata = {}
        localForce = False
        if self.credit is True or self.extra is True or self.song is True or self.composition is True:
            localForce=False
        else:
            localForce=force

        if isFile(dbname) is False:
            localForce = True

        if localForce is False:
            if debug:
                print("Loading {0}".format(dbname))
            dbdata = getFile(dbname, version=3)
            if isinstance(dbdata,Series):
                dbdata = dbdata.to_dict()
            if debug:
                print("  ===> Found {0} previous data for ModVal={1}".format(len(dbdata), modVal))
        else:            
            print("  ===> Forcing Reloads of ModVal={0}".format(modVal))
        
        return dbdata
    
    
    ##################################################################################################################
    # I/O DB Data
    ##################################################################################################################
    def getMasterIgnoreFilename(self):
        return setFile(setDir(prefix, 'dbdata'), 'dbIgnoreData.yaml')
    
    def getMasterIgnoreData(self):
        ignoreData = getFile(self.getMasterIgnoreFilename())
        return ignoreData
        
    def updateMasterIgnoreData(self, db, category, artistIDs):
        masterIgnoreData = self.getMasterIgnoreData()
        if masterIgnoreData.get(db) is None:
            masterIgnoreData[db] = {}
        if masterIgnoreData[db].get(category) is None:
            masterIgnoreData[db][category] = []
        print("Found {0} {1} Ignores".format(len(masterIgnoreData[db][category]), category))
        masterIgnoreData[db][category] += artistIDs
        print("Adding {0} {1} Ignores".format(len(artistIDs), category))
        masterIgnoreData[db][category] = list(set(masterIgnoreData[db][category]))
        print("Now Have {0} {1} Ignores".format(len(masterIgnoreData[db][category]), category))
        self.saveMasterIgnoreData(masterIgnoreData)
        
    def updateMasterIgnoreCreditData(self, artistIDs):
        self.updateMasterIgnoreData("AllMusic", "Credit", artistIDs)
              
    def updateMasterIgnoreSongData(self, artistIDs):
        self.updateMasterIgnoreData("AllMusic", "Song", artistIDs)
              
    def updateMasterIgnoreNameData(self, db, artistNames):
        self.updateMasterIgnoreData(db, "Name", artistNames)
        
    def saveMasterIgnoreData(self, masterIgnoreData):
        saveFile(idata=masterIgnoreData, ifile=self.getMasterIgnoreFilename())
        
        
        
    ##################################################################################################################
    # File I/O And Directories For Parsing
    ##################################################################################################################
    def getModValDir(self, modVal):
        artistDir = self.disc.getArtistsDir()
        maxModVal = self.disc.getMaxModVal()
        artistDBDir = self.disc.getArtistsDBDir()                
        dirVal = setDir(artistDir, str(modVal))
        if self.credit is True:
            dirVal = setDir(dirVal, "credit")
        elif self.song is True:
            dirVal = setDir(dirVal, "song")
        elif self.composition is True:
            dirVal = setDir(dirVal, "composition")
        elif self.extra is True:
            dirVal = setDir(dirVal, "extra")
        elif self.unofficial is True:
            dirVal = setDir(dirVal, "unofficial")
        return dirVal
    
    def getFilesByRecency(self, files, expr, force=False):
        if force is True:
            newFiles = files
        else:
            rf = recentFiles()
            rf.setFiles(files)
            newFiles = rf.getFilesByRecency(expr)
        return newFiles
    
    def getFilesByLastMod(self, files, expr, ifile, force=False):
        if force is True:
            newFiles = files
        else:
            rf = recentFiles()
            rf.setFiles(files)
            newFiles = rf.getFilesByModTime(expr, ifile)
        return newFiles

    
    
    ##################################################################################################################
    # Raw and Downloaded Files
    ##################################################################################################################
    
    ##########################################
    ## Primary
    ##########################################
    def getArtistPrimaryFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(self.getModValDir(modVal))
        fname = self.disc.getArtistsDBModValFilename(modVal)
        newFiles = files if force is True else self.getFilesByLastMod(files, expr, fname)
        return newFiles
        
    ##########################################
    ## Raw
    ##########################################    
    def getArtistRawFiles(self, datatype, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(setDir(self.disc.getArtistsDir(), datatype))
        newFiles = files if force is True else self.getFilesByRecency(files, expr)
        return newFiles
        
    ##########################################
    ## Raw HTML
    ##########################################    
    def getArtistRawHTMLFiles(self, expr, force=False):
        ffd   = filesFromDir(ext=[".html", ".htm"])
        files = ffd.getFiles(setDir(self.disc.getArtistsDir(), "data"))
        newFiles = files if force is True else self.getFilesByRecency(files, expr)
        return newFiles
    
    ##########################################
    ## Credit
    ##########################################            
    def getArtistCreditFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(self.getModValDir(modVal))
        newFiles = files if force is True else self.getFilesByRecency(files, expr)
        return newFiles
    
    ##########################################
    ## Extra
    ##########################################            
    def getArtistExtraFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(self.getModValDir(modVal))
        newFiles = files if force is True else self.getFilesByRecency(files, expr)
        return newFiles
    
    ##########################################
    ## Unofficial
    ##########################################            
    def getArtistUnofficialFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(self.getModValDir(modVal))
        newFiles = files if force is True else self.getFilesByRecency(files, expr)
        return newFiles
        
    def getAllRawSpotifyFiles(self, dirVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(setDir(dirVal, "spotify"))
        newFiles = self.getFilesByRecency(files, expr)
        return newFiles
        
    def getArtistSongFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(setDir(self.getModValDir(modVal), "song"))
        newFiles = self.getFilesByRecency(files, expr)
        return newFiles
        
    def getArtistCompositionFiles(self, modVal, expr, force=False):
        ffd   = filesFromDir(ext=".p")
        files = ffd.getFiles(setDir(self.getModValDir(modVal), "composition"))
        newFiles = self.getFilesByRecency(files, expr)
        return newFiles


    
    ##################################################################################################################
    # Collect Metadata About Artists
    ##################################################################################################################
    def createArtistMetadata(self, modVal):
        ts = timestat("Creating Artist Metadata For ModVal={0}".format(modVal))
        dbdata = self.getDBData(modVal)
    
        artistIDMetadata = {k: [v.artist.name, v.url.url] for k,v in dbdata.items()}
        for artistID,artistData in dbdata.items():
            if artistData.profile.variations is not None:
                artistIDMetadata[artistID].append([v2.name for v2 in artistData.profile.variations])
            else:
                artistIDMetadata[artistID].append([artistData.artist.name])        
        
        savename = self.disc.getArtistsDBModValMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        saveFile(idata=Series(artistIDMetadata), ifile=savename, debug=False)
        ts.stop()
        
        
    def createAlbumMetadata(self, modVal):
        ts = timestat("Creating Artist Album Metadata For ModVal={0}".format(modVal))
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
        saveFile(idata=Series(artistIDMetadata), ifile=savename, debug=False)
        ts.stop()