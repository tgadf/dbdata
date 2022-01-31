from timeUtils import timestat
from fileIO import fileIO
from dbArtistsBase import dbArtistsBase
from pandas import Series

##################################################################################################################
# Collect Metadata About Artists
##################################################################################################################
class dbArtistsMetadata(dbArtistsBase):
    def __init__(self, dbArtists, modVal=None):
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.io        = fileIO()
        
        _ = self.parse(modVal) if isinstance(modVal,int) else None
            
            
    def parse(self, modVal, **kwargs):
        self.modVal    = modVal
        self.dbData    = self.disc.getDBModValData(modVal)
        self.createArtistMetadata()
        self.createAlbumMetadata()
    
    
    def createArtistMetadata(self):
        ts = timestat("Creating Artist Name Metadata For ModVal={0}".format(self.modVal))
        artistIDMetadata = {str(artistID): [artistData.artist.name, artistData.url.url] for artistID,artistData in self.dbData.items() if artistData.artist.name is not None}
        artistIDMetadata = Series(artistIDMetadata)
        
        print("Saving [{0}] {1} Entries To {2}".format(len(artistIDMetadata), "ID => Name/URL", self.disc.getMetadataArtistFilename(self.modVal)))
        self.disc.saveMetadataArtistData(idata=artistIDMetadata, modVal=self.modVal)
        
        ts.stop()
        
        
    def createAlbumMetadata(self):
        ts = timestat("Creating Artist Album Metadata For ModVal={0}".format(self.modVal))        
        artistIDMetadata = {}
        errs = {}
        for artistID,artistData in self.dbData.items():
            artistID = str(artistID)
            if artistData.artist.name is None:
                continue
            artistIDMetadata[artistID] = {}
            for mediaName,mediaData in artistData.media.media.items():
                try:
                    albumURLs  = {mediaValues.code: mediaValues.url for mediaValues in mediaData}
                    albumNames = {mediaValues.code: mediaValues.album for mediaValues in mediaData}
                    artistIDMetadata[artistID][mediaName] = albumNames #, albumURLs]  
                except:
                    errs[artistID] = artistData.artist.name
                    #print(artistID,'\t',mediaName)
        artistIDMetadata = Series(artistIDMetadata)
        
        print("Saving [{0}] {1} Entries To {2}".format(len(artistIDMetadata), "ID => AlbumNames", self.disc.getMetadataAlbumFilename(self.modVal)))
        self.disc.saveMetadataAlbumData(idata=artistIDMetadata, modVal=self.modVal)    
        
        ts.stop()
        
        print(errs)