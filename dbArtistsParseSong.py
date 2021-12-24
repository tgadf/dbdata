from dbArtistsBase import dbArtistsBase
from fsUtils import isFile
from fileUtils import getBaseFilename
from timeUtils import timestat
from ioUtils import saveFile
from time import sleep
import urllib
from webUtils import getHTML


#################################################################################################################################
# Assert Song (Find Song For AllMusic)
#################################################################################################################################
class dbArtistsAssertSong(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        #self.dbSong = dbArtistsSong(dbArtists)
        print("dbArtistsAssertSong({0})".format(self.db))
        try:
            self.masterIgnoreData = self.getMasterIgnoreData()
            self.songIgnores = self.masterIgnoreData["AllMusic"]["Song"]
            print("  --> Found {0} AllMusic Song IDs To Ignore".format(len(self.songIgnores)))
        except:
            self.songIgnores = []
            #raise ValueError("Could not load AllMusic Credit Ignores data!")
        self.metadata = {}
                
    
    def getMetadata(self):
        return self.metadata
    
    def createSongMetadata(self, modVal=None):
        modVals = [modVal] if modVal is not None else range(100)
            
        ts = timestat("Creating AllMusic Song Metadata")
        for modVal in modVals:
            
            tsDBData = timestat("Finding Known Credit Artists For ModVal={0}".format(modVal))
            dbData = self.getDBData(modVal)
            dbArtistURLs    = {artistID: {"Name": artistData.artist.name, "URL": artistData.url.url} for artistID,artistData in dbData.items()}
            tsDBData.stop()            

            tsCredit = timestat("Finding Known Credit Artists From {0} Artists For ModVal={1}".format(len(dbArtistURLs), modVal))
            creditArtistIDs = {artistID: artistData for artistID,artistData in dbArtistURLs.items() if artistData["URL"] is not None and artistData["URL"].endswith("/credits")}
            tsCredit.stop()
            
            tsIgnore = timestat("Removing IDs To Ignore From {0} Primary Files For ModVal={0}".format(len(creditArtistIDs), modVal))
            availableArtistIDs = {artistID: artistData for artistID,artistData in creditArtistIDs.items() if artistID not in self.songIgnores}
            tsIgnore.stop()
            
            tsMeta = timestat("Finding Metadata For {0}/{1}/{2} Missing ArtistIDs for ModVal={3}".format(len(availableArtistIDs), len(creditArtistIDs), len(dbArtistURLs), modVal))
            self.metadata[modVal] = availableArtistIDs
            tsMeta.stop()
        ts.stop()

    
    def downloadUnknownArtistSongs(self):
        newIgnores = []
        for modVal,modValMetadata in self.metadata.items():
            N = len(modValMetadata)
            ts = timestat("Downloading {0} Unknown Song Files For ModVal={1}".format(N, modVal))
            for i,(artistID,artistIDData) in enumerate(modValMetadata.items()):
                savename = self.dutils.getArtistSavename(artistID, song=True)
                
                href   = artistIDData["URL"]
                artist = artistIDData["Name"]
                if isFile(savename):
                    continue

                ## Replace /credits with /songs
                href = "/".join(href.split('/')[:-1] + ["songs", "all"])
                    
                ## Create Full URL
                url = urllib.parse.urljoin(self.dbArtists.baseURL, href)
                print("\n")
                print("="*100)
                print("{0}/{1}:  [{2}] / [{3}]".format(i,N,artist,url))
                

                data, response = self.dutils.downloadURL(url)
                if response == 200:
                    bsdata = getHTML(data)
                    if len(bsdata.findAll("th", {"class": "title-composer"})) > 0:
                        print("  ---> Saving Data To {0}".format(savename))
                        saveFile(idata=data, ifile=savename)
                        sleep(3)
                        continue
                
                sleep(3)
                newIgnores.append(artistID)
                        
                
                if i == 20:
                    break
            ts.stop()
            
        print("New IDs To Ignore")
        print(newIgnores)
        tsUpdate = timestat("Adding {0} ArtistIDs To Master Song Ignore List".format(len(newIgnores)))
        self.updateMasterIgnoreSongData(newIgnores)
        tsUpdate.stop()  
 
        
#################################################################################################################################
# Song
#################################################################################################################################
class dbArtistsSong(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setSong()
        self.dbArtists = dbArtists
        
    def parse(self, modVal, expr, force=False, debug=False):
        ts = timestat("Parsing ModVal={0} Song Files".format(modVal))  
        
        tsFiles  = timestat("Finding Files To Parse")
        newFiles = self.getArtistSongFiles(modVal, expr, force)
        tsFiles.stop()

        N = len(newFiles)
        modValue = 500 if N >= 1000 else 100
        if N > 0:
            tsDB = timestat("Loading ModVal={0} DB Data".format(modVal))
            dbdata   = self.disc.getDBModValData(modVal) ## We do not want to overwrite other data
            tsDB.stop()
            
        newData  = 0
        tsParse = timestat("Parsing {0} New Song Files For ModVal={1}".format(N, modVal))
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
            print("Saving {0} New Entries".format(newData))
            self.disc.saveDBModValData(idata=dbdata, modVal=modVal) ## We do not want to overwrite other data
            
        tsParse.stop()  