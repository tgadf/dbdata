from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from strUtils import fixName
from dbUtils import utilsDiscogs


class artistDiscogs(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsDiscogs()
        
        
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
        result1 = self.bsdata.find("h1", {'class':'hide_desktop'})
        result2 = self.bsdata.find("h1", {'class':'hide_mobile'})
        if result1 and not result2:
            result = result1
        elif result2 and not result1:
            result = result2
        elif result1 and result2:
            result = result1
        else:        
            anc = artistDBNameClass(err=True)
            return anc

        if result:
            artist = result.text
            if len(artist) > 0:
                artist = fixName(artist)
                anc = artistDBNameClass(name=artist, err=None)
            else:
                result = self.bsdata.find("script", {"id": "artist_schema"})
                if result is None:
                    anc = artistDBNameClass(name=artist, err="Fix")
                else:
                    try:
                        artist = fixName(json.loads(result.text)["name"])
                        anc = artistDBNameClass(name=artist, err=None)
                    except:
                        anc = artistDBNameClass(name=artist, err="JSON")
        else:
            anc = artistDBNameClass(err="NoH1")

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
            url = url.replace("https://www.discogs.com", "")
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
        discID   = self.dutils.getArtistID(suburl.url)
        aic = artistDBIDClass(ID=discID)
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        from numpy import ceil
        bsdata = self.bsdata


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
        result = self.bsdata.find("div", {"class": "profile"})
        heads = result.findAll("div", {"class": "head"})
        content = result.findAll("div", {"class": "content"})
        profileData = dict(zip(heads, content)) if len(heads) == len(content) else {}
        generalData = {}
        for head,content in profileData.items():
            key  = head.text[:-1] if isinstance(head.text, str) else None
            refs = content.findAll("a")
            val  = [artistDBTextClass(content)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs]
            generalData[key] = val  
            
        apc = artistDBProfileClass(general=generalData)
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
        amc = artistDBMediaClass()
        
        table = self.bsdata.find("table", {"id": "artist"})
        if table == None:
            amc.err="NoMedia"
            return amc

        name  = None
        for tr in table.findAll("tr"):
            h3 = tr.find("h3")
            if h3:
                name = h3.text
                amc.media[name] = []
                continue


            # Album, Class, Format
            result = tr.find("td", {"class": "title"})
            album  = None
            url    = None
            albumformat = name
            if result:
                retval      = self.getMediaAlbum(result)
                album       = fixName(retval.album)
                url         = retval.url
                albumformat = retval.aformat

            if album == None:
                continue

            # Code
            code = tr.attrs.get("data-object-id")

            # AlbumClass
            albumclass = tr.attrs.get("data-object-type")

            # AlbumURL
            result  = tr.find("td", {"class": "artist"})
            artists = None
            if result:
                artists = self.getNamesAndURLs(result)

            # Year
            result = tr.find("td", {"class": "year"})
            year   = None
            if result:
                year = result.text

            if name is None:
                name = "Albums"
                amc.media[name] = []
            amdc = artistDBMediaDataClass(album=album, url=url, aclass=albumclass, aformat=albumformat, artist=artists, code=code, year=year)
            amc.media[name].append(amdc)
            #if debug: print "  Found album:",album,"of type:",name


        if False:
            newMedia = {}
            for name,v in media.items():
                newMedia[name] = {}
                for item in v:
                    code = item['Code']
                    del item['Code']
                    newMedia[name][code] = item

            media = newMedia

        return amc
    
    

    ##############################################################################################################################
    ## Artist Media Counts
    ##############################################################################################################################
    def getMediaCounts(self, media):
        amcc = artistDBMediaCountsClass()
        
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