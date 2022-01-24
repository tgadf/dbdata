from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from dbUtils import utilsBase
from pandas import Series, DataFrame, to_datetime
from hashlib import md5

class artistSpotify(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsBase()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        if self.dbdata is not None:
            return self.dbdata
        if not isinstance(self.bsdata, dict):
            raise ValueError("Could not parse Spotify API data")
            
        
        artistData       = self.bsdata['Artist']
        artistID         = artistData.name
        artistURI        = artistData.get('uri')
        artistType       = artistData.get('stype')
        artistPopularity = artistData.get('popularity')
        artistName       = artistData.get('name')
        artistAPIURL     = artistData.get('href')
        artistGenres     = artistData.get('genres', [])
        artistFollowers  = artistData.get('followers')
        artistURL        = artistData.get('urls', {}).get('spotify')
        
        generalData  = {"Type": artistType}
        genresData   = artistGenres if len(artistGenres) > 0 else None
        externalData = {'SpotifyAPI': {"URL": artistAPIURL, "URI": artistURI}}
        extraData    = {'Followers': artistFollowers, "Popularity": artistPopularity}
        
        mediaData = {}
        albumsData = self.bsdata['Albums']
        if len(albumsData) > 0:
            albumsURL  = albumsData.get('href')
            if albumsData.get('artistID') != artistID:
                raise ValueError("ArtistIDs do not match for Spotify API Data! [{0}, {1}]".format(albumsData.get('artistID'), artistID))

            mediaData = {}
            for albumData in albumsData.get('albums', []):
                albumID      = albumData.get('sid')
                albumGroup   = albumData.get('album_group')
                albumType    = albumData.get('album_type')
                albumSType   = albumData.get('stype')
                albumArtists = [{artist['sid']: artist['name']} for artist in albumData.get('artists', [])]
                albumURL     = albumData.get('urls', {}).get('spotify')
                albumURI     = albumData.get('uri')
                albumAPI     = albumData.get('href')
                albumName    = albumData.get('name')
                albumTracks  = albumData.get('numtracks')
                albumDate    = albumData.get('date')
                albumYear    = to_datetime(albumDate).year if albumDate is not None else None

                if all([albumGroup,albumType]):
                    mediaName = " + ".join([albumGroup,albumType])
                elif albumGroup is not None:
                    mediaName = albumGroup
                elif albumType is not None:
                    mediaName = albumType
                else:
                    mediaName = "Unknown"


                amdc = artistDBMediaDataClass(album=albumName, url=albumURL, artist=albumArtists, code=albumID, year=albumYear, aclass=albumSType,
                                              aformat={"URI": albumURI, "API": albumAPI, "Date": albumDate, "NumTracks": albumTracks})
                if mediaData.get(mediaName) is None:
                    mediaData[mediaName] = []
                mediaData[mediaName].append(amdc)
                


        artist      = artistDBNameClass(name=artistName, err=None)
        meta        = artistDBMetaClass(title=None, url=artistURL)
        url         = artistDBURLClass(url=artistURL)
        ID          = artistDBIDClass(ID=artistID)
        pages       = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        profile     = artistDBProfileClass(general=generalData, external=externalData, extra=extraData, genres=genresData)
        media       = artistDBMediaClass()
        media.media = mediaData
        mediaCounts = self.getMediaCounts(media)
        info        = self.getInfo()
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, info=info)
        
        return adc
    
    
    ##############################################################################################################################
    ## File Info
    ##############################################################################################################################
    def getInfo(self):
        afi = artistDBFileInfoClass(info=self.fInfo)
        return afi
    
    

    ##############################################################################################################################
    ## Artist Media Counts
    ##############################################################################################################################
    def getMediaCounts(self, media):
        
        amcc = artistDBMediaCountsClass()
        
        credittype = "Releases"
        if amcc.counts.get(credittype) == None:
            amcc.counts[credittype] = {}
        for creditsubtype in media.media.keys():
            amcc.counts[credittype][creditsubtype] = int(len(media.media[creditsubtype]))
            
        return amcc