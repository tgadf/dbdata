from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename
from fsUtils import isFile, setFile, setDir
from ioUtils import getFile, saveFile
from timeUtils import timestat
from sys import prefix
import urllib
from time import sleep
from webUtils import getHTML
    
from fileIO import fileIO
from fsUtils import fileUtil


#################################################################################################################################
# Primary
#################################################################################################################################
class dbArtistsPrimary(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
    def parse(self, modVal, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Primary ModVal={0} Files(expr=\'{1}\', force={2}, debug={3}, quiet={4})".format(modVal, expr, force, debug, quiet))
                
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistPrimaryFiles(modVal, expr, force)
        tsFiles.stop()

        N = len(newFiles)        
        if N == 0:
            ts.stop()
            return
        
        modValue = max([250 * round((N/10)/250), 250])

        if force is True or not fileUtil(self.disc.getDBModValFilename(modVal)).exists:
            tsDB = timestat("Creating New DB For ModVal={0}".format(modVal))
            dbdata = {}
            ts.stop()
        else:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata = self.disc.getDBModValData(modVal)
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Files For ModVal={1}".format(N, modVal))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                tsParse.update(n=i+1, N=N)
                #print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
                
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
            print("Saving [{0}/{1}] {2} Entries To {3}".format(newData, len(dbdata), "ID Data", self.disc.getDBModValFilename(modVal)))
            self.disc.saveDBModValData(modVal=modVal, idata=dbdata)
        
        ts.stop()
        
        return newData > 0
    

#################################################################################################################################
# Parse From HTML
#################################################################################################################################
class dbArtistsHTML(dbArtistsBase):
    def __init__(self, dbArtists):
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
            
    def parse(self, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Raw HTML Files(expr=\'{0}\', force={1}, debug={2}, quiet={3})".format(expr, force, debug, quiet))
        
        io = fileIO()
        newFiles = self.getArtistRawHTMLFiles(expr, force=force)
        
        N = len(newFiles)
        modValue = 250 if N >= 500 else 50
        modValue = 500 if N >= 2000 else modValue
        nSave = 0
        tsParse = timestat("Parsing {0} Raw HTML Files".format(N))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                tsParse.update(n=i+1, N=N)
            htmldata = io.get(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            savename = self.dutils.getArtistSavename(artistID)
            if isinstance(savename,str) and (force == True or fileUtil(savename).exists == False):
                io.save(idata=retval, ifile=savename)
                nSave += 1
                
        ts.stop()
        print("Saved {0} New Files".format(nSave))
    

#################################################################################################################################
# Parse From Pickled HTML
#################################################################################################################################
class dbArtistsPickleHTML(dbArtistsBase):
    def __init__(self, dbArtists):
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
            
    def parse(self, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Raw Pickled HTML Files(expr=\'{0}\', force={1}, debug={2}, quiet={3})".format(expr, force, debug, quiet))
        
        io = fileIO()
        newFiles = self.getArtistRawFiles(datatype="data", expr=expr, force=force)
        
        N = len(newFiles)
        modValue = 250 if N >= 500 else 50
        nSave = 0
        tsParse = timestat("Parsing {0} Raw Picked HTML Files".format(N))
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N or debug:
                tsParse.update(n=i+1, N=N)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            savename = self.dutils.getArtistSavename(artistID)
            print(ifile,'\t',artistID,'\t',savename)
            if isinstance(savename,str) and (force == True or fileUtil(savename).exists == False):
                io.save(idata=retval, ifile=savename)
                nSave += 1
                
        ts.stop()
        print("Saved {0} New Files".format(nSave))
                

#################################################################################################################################
# Parse From Raw HTML
#################################################################################################################################
class dbArtistsRawHTML(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
            
    def parse(self, expr, force=False, debug=False, quiet=False):
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
                tsParse.update(n=i+1, N=N)
                #print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
            
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
        
    def parse(self, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Raw Files")  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistRawFiles(datatype=self.datatype, expr=expr, force=force)
        tsFiles.stop()
            
        N = len(newFiles)
        tsParse = timestat("Parsing {0} New Raw Files".format(N))
        
        newData = 0
        modValue = 250 if N >= 500 else 50
        for i,ifile in enumerate(newFiles):
            if (i+1) % modValue == 0 or (i+1) == N:
                tsParse.update(n=i+1, N=N)
                #print("{0: <15}Parsing {1}".format("{0}/{1}".format(i+1,N), ifile))
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
        

            
