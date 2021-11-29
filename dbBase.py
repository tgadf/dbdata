from fsUtils import isDir, setDir, mkDir, setFile, isFile
from ioUtils import getFile, saveFile
from os import getcwd
from dbUtils import discogsUtils
from fsUtils import moveFile, moveDir, fileUtil
from fileUtils import getFileBasics, getBasename, getDirname
from searchUtils import findExt, findPattern
from glob import glob
from os.path import join
from time import sleep
from collections import Counter

from fileIO import fileIO
from fsUtils import dirUtil, fileUtil, fsPath



class dbBase():
    def __init__(self, db, debug=False):
        if debug:
            print("="*25,"  {0}  ".format(db),"="*25)
        self.base       = db
        self.debug      = debug
        self.dbsavepath   = setDir("/Users/tgadfort/Music", "Discog", forceExist=False)
        self.metasavepath = setDir("/Users/tgadfort/Music", "Discog", forceExist=False)
        self.rawsavepath  = setDir("/Volumes/Piggy", "Discog", forceExist=False)
                
        self.maxModVal  = 100
        self.io = fileIO()
                
        self.createDirectories()
        
        #self.unitTests()
        
    ## Improve upon this later
    def unitTests(self, debug=False):
        ### Various Tests
        dbfiles = self.getArtistsDBFiles()
        assert len(dbfiles) == self.getMaxModVal()
        print("Found {0} artist DB files and that is equal to the max mod value".format(len(dbfiles)))

        
    def getModValList(self, debug=False):
        return list(range(0, self.maxModVal))
    
    def getRawSaveDir(self, debug=False):
        return self.rawsavepath
        
    def getMetaSaveDir(self, debug=False):
        return self.metasavepath
        
    def getDBSaveDir(self, debug=False):
        return self.dbsavepath      
        
        
    def createDirnameDirectories(self, savedir, dirnames):
        localdirnames = dict(zip(dirnames, [setDir(savedir, x) for x in dirnames]))
        for name, dirname in localdirnames.items():
            if not isDir(dirname):
                print("Creating {0}".format(dirname))
                try:
                    mkDir(dirname, debug=True)
                except:
                    print("Cannot create {0}".format(dirname))
            else:
                if self.debug:
                    print("{0} exists".format(dirname))
        return localdirnames
                    
        
    def createDirectories(self):
        if self.debug:
            print("Directory Information:")
            print("  Raw:  {0}".format(self.getRawSaveDir()))
            print("  Meta: {0}".format(self.getMetaSaveDir()))
            print("  DB:   {0}".format(self.getDBSaveDir()))
        
        
        ########################################################################
        # Regular Database Directories
        ########################################################################
        rawdirnames  = []
        metadirnames = []
        names = ["artists", "albums"]
        rawdirnames  += ["{0}-{1}".format(x, self.base) for x in names]
        metadirnames += ["{0}-{1}-db".format(x, self.base) for x in names]
        metadirnames += ["{0}-{1}-db/metadata".format(x, self.base) for x in names]
        self.rawdirnames  = self.createDirnameDirectories(self.getRawSaveDir(), rawdirnames)
        self.metadirnames = self.createDirnameDirectories(self.getMetaSaveDir(), metadirnames)
        

        ########################################################################
        # Complete Database Directories
        ########################################################################
        dbdirnames  = []
        names = ["diagnostic"]
        dbdirnames += ["{0}-{1}".format(x, self.base) for x in names]  
        dbdirnames += ["db-{0}".format(self.base)]
        self.dbdirnames = self.createDirnameDirectories(self.getDBSaveDir(), dbdirnames)

                    
    
    ###############################################################################
    # Basic Artist Functions
    ###############################################################################
    def getArtistSavename(self, discID):
        artistDir = self.disc.getArtistsDir()
        modValue  = self.discogsUtils.getDiscIDHashMod(discID=discID, modval=self.disc.getMaxModVal())
        if modValue is not None:
            outdir    = mkSubDir(artistDir, str(modValue))
            savename  = setFile(outdir, discID+".p")
            return savename
        return None

    
    ###############################################################################
    # Artist ModVals
    ###############################################################################
    def getMaxModVal(self, debug=False):
        return self.maxModVal

    
    ###############################################################################
    # Discog Directories
    ###############################################################################
    def getDiscogDBDir(self, debug=False):
        key = "db-{0}".format(self.base)
        if self.dbdirnames.get(key) is not None:
            return self.dbdirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))


    ####################################################################################################################
    # Syntax
    ####################################################################################################################
    def getDBData(self, dbname, prefix, returnName=False, debug=False):
        savename = setFile(self.getDiscogDBDir(), "{0}{1}.p".format(prefix, dbname))
        if self.debug is True:
            print("Data stored in {0}".format(savename))
        if returnName is True:
            return savename
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
           
        if self.debug:
            print("Returning data from {0}".format(savename))
        data = getFile(savename, debug=debug)
        return data

    ###############################################################################
    ##
    ## Artist Directories
    ##
    ###############################################################################
    def getArtistsDir(self, debug=False):
        key = "artists-{0}".format(self.base)
        if self.rawdirnames.get(key) is not None:
            return self.rawdirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getArtistsExtraDir(self, debug=False):
        key = "artists-extra-{0}".format(self.base)
        if self.rawdirnames.get(key) is not None:
            return self.rawdirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getArtistsDBDir(self, debug=False):
        key = "artists-{0}-db".format(self.base)
        if self.metadirnames.get(key) is not None:
            return self.metadirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    
    ####################################################################################################################
    ## DB Raw Files
    ####################################################################################################################
    def getRawFilename(self, dbID):
        artistDir = self.getArtistsDir()
        modVal = str(int(dbID) % self.maxModVal)
        modDir = fsPath(self.getArtistsDir()).join(modVal)
        return fsPath(modDir).join("{0}.p".format(dbID))
    def getRawData(self, dbID):
        return self.io.get(self.getRawFilename(dbID))

    
    ####################################################################################################################
    ## DB ModVal Data
    ####################################################################################################################
    def getDBModValFilename(self, modVal):
        return fsPath(self.getArtistsDBDir()).join("{0}-DB.p".format(modVal))
    def getDBModValData(self, modVal):
        return self.io.get(self.getDBModValFilename(modVal))
    def saveDBModValData(self, idata, modVal):
        self.io.save(idata=idata, ifile=self.getDBModValFilename(modVal))
    
    
    ####################################################################################################################
    ## Metadata
    ####################################################################################################################
    def getMetadataDir(self, debug=False):
        key = "artists-{0}-db/metadata".format(self.base)
        if self.metadirnames.get(key) is not None:
            return self.metadirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    def getMetadataArtistFilename(self, modVal):
        return fsPath(self.getMetadataDir()).join("{0}-Metadata.p".format(modVal))
    def getMetadataArtistData(self, modVal):
        return self.io.get(self.getMetadataArtistFilename(modVal))
    def saveMetadataArtistData(self, idata, modVal):
        self.io.save(idata=idata, ifile=self.getMetadataArtistFilename(modVal))
        
    def getMetadataAlbumFilename(self, modVal):
        return fsPath(self.getMetadataDir()).join("{0}-MediaMetadata.p".format(modVal))        
    def getMetadataAlbumData(self, modVal):
        return self.io.get(self.getMetadataAlbumFilename(modVal))
    def saveMetadataAlbumData(self, idata, modVal):
        self.io.save(idata=idata, ifile=self.getMetadataAlbumFilename(modVal))


    ####################################################################################################################
    ## Basic Lookup Data
    ####################################################################################################################
    def getArtistIDToNameFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToName", suffix))    
    def getArtistIDToNameData(self, suffix=""):
        return self.io.get(self.getArtistIDToNameFilename(suffix))
    def saveArtistIDToNameData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToNameFilename(suffix))
    
    def getArtistIDToRefFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToRef", suffix))    
    def getArtistIDToRefData(self, suffix=""):
        return self.io.get(self.getArtistIDToRefFilename(suffix))
    def saveArtistIDToRefData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToRefFilename(suffix))
    
    def getArtistIDToNumAlbumsFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToNumAlbums", suffix))
    def getArtistIDToNumAlbumsData(self, suffix=""):
        return self.io.get(self.getArtistIDToNumAlbumsFilename(suffix))
    def saveArtistIDToNumAlbumsData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToNumAlbumsFilename(suffix))
    
    def getArtistIDToAlbumNamesFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToAlbumNames", suffix))
    def getArtistIDToAlbumNamesData(self, suffix=""):
        return self.io.get(self.getArtistIDToAlbumNamesFilename(suffix))
    def saveArtistIDToAlbumNamesData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToAlbumNamesFilename(suffix))


    ####################################################################################################################
    ## Search Lookup Data (Translation + >=2 Albums
    ####################################################################################################################
    def getArtistIDToSearchNameFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToSearchName", suffix))    
    def getArtistIDToSearchNameData(self, suffix=""):
        return self.io.get(self.getArtistIDToSearchNameFilename(suffix))
    def saveArtistIDToSearchNameData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToSearchNameFilename(suffix))
    
    def getArtistIDToSearchNumAlbumsFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToSearchNumAlbums", suffix))
    def getArtistIDToSearchNumAlbumsData(self, suffix=""):
        return self.io.get(self.getArtistIDToSearchNumAlbumsFilename(suffix))
    def saveArtistIDToSearchNumAlbumsData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToSearchNumAlbumsFilename(suffix))
    
    def getArtistIDToSearchAlbumNamesFilename(self, suffix=""):
        return fsPath(self.getDiscogDBDir()).join("{0}{1}{2}.p".format("Artist", "IDToSearchAlbumNames", suffix))
    def getArtistIDToSearchAlbumNamesData(self, suffix=""):
        return self.io.get(self.getArtistIDToSearchAlbumNamesFilename(suffix))
    def saveArtistIDToSearchAlbumNamesData(self, idata, suffix=""):
        self.io.save(idata=idata, ifile=self.getArtistIDToSearchAlbumNamesFilename(suffix))
    


    
    


    ###############################################################################
    ##
    ## Discog Albums Directories
    ##
    ###############################################################################
    def getAlbumsDir(self, debug=False):
        key = "albums-{0}".format(self.base)
        if self.rawdirnames.get(key) is not None:
            return self.rawdirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))

    def getAlbumsDBDir(self, debug=False):
        key = "albums-{0}-db".format(self.base)
        if self.metadirnames.get(key) is not None:
            return self.metadirnames[key]
        else:
            raise ValueError("Base is illegal: {0}".format(self.base))
    
    
    ##################################  Helper ######################################
    def flip(self, db):
        return {v: k for k,v in db.items()}
    
    
    ##################################  Diagnostic ##################################
    def getDiagnosticAlbumIDs(self, debug=False):
        savename = setFile(self.getDiagnosticDir(), "albumKnownIDs.p")
        if not isFile(savename):
            raise ValueError("Could not find {0}".format(savename))
        data = getFile(savename, debug=True)
        return data
    
    def saveDiagnosticAlbumIDs(self, albumIDs):
        savename = setFile(self.getDiagnosticDir(), "albumKnownIDs.p")
        saveFile(ifile=savename, idata=albumIDs)
    
    
    ###############################################################################
    #
    # Master Discogs DB
    #
    ###############################################################################
    
    ###############################################################################
    ### Master Artist
    ###############################################################################
    def getMasterDBArtistFilename(self, debug=False):
        return self.getDBData("DB", "MasterArtist", returnName=True)
        
    def getMasterDBArtistDataFrame(self, debug=False):
        return self.getDBData("DB", "MasterArtist")

    def getMasterDBArtistIDToNameData(self, debug=False):
        return self.getDBData("", "MasterArtistIDToName")

    def getMasterDBArtistNameToIDData(self, debug=False):
        return self.getDBData("", "MasterArtistNameToID")

    
    ###############################################################################
    ### Master Artist Albums
    ############################################################################### 
    def getMasterDBArtistAlbumsFilename(self, debug=False):
        return self.getDBData("DB", "MasterArtistAlbums", returnName=True)

    def getMasterDBArtistIDToAlbumsData(self, debug=False):
        return self.getDBData("", "MasterArtistIDToAlbums")

    def getMasterDBArtistIDToNumAlbumsData(self, debug=False):
        return self.getDBData("", "MasterArtistIDToNumAlbums")
        
    def getMasterDBArtistAlbumsDataFrame(self, debug=False):
        return self.getDBData("DB", "MasterArtistAlbums")
    
        
    ###############################################################################
    #
    # Artist Lookups
    #
    ###############################################################################
    def getArtistIDToPreMergeNameData(self, debug=False):
        return self.getDBData("IDToNamePreMerge", "Artist", debug=debug)
    
    def getArtistIDToPreMergeRefData(self, debug=False):
        return self.getDBData("IDToRefPreMerge", "Artist", debug=debug)

    def getArtistIDToPreMergeNumAlbumsData(self, debug=False):
        return self.getDBData("IDToNumAlbumsPreMerge", "Artist", debug=debug)
    
    def getArtistIDToNameData(self, debug=False):
        return self.getDBData("IDToName", "Artist", debug=debug)
    
    def getArtistNameToIDData(self, debug=False):
        return self.getDBData("NameToID", "Artist", debug=debug)
        
    def getArtistIDToRefData(self, debug=False):
        return self.getDBData("IDToRef", "Artist", debug=debug)

    def getArtistIDToAlbumNamesData(self, debug=False):
        return self.getDBData("IDToAlbumNames", "Artist", debug=debug)

    def getArtistIDToAlbumRefsData(self, debug=False):
        return self.getDBData("IDToAlbumRefs", "Artist", debug=debug)
    
    
    ###############################################################################
    #
    # Album Lookups
    #
    ###############################################################################
    def getAlbumIDToNameData(self, debug=False):
        return self.getDBData("IDToName", "Album")
    
    def getAlbumIDToRefData(self, debug=False):
        return self.getDBData("IDToRef", "Album")
    
    def getAlbumIDToArtistsData(self, debug=False):
        return self.getDBData("IDToArtists", "Album")
    
    def getAlbumNameToIDData(self, debug=False):
        return self.getDBData("NameToID", "Album")
    
    def getAlbumNameToIDsData(self, debug=False):
        return self.getDBData("NameToIDs", "Album")
    
    def getAlbumNameToRefData(self, debug=False):
        return self.getDBData("NameToRef", "Album")

    def getAlbumRefToIDData(self, debug=False):
        return self.getDBData("RefToID", "Album")
    
    def getAlbumRefToNameData(self, debug=False):
        return self.getDBData("RefToName", "Album")
    
    def getAlbumIDToArtistIDData(self, debug=False):
        return self.getDBData("IDToArtistID", "Album")
    
    def getAlbumArtistMetaData(self, debug=False):
        return self.getDBData("ArtistMetaData", "Album")
    
    
    ##################################  Ascii Lookup ##################################
    def getArtistAsciiNames(self, debug=False):
        return self.getDBData("AsciiNames", "Artist", debug=debug)
    
    
    ###############################################################################
    # Moving Functions
    ###############################################################################
    def moveAlbumFilesToNewModValue(self, newModValue, oldModValue):
        filedir    = self.getAlbumsDir()
        dutils     = discogsUtils()
        for modVal in range(oldModValue):
            modValue  = dutils.getDiscIDHashMod(discID=modVal, modval=newModValue) #disc.getMaxModVal())
            if modVal == modValue:
                sleep(1)
                continue
            else:
                dirs = glob(join(filedir, str(modVal), "*"))
                print("Moving {0} directories from {1} to {2}".format(len(dirs), modVal, modValue))
                for idir in dirs:
                    dname = getDirname(idir)
                    src = idir
                    dst = join(filedir, str(modValue), dname)
                    print(src)
                    print(dst)
                    1/0
                    moveDir(src, dst)

        
    def moveArtistFilesToNewModValue(self, newModValue, oldModValue):
        filedir    = self.getArtistsDir()
        dutils     = discogsUtils()
        for modVal in range(oldModValue):
            modValue  = dutils.getDiscIDHashMod(discID=modVal, modval=newModVal) #disc.getMaxModVal())
            if modVal == modValue:
                sleep(1)
                continue
            else:
                files = glob(join(filedir, str(modVal), "*.p"))
                print("Moving {0} files from {1} to {2}".format(len(files), modVal, modValue))
                for ifile in files:
                    fbasics = getFileBasics(ifile)
                    fname = getBasename(ifile)
                    src = ifile
                    dst = join(artistsDir, str(modValue), fname)
                    moveFile(src, dst)

                            

    def moveExtArtistFilesToNewModValue(self, newModVal):
        artistsDir     = self.getArtistsDir()
        extArtistsDir  = self.getArtistsExtraDir()
        dutils         = discogsUtils()

        files = glob(join(extArtistsDir, "*.p"))
        print("Moving {0} files".format(len(files)))
        for ifile in files:
            fbasics   = getFileBasics(ifile)
            fname     = getBasename(ifile)
            discID    = fbasics[1].split('-')[0]
            modValue  = dutils.getDiscIDHashMod(discID=discID, modval=newModVal) #disc.getMaxModVal())

            src = ifile
            dst = join(artistsDir, str(modValue), fname)
            moveFile(src, dst)

    def mergeArtistDBs(self, debug=False):
        from glob import glob
        from os.path import join

        artistsDBDir = self.getArtistsDBDir()
        dutils       = discogsUtils()

        for modVal in self.getModValList():
            dbdata = {}
            files = glob(join(artistsDBDir, "old/*.p"))
            print(modVal,len(files))
            for ifile in files:
                fbasics  = getFileBasics(ifile)
                oldValue = int(fbasics[1].split('-')[0])
                modValue = dutils.getDiscIDHashMod(discID=oldValue, modval=disc.getMaxModVal())
                if modValue == modVal:
                    db = getFile(ifile)
                    dbdata.update(db)


            savename = setFile(artistsDBDir, "{0}-DB.p".format(modVal))     
            print("Saving {0} artist IDs to {1}".format(len(dbdata), savename))
            saveJoblib(data=dbdata, filename=savename, compress=True)