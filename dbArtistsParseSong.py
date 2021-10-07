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