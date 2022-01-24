from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename
from fsUtils import isFile, setFile, setDir
from ioUtils import getFile, saveFile
from timeUtils import timestat
from sys import prefix
import urllib
from time import sleep
from webUtils import getHTML
from pandas import Series
    
from fileIO import fileIO
from fsUtils import fileUtil
from artistModValue import artistModValue


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
            dbdata = Series(dbdata)
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
            if retval is None:
                if debug:
                    print("Could not find data for {0}".format(ifile))
                continue
            artistID = retval.ID.ID
            if artistID is None:
                if debug:
                    print("Could not find artistID for {0}".format(ifile))
                continue
            savename = self.dutils.getArtistSavename(artistID)
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
# Parse From Pickled API
#################################################################################################################################
class dbArtistsPickleAPI(dbArtistsBase):
    def __init__(self, dbArtists):
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
        self.artistAlbums = None
        self.artistTracks = None
        self.artistsData  = None
        
            
    def parse(self, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Raw Pickled API Files(expr=\'{0}\', force={1}, debug={2}, quiet={3})".format(expr, force, debug, quiet))
        
        io = fileIO()
        newFiles = self.getArtistRawFiles(datatype="data", expr=expr, force=force)
        print("Found {0} New Files".format(len(newFiles)))

        tracksData  = {}
        albumsData  = {}
        artistsData = {}        
        
        N = len(newFiles)
        modValue = 500 if N >= 5000 else 100
        nSave = 0
        tsParse = timestat("Parsing {0} Raw Picked API Files".format(N))
        for i,ifile in enumerate(newFiles):
            dData = io.get(ifile)

            for item in dData:
                dArtist = deezerArtist(item)
                dAlbum  = deezerAlbum(item)
                dAlbum.setArtistID(dArtist.id)
                dTrack  = deezerTrack(item)
                dTrack.setArtistID(dArtist.id)
                dTrack.setAlbumID(dAlbum.id)

                if tracksData.get(dTrack.id) is None:
                    tracksData[dTrack.id] = dTrack
                if albumsData.get(dAlbum.id) is None:
                    albumsData[dAlbum.id] = dAlbum
                if artistsData.get(dArtist.id) is None:
                    artistsData[dArtist.id] = dArtist

            if (i+1) % 2500 == 0 or (i+1) == 500:
                tsParse.update(n=i+1,N=N)
        tsParse.stop()
        
        
        artistAlbums = {}
        for albumID,album in albumsData.items():
            if artistAlbums.get(album.artistID) is None:
                artistAlbums[album.artistID] = {}
            artistAlbums[album.artistID][album.id] = {"Name": album.name, "URL": album.tracks, "Type": album.type}
            
        artistTracks = {}
        for trackID,track in tracksData.items():
            if artistTracks.get(track.artistID) is None:
                artistTracks[track.artistID] = {}
            artistTracks[track.artistID][track.id] = {"Name": track.title, "URL": track.link, "Type": track.type}
            
            

        modValuesData = {modValue: {} for modValue in range(self.dutils.maxModVal)}
        print("Found {0} Artists".format(len(artistsData)))
        print("Found {0} Artists/Albums w/ ({1}) Albums".format(len(artistAlbums), len(albumsData)))
        print("Found {0} Artists/Tracks w/ ({1}) Tracks".format(len(artistTracks), len(tracksData)))
        for artistID,artist in artistsData.items():
            modValue = self.dutils.getDiscIDHashMod(artistID, self.dutils.maxModVal)
            artistAPIData = {"Name": artist.name, "URL": artist.link, "Type": artist.type, "ID": str(artist.id),
                             "Tracks": artistTracks.get(artist.id, {}), "Albums": artistAlbums.get(artist.id, {})}
            modValuesData[modValue][artistID] = self.artist.getData(artistAPIData)


        for modVal,modValueData in modValuesData.items():
            dbdata = Series(modValueData)
            print("Saving [{0}/{1}] {2} Entries To {3}".format(len(dbdata), len(dbdata), "ID Data", self.disc.getDBModValFilename(modVal)))
            self.disc.saveDBModValData(modVal=modVal, idata=dbdata)
                
        ts.stop()
            
            
            
#################################################################################################################################
# Parse From Spotify API
#################################################################################################################################
class dbArtistsSpotifyAPI(dbArtistsBase):
    def __init__(self, dbArtists):
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
        self.artistAlbums = None
        self.artistTracks = None
        self.artistsData  = None
            
            
    def parse(self, modVal, expr, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Raw Pickled Spotify API Primary ModVal={0} Files(expr=\'{1}\', force={2}, debug={3}, quiet={4})".format(modVal, expr, force, debug, quiet))
        
        io = fileIO()
        newFiles = self.getArtistPrimaryFiles(modVal, expr, force)
        print("Found {0} New Files".format(len(newFiles)))
        if len(newFiles) == 0:            
            return
        
        artistSearchFilename = self.getArtistRawFiles(datatype="search", expr=expr, force=True)
        if len(artistSearchFilename) == 1:
            artistSearchData = io.get(artistSearchFilename[0])
        else:
            raise ValueError("Could not find Spotify API Artist Search Data")
                
        if force is True or not fileUtil(self.disc.getDBModValFilename(modVal)).exists:
            tsDB = timestat("Creating New DB For ModVal={0}".format(modVal))
            dbdata = Series({})
            ts.stop()
        else:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata = self.disc.getDBModValData(modVal)
            tsDB.stop()
        
        
        N = len(newFiles)
        modValue = 500 if N >= 5000 else 100
        nSave = 0
        tsParse = timestat("Parsing {0} Raw Picked API Files".format(N))
        for i,ifile in enumerate(newFiles):
            dData = io.get(ifile)
            artistID = dData['artistID']
            try:
                artistData = artistSearchData.loc[artistID]
            except:
                print("Could not find Spotify ID [{0}]".format(artistID))
                continue
                
            artistAPIData = {"Artist": artistData, "Albums": dData}
            dbdata = dbdata.append(Series({artistID: self.artist.getData(artistAPIData)}))
            nSave += 1
            
        if nSave > 0:
            print("Saving [{0}/{1}] {2} Entries To {3}".format(nSave, len(dbdata), "ID Data", self.disc.getDBModValFilename(modVal)))
            self.disc.saveDBModValData(modVal=modVal, idata=dbdata)
        else:
            print("Not saving any of the new data")
                
        ts.stop()
        
    
    def parseSearch(self, modVal, expr=None, force=False, debug=False, quiet=False):
        ts = timestat("Parsing Spotify Search ModVal={0} Files(expr=\'{1}\', force={2}, debug={3}, quiet={4})".format(modVal, expr, force, debug, quiet))
                
        if not fileUtil(self.disc.getDBModValFilename(modVal)).exists:
            tsDB = timestat("Creating New DB For ModVal={0}".format(modVal))
            dbdata = Series({})
            ts.stop()
        else:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata = self.disc.getDBModValData(modVal)
            tsDB.stop()
            
        
        io = fileIO()
        artistSearchFilename = self.getArtistRawFiles(datatype="search", expr=expr, force=True)
        if len(artistSearchFilename) == 1:
            artistSearchData = io.get(artistSearchFilename[0])
        else:
            raise ValueError("Could not find Spotify API Artist Search Data")
        #print(artistSearchData.columns)
        
        
        amv = artistModValue()
        idx = artistSearchData.reset_index()['sid'].apply(amv.getModVal) == modVal
        idx.index = artistSearchData.index
        artists = artistSearchData[idx]
        N = artists.shape[0]
        
        tsParse = timestat("Parsing {0} Searched For Spotify API Artists".format(N))
        Nnew = 0
        for artistID,artistData in artists.iterrows():
            if dbdata.get(artistID) is not None:
                continue
            artistAPIData = {"Artist": artistData, "Albums": {}}
            dbdata = dbdata.append(Series({artistID: self.artist.getData(artistAPIData)}))
            Nnew += 1
            
        if Nnew > 0:
            print("Saving [{0}/{1}] {2} Entries To {3}".format(len(dbdata), len(dbdata), "ID Data", self.disc.getDBModValFilename(modVal)))
            self.disc.saveDBModValData(modVal=modVal, idata=dbdata)
        else:
            print("Not saving any of the new data")
                
        ts.stop()
            

            

class deezerTrack:
    def __init__(self, item):
        self.id    = item.get('id')
        self.link  = item.get('link')
        self.title = item.get('title_short')
        self.title = item.get('title') if self.title is None else self.title
        self.type  = item.get('track')
        self.artistID = None
        self.albumID  = None
        
    def setArtistID(self, artistID):
        self.artistID = artistID
        
    def setAlbumID(self, albumID):
        self.albumID = albumID
        

class deezerArtist:
    def __init__(self, item):    
        artistData  = item.get('artist', {})
        self.id     = artistData.get('id')
        self.name   = artistData.get('name')
        self.link   = artistData.get('link')
        self.tracks = artistData.get('tracklist')
        self.type   = artistData.get('type')
        
        
class deezerAlbum:
    def __init__(self, item):
        albumData   = item.get('album', {})
        self.id     = albumData.get('id')
        self.name   = albumData.get('title')
        self.tracks = albumData.get('tracklist')
        self.type   = albumData.get('type')
        self.artistID    = None
        
    def setArtistID(self, artistID):
        self.artistID = artistID