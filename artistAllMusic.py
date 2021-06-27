from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from strUtils import fixName
from dbUtils import utilsAllMusic


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
        media       = self.getMedia()
        mediaCounts = self.getMediaCounts(media)
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

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
    
    
        
        ival = "/artist"
        if isinstance(suburl, artistDBURLClass):
            suburl = suburl.url
        if not isinstance(suburl, str):
            aic = artistDBIDClass(err="NotStr")            
            return aic

        pos = suburl.find(ival)
        if pos == -1:
            aic = artistDBIDClass(err="NotArtist")            
            return aic

        data = suburl[pos+len(ival)+1:]
        pos  = data.rfind("-")
        discIDurl = data[(pos+3):]       
        discID = discIDurl.split("/")[0]
        
        try:
            int(discID)
        except:
            aic = artistDBIDClass(err="NotInt")            
            return aic

        aic = artistDBIDClass(ID=discID)
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        apc   = artistDBPageClass()
        from numpy import ceil
        bsdata = self.bsdata

    
        apc   = artistDBPageClass(ppp=1, tot=1, redo=False, more=False)
        return apc
            
        pageData = bsdata.find("div", {"class": "pagination bottom"})
        if pageData is None:
            err = "pagination bottom"
            apc = artistDBPageClass(err=err)
            return apc
        else:
            x = pageData.find("strong", {"class": "pagination_total"})
            if x is None:
                err = "pagination_total"
                apc = artistDBPageClass(err=err)
                return apc
            else:
                txt = x.text
                txt = txt.strip()
                txt = txt.replace("\n", "")
                retval = [tmp.strip() for tmp in txt.split('of')]

                try:
                    ppp   = int(retval[0].split('–')[-1])
                    tot   = int(retval[1].replace(",", ""))
                except:
                    err   = "int"
                    apc   = artistDBPageClass(err=err)
                    return apc

                if ppp < 500:
                    if tot < 25 or ppp == tot:
                        apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=True, more=False)
                else:
                    if tot < 500:
                        apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=False, more=False)
                    else:
                        apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=False, more=True)
                        
                return apc
            
        return artistDBPageClass()
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):       
        from json import loads
        result = self.bsdata.find("section", {"class": "basic-info"})
        if result is None:
            try:
                content = self.bsdata.find("meta", {"name": "title"})
                searchTerm = content.attrs["content"]
                searchTerm = searchTerm.replace("Artist Search for ", "")
                searchTerm = searchTerm.replace(" | AllMusic", "")
                searchTerm = searchTerm[1:-1]
            except:
                apc = artistDBProfileClass(err="No Profile")
                return apc
            
            apc = artistDBProfileClass(search=searchTerm)
            return apc
            
            
            
           
        data   = {}
       
        members = result.find("div", {"class": "group-members"})
        if members is not None:
            data["Members"] = [item.text.strip() for item in members.findAll("span")]
        else:
            data["Members"] = []
       
        genres = result.find("div", {"class": "genre"})
        genre  = self.getNamesAndURLs(genres)
        styles = result.find("div", {"class": "styles"})
        style = self.getNamesAndURLs(styles)
        #data["Profile"] = str({'genre': genre, 'style': style})
        data["Profile"] = {'genre': genre, 'style': style}
               
        apc = artistDBProfileClass(profile=data.get("Profile"), aliases=data.get("Aliases"),
                                   members=data.get("Members"), groups=data.get("In Groups"),
                                   sites=data.get("Sites"), variations=data.get("Variations"))
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
    
    
    def getMedia(self):
        amc  = artistDBMediaClass()
        name = "Albums"
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