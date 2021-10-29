from timeUtils import timestat
from fileIO import fileIO
from dbArtistsBase import dbArtistsBase
from pandas import Series

##################################################################################################################
# Collect Metadata About Artists
##################################################################################################################
class dbArtistMetadata(dbArtistsBase):
    def __init__(self, dbArtists, modVal):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.io        = fileIO()
        self.dbData    = self.getDBData(modVal)
        self.modVal    = modVal
    
    
    def createArtistMetadata(self):
        modVal = self.modVal
        ts = timestat("Creating Artist Name Metadata For ModVal={0}".format(modVal))
        artistIDMetadata = Series({artistID: [artistData.artist.name, artistData.url.url] for artistID,artistData in self.dbData.items()})
        savename = self.disc.getArtistsDBModValMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        self.io.save(idata=artistIDMetadata, ifile=savename)
        ts.stop()
        
        
    def createAlbumMetadata(self):
        modVal = self.modVal
        ts = timestat("Creating Artist Album Metadata For ModVal={0}".format(modVal))
        dbdata = self.dbData
        
        artistIDMetadata = {}
        for artistID,artistData in dbdata.items():
            artistIDMetadata[artistID] = {}
            for mediaName,mediaData in artistData.media.media.items():
                albumURLs  = {mediaValues.code: mediaValues.url for mediaValues in mediaData}
                albumNames = {mediaValues.code: mediaValues.album for mediaValues in mediaData}
                artistIDMetadata[artistID][mediaName] = [albumNames, albumURLs]      
        
        savename = self.disc.getArtistsDBModValAlbumsMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        self.io.save(idata=Series(artistIDMetadata), ifile=savename)
        ts.stop()