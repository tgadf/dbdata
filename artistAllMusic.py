from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from strUtils import fixName
from dbUtils import utilsAllMusic
from hashlib import md5


class artistAllMusic(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsAllMusic()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(url)
        pages       = self.getPages()
        profile     = self.getProfile()
        media       = self.getMedia(url.url)
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
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        artistBios = self.bsdata.findAll("div", {"class": "artist-bio-container"})
        if len(artistBios) > 0:
            for div in artistBios:
                h1 = div.find("h1", {"class": "artist-name"})
                if h1 is not None:
                    artistName = h1.text.strip()
                    if len(artistName) > 0:
                        artist = fixName(artistName)
                        anc = artistDBNameClass(name=artist, err=None)
                    else:
                        artist = "?"
                        anc = artistDBNameClass(name=artist, err="Fix")
                else:
                    anc = artistDBNameClass(err="NoH1")
        else:       
            anc = artistDBNameClass(err=True)
            return anc
        
        return anc
    
    

    ##############################################################################################################################
    ## Meta Information
    ##############################################################################################################################
    def getMeta(self):
        metatitle = self.bsdata.find("meta", {"property": "og:title"})
        metaurl   = self.bsdata.find("meta", {"property": "og:url"})

        title = None
        if metatitle is not None:
            title = metatitle.attrs['content']

        url = None
        if metatitle is not None:
            url = metaurl.attrs['content']

        amc = artistDBMetaClass(title=title, url=url)
        return amc
        

    ##############################################################################################################################
    ## Artist URL
    ##############################################################################################################################
    def getURL(self):
        result1 = self.bsdata.find("link", {"rel": "canonical"})
        result2 = self.bsdata.find("link", {"hreflang": "en"})
        if result1 and not result2:
            result = result1
        elif result2 and not result1:
            result = result2
        elif result1 and result2:
            result = result1
        else:        
            auc = artistDBURLClass(err=True)
            return auc

        if result:
            url = result.attrs["href"]
            url = url.replace("https://www.allmusic.com", "")
            if url.find("/artist/") == -1:
                url = None
                auc = artistDBURLClass(url=url, err="NoArtist")
            else:
                auc = artistDBURLClass(url=url)
        else:
            auc = artistDBURLClass(err="NoLink")

        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, suburl):
        discID = self.dbUtils.getArtistID(suburl.url, debug=False)
        aic = artistDBIDClass(ID=discID)
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        apc   = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):
        generalData = None
        genreData   = None
        tagsData    = None
        extraData   = None

        content     = self.bsdata.find("meta", {"name": "title"})
        contentAttr = content.attrs if content is not None else None
        searchTerm  = contentAttr.get("content") if contentAttr is not None else None
        searchData  = [artistDBTextClass(searchTerm)] if searchTerm is not None else None
        
        tabsul      = self.bsdata.find("ul", {"class": "tabs"})
        #print('tabsul',tabsul)
        refs        = tabsul.findAll("a") if tabsul is not None else None
        #print('refs',refs)
        tabLinks    = [artistDBLinkClass(ref) for ref in refs] if refs is not None else None
        #print('tabLinks',tabLinks)
        #print('tabLinks',[x.get() for x in tabLinks])
        tabKeys = []
        if isinstance(tabLinks, list):
            for i,tabLink in enumerate(tabLinks):
                keyTitle = tabLink.title
                keyText  = tabLink.text
                if keyTitle is not None:
                    tabKeys.append(keyTitle)
                    continue
                if keyText is not None:
                    key = keyText.replace("\n", "").split()[0]
                    tabKeys.append(key)
                    continue
                tabKeys.append("Tab {0}".format(i))
        else:
            tabKeys = None
            
        tabsData    = dict(zip(tabKeys, tabLinks)) if (isinstance(tabKeys, list) and all(tabKeys)) else None
        #print('tabsData', tabsData)

        if searchData is not None:
            if extraData is None:
                extraData = {}
            extraData["Search"] = searchData
        if tabsData is not None:
            if extraData is None:
                extraData = {}
            extraData["Tabs"] = tabsData
        #print('extraData',extraData)


        basicInfo = self.bsdata.find("section", {"class": "basic-info"})
        if basicInfo is not None:
            for div in basicInfo.findAll("div"):
                attrs = div.attrs.get('class')
                if isinstance(attrs, list) and len(attrs) == 1:
                    attrKey = attrs[0]
                    if attrKey == "genre":
                        refs = div.findAll("a")
                        val  = [artistDBTextClass(div)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
                        genreData = val
                    elif attrKey == "styles":
                        refs = div.findAll("a")
                        val  = [artistDBTextClass(div)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
                        tagsData = val
                    else:
                        if generalData is None:
                            generalData = {}
                        refs = div.findAll("a")
                        val  = [artistDBTextClass(div)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
                        generalData[attrKey] = val

        apc = artistDBProfileClass(general=generalData, tags=tagsData, genres=genreData, extra=extraData)
        return apc

    
    
    ##############################################################################################################################
    ## Artist Media
    ##############################################################################################################################
    def getMediaAlbum(self, td):
        amac = artistDBMediaAlbumClass()
        for span in td.findAll("span"):
            attrs = span.attrs
            if attrs.get("class"):
                if 'format' in attrs["class"]:
                    albumformat = span.text
                    albumformat = albumformat.replace("(", "")
                    albumformat = albumformat.replace(")", "")
                    amac.format = albumformat
                    continue
            span.replaceWith("")

        ref = td.find("a")
        if ref:
            amac.url   = ref.attrs['href']
            amac.album = ref.text
        else:
            amac.err = "NoText"

        return amac
    
    
    #def getMediaCredits(self):
    def getMediaSongs(self):
        mediaType = "Songs"
        media  = {}
        tables = self.bsdata.findAll("table")
        for table in tables:
            trs = table.findAll("tr")

            header  = trs[0]
            ths     = header.findAll("th")
            headers = [x.text.strip() for x in ths]
            if len(headers) == 0:
                continue
            for j,tr in enumerate(trs[1:]):
                tds  = tr.findAll("td")
                vals = [td.text.strip() for td in tds]

                tdTitle   = tr.find("td", {"class": "title-composer"})
                divTitle  = tdTitle.find("div", {"class": "title"}) if tdTitle is not None else None
                compTitle = tdTitle.find("div", {"class": "composer"}) if tdTitle is not None else None

                songTitle = divTitle.text if divTitle is not None else None
                songTitle = songTitle.strip() if songTitle is not None else None
                songURL   = divTitle.find('a') if divTitle is not None else None
                songURL   = artistDBLinkClass(songURL) if songURL is not None else None
                
                if songTitle is None:
                    continue

                songArtists = compTitle.findAll("a") if compTitle is not None else None
                if songArtists is not None:
                    if len(songArtists) == 0:
                        songArtists = [artistDBTextClass(compTitle.text)]
                    else:
                        songArtists = [artistDBLinkClass(ref) for ref in songArtists]
                        
                m = md5()
                m.update(str(j).encode('utf-8'))
                if songTitle is not None:
                    m.update(songTitle.encode('utf-8'))
                code = str(int(m.hexdigest(), 16) % int(1e5))

                amdc = artistDBMediaDataClass(album=songTitle, url=songURL, aclass=None, aformat=None, artist=songArtists, code=code, year=None)
                if media.get(mediaType) is None:
                    media[mediaType] = []
                media[mediaType].append(amdc)
                
        return media
        
        
    def getMediaCompositions(self):
        media  = {"Composition": []}
        tables = self.bsdata.findAll("table")
        for table in tables:
            trs = table.findAll("tr")

            header  = trs[0]
            ths     = header.findAll("th")
            headers = [x.text.strip() for x in ths]
            if len(headers) == 0:
                continue
            for tr in trs[1:]:
                tds  = tr.findAll("td")
                vals = [td.text.strip() for td in tds]
                if len(vals) == len(headers):
                    albumData = dict(zip(headers,vals))

                    url   = None
                    year  = albumData.get('Year')
                    album = albumData.get('Title')
                    
                    if album is None:
                        continue

                    mediaType = "Composition"
                    for k,v in albumData.items():
                        if k.find("Genre") != -1:
                            mediaType = v

                    m = md5()
                    if year is not None:
                        m.update(year.encode('utf-8'))
                    if album is not None:
                        m.update(album.encode('utf-8'))
                    code = str(int(m.hexdigest(), 16) % int(1e5))

                    amdc = artistDBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=None, code=code, year=year)
                    if media.get(mediaType) is None:
                        media[mediaType] = []
                    media[mediaType].append(amdc)
                    
        return media
            
                
    def getMedia(self, url):
        amc  = artistDBMediaClass()
        name = "Albums"
        if url is None:
            name = "Unknown"
        else:
            if url.find("/credits") != -1:
                name = "Credits"
            if url.find("/songs") != -1:
                name = "Songs"
            if url.find("/compositions") != -1:
                name = "Compositions"
        amc.media[name] = []

        tables = self.bsdata.findAll("table")
        for table in tables:
            trs = table.findAll("tr")

            header  = trs[0]
            ths     = header.findAll("th")
            headers = [x.text.strip() for x in ths]
            if len(headers) == 0:
                continue

            for tr in trs[1:]:
                tds = tr.findAll("td")
                
                ## Name
                key = "Name"
                try:
                    if len(headers[1]) == 0:
                        idx = 1
                        mediaType = tds[idx].text.strip()
                        if len(mediaType) == 0:
                            mediaType = name
                    else:
                        mediaType = name
                except:
                    #print("Error getting key: {0} from AllMusic media".format(key))
                    break

                ## Year
                key  = "Year"
                try:
                    idx  = headers.index(key)
                    year = tds[idx].text.strip()
                except:
                    #print("Error getting key: {0} from AllMusic media".format(key))
                    continue

                ## Title
                key   = "Album"
                try:
                    idx   = headers.index(key)
                    ref   = tds[idx].findAll("a")
                except:
                    #print("Error getting key: {0} from AllMusic media".format(key))
                    continue
                    
                try:
                    refdata = ref[0]
                    url     = refdata.attrs['href']
                    album   = refdata.text.strip()
                    
                    data = url.split("/")[-1]
                    pos  = data.rfind("-")
                    discIDurl = data[(pos+3):]       
                    discID = discIDurl.split("/")[0]

                    try:
                        int(discID)
                        code = discID
                    except:
                        code = None
                except:
                    url  = None
                    code = None
                    continue

                amdc = artistDBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=None, code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)

                
        compMedia = self.getMediaCompositions()
        for mediaType,mediaTypeData in compMedia.items():
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType] += mediaTypeData
            

        songMedia = self.getMediaSongs()
        for mediaType,mediaTypeData in songMedia.items():
            if amc.media.get(mediaType) is None:
                amc.media[mediaType] = []
            amc.media[mediaType] += mediaTypeData
                
        return amc
    
    

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
        
        
        amcc.err = "No Counts"
        return amcc
        
        results = self.bsdata.findAll("ul", {"class": "facets_nav"})
        if results is None or len(results) == 0:
            amcc.err = "No Counts"
            return amcc
            
        for result in results:
            for li in result.findAll("li"):
                ref = li.find("a")
                if ref:
                    attrs = ref.attrs
                    span = ref.find("span", {"class": "facet_count"})
                    count = None
                    if span:
                        count = span.text
                        credittype    = attrs.get("data-credit-type")
                        creditsubtype = attrs.get("data-credit-subtype")
                        if credittype and creditsubtype:
                            if amcc.counts.get(credittype) == None:
                                amcc.counts[credittype] = {}
                            if amcc.counts[credittype].get(creditsubtype) == None:
                                try:
                                    amcc.counts[credittype][creditsubtype] = int(count)
                                except:
                                    amcc.counts[credittype][creditsubtype] = count
                                    amcc.err = "Non Int"

        return amcc