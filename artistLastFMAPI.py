from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from dbUtils import utilsLastFMAPI
from dbUtils import utilsMusicBrainz
from pandas import Series, DataFrame
from hashlib import md5

class artistLastFMAPI(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsLastFMAPI()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        if self.dbdata is not None:
            return self.dbdata
        if not isinstance(self.bsdata, dict):
            raise ValueError("Could not parse LastFM API data")
            
        
        tracks = self.bsdata["Tracks"]
        albums = self.bsdata["Albums"]
        if len(tracks) > 0:
            artistData = {"Name": tracks[0]["artistName"], "URL": tracks[0]["artistURL"], "MBID": tracks[0]["artistMBID"]}
        elif len(albums) > 0:
            artistData = {"Name": albums[0]["artistName"], "URL": albums[0]["artistURL"], "MBID": albums[0]["artistMBID"]}
        else:
            return None
            raise ValueError("No track/album data!")
            
        artistName   = artistData["Name"]
        artistURL    = artistData["URL"]
        artistID     = self.dbUtils.getArtistID(artistURL)
        generalData  = None
        externalData = {"MusicBrainzID": artistData["MBID"]}
        #mbID       = mbutil.getArtistID(artistData['MBID']
    
    
        trackData = [{"Name": track["name"], "URL": track["URL"], "Counts": int(track["counts"])} for track in tracks if int(track["counts"]) > 50]
        counts    = sorted([x["Counts"] for x in trackData], reverse=True)
        idx       = min([len(counts)-1,1000-1])
        trackData = [v for v in trackData if v['Counts'] >= counts[idx]]
        
        albumData = [{"Name": album["name"], "URL": album["URL"], "Counts": int(album["counts"])} for album in albums if int(album["counts"]) > 25]
        counts    = sorted([x["Counts"] for x in albumData], reverse=True)
        idx       = min([len(counts)-1,1000-1])
        albumData = [v for v in albumData if v['Counts'] >= counts[idx]]

        mediaData = {}
        if len(trackData) > 0:
            mediaName = "Tracks"
            mediaData[mediaName] = []
            for artistTrack in trackData:
                m = md5()
                m.update(artistTrack['Name'].encode('utf-8'))
                m.update(artistTrack['URL'].encode('utf-8'))
                hashval = m.hexdigest()
                code  = str(int(hashval, 16) % int(1e7))

                album        = artistTrack["Name"]
                albumURL     = artistTrack["URL"]
                albumArtists = [artistData["Name"]]

                amdc = artistDBMediaDataClass(album=album, url=albumURL, artist=albumArtists, code=code, year=None)
                mediaData[mediaName].append(amdc)

        if len(albumData) > 0:
            mediaName = "Albums"
            mediaData[mediaName] = []
            for artistAlbum in albumData:
                m = md5()
                m.update(artistAlbum['Name'].encode('utf-8'))
                m.update(artistAlbum['URL'].encode('utf-8'))
                hashval = m.hexdigest()
                code  = str(int(hashval, 16) % int(1e7))
                
                album        = artistAlbum["Name"]
                albumURL     = artistAlbum["URL"]
                albumArtists = [artistName]

                amdc = artistDBMediaDataClass(album=album, url=albumURL, artist=albumArtists, code=code, year=None)
                mediaData[mediaName].append(amdc)

        
        artist      = artistDBNameClass(name=artistName, err=None)
        meta        = artistDBMetaClass(title=None, url=artistURL)
        url         = artistDBURLClass(url=artistURL)
        ID          = artistDBIDClass(ID=artistID)
        pages       = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        profile     = artistDBProfileClass(general=generalData, external=externalData)
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