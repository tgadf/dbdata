from timeUtils import timestat
from fileIO import fileIO
from fileInfo import fileInfo
from dbArtistsBase import dbArtistsBase

##################################################################################################################
# Collect Metadata About Artists
##################################################################################################################
class dbArtistMetadata:
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.io = fileIO()
    
    
    def createArtistMetadata(self, modVal):
        ts = timestat("Creating Artist Name Metadata For ModVal={0}".format(modVal))
        artistIDMetadata = Series({artistID: [artistData.artist.name, artistData.url.url] for artistID,artistData in self.getDBData(modVal).items()})
        savename = self.disc.getArtistsDBModValMetadataFilename(modVal)
        print("Saving {0} new artist IDs name data to {1}".format(len(artistIDMetadata), savename))
        self.io.save(idata=artistIDMetadata, ifile=savename)
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
        self.io.save(idata=artistIDMetadata, ifile=savename)
        ts.stop()