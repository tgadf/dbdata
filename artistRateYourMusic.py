from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBURLInfo, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass
from artistDBBase import artistDBLinkClass, artistDBTagClass, artistDBTextClass
from strUtils import fixName
from dbUtils import utilsRateYourMusic
from webUtils import removeTag


class artistRateYourMusic(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dbUtils = utilsRateYourMusic()
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(artist)
        pages       = self.getPages()
        profile     = self.getProfile()
        media       = self.getMedia(artist, url)
        mediaCounts = self.getMediaCounts(media)
        
        err = [artist.err, meta.err, url.err, ID.err, pages.err, profile.err, mediaCounts.err, media.err]
        
        adc = artistDBDataClass(artist=artist, meta=meta, url=url, ID=ID, pages=pages, profile=profile, mediaCounts=mediaCounts, media=media, err=err)
        
        return adc
    
    

    ##############################################################################################################################
    ## Artist Name
    ##############################################################################################################################
    def getName(self):
        artistData = self.bsdata.find("h1", {"class": "artist_name_hdr"})
        if artistData is None:
            anc = artistDBNameClass(err="No H1")
            return anc
        
        span = artistData.find("span")
        if span is None:
            artistName = artistData.text.strip()
            artistNativeName = artistName
        else:
            artistName = span.text.strip()
            artistData = removeTag(artistData, span)
            artistNativeName = artistData.text.strip() #.replace(artistName, "").strip()
            
        if len(artistName) > 0:
            artistName = fixName(artistName)
            artistNativeName = fixName(artistNativeName)
            
            if artistName.endswith("]"):
                artistName = artistName.split(" [")[0].strip()
            if artistNativeName.endswith("]"):
                artistNativeName = artistNativeName.split(" [")[0].strip()
            
            anc = artistDBNameClass(name=artistName, native=artistNativeName, err=None)
        else:
            anc = artistDBNameClass(name=artistName, err="Fix")
        
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
        artistData = self.bsdata.find("meta", {"property": "og:url"})
        if artistData is None:
            auc = artistDBURLClass(err=True)
            return auc
        
        url = artistData.attrs["content"]
        if url.find("/artist/") == -1:
            url = None
            auc = artistDBURLClass(url=url, err="NoArtist")
        else:
            auc = artistDBURLClass(url=url)

        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, artist):
        discID = self.dbUtils.getArtistID(self.bsdata, debug=False)
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
    def getAlsoKnownAs(self, tag):
        if tag is None:
            return None
#        {'tag': <div class="info_content"><span class="rendered_text">Dwight David Turner [birth name], <a class="artist" href="/artist/dwight_david" title="[Artist864564]">Dwight David</a>, Spider Turner</span></div>}        
        span = tag.getTag().find("span", {"class": "rendered_text"})
        retval = []
        if span is not None:
            refs = span.findAll("a")
            for ref in refs:
                result = artistDBLinkClass(ref)
                retval.append(result)
                span = removeTag(span, ref)
                
            for result in span.text.split(","):
                retval.append(artistDBTextClass(result.strip()))
        else:
            refs = tag.getTag().findAll("a")
            if len(refs) == 0:
                try:
                    retval.append(artistDBTextClass(tag.getTag().strip()))
                except:
                    pass
            else:
                for ref in refs:
                    result = artistDBLinkClass(ref)
                    retval.append(result)
        return retval
    
    def getProfile(self):
        profile = self.bsdata.find("div", {"class": "artist_info"})
        headers = profile.findAll("div", {"class": "info_hdr"})
        headers = [header.text for header in headers]
        content = profile.findAll("div", {"class": "info_content"})
        profileData = dict(zip(headers, content))

        data = {}
        if True:
            if profileData.get("Formed") is not None:
                link     = profileData["Formed"].find("a", {"class": "location"})
                data["Formed"] = artistDBLinkClass(link)
                #print("Formed:",data["Formed"])

            if profileData.get("Disbanded") is not None:
                link     = profileData["Disbanded"].find("a", {"class": "location"})
                data["Disbanded"] = artistDBLinkClass(link)
                #print("Disbanded:",data["Disbanded"])

            if profileData.get("Members") is not None:
                links   = profileData["Members"].findAll("a", {"class": "artist"})
                data["Members"] = [artistDBLinkClass(member) for member in links]
                #print("Members:",data["Members"])

            if profileData.get("Also Known As"):
                tag = profileData["Also Known As"]
                data["Also Known As"] = [artistDBLinkClass(ref) for ref in tag.findAll("a")]
                #data["Also Known As"] = self.getAlsoKnownAs(artistDBTagClass(tag))
                #print("Also Known As:",data["Also Known As"])
                
            if profileData.get("Member of"):
                tag = profileData["Member of"]
                data["Member of"] = [artistDBLinkClass(ref) for ref in tag.findAll("a")]
                #print("Member of:",data["Member of"])
                
            if profileData.get("Related Artists"):
                links   = profileData["Related Artists"].findAll("a", {"class": "artist"})
                data["Related Artists"] = [artistDBLinkClass(member) for member in links]
                #print("Related Artists:",data["Related Artists"])
                
            if profileData.get("Born"):
                tag = profileData["Born"]
                if tag.find("a") is not None:
                    data["Born"] = artistDBLinkClass(tag.find("a"))
                else:
                    data["Born"] = None
                    #data["Born"] = artistDBTagClass(tag)
                #print("Born:",data["Born"])
                
            if profileData.get("Currently"):
                tag = profileData["Currently"]
                if tag.find("a") is not None:
                    data["Currently"] = artistDBLinkClass(tag.find("a"))
                else:
                    data["Currently"] = None
                    #data["Currently"] = artistDBTagClass(tag)
                #print("Currently:",data["Currently"])
                
            if profileData.get("Genres") is not None:
                links   = profileData["Genres"].findAll("a", {"class": "genre"})
                data["Genres"]  = [artistDBLinkClass(genre) for genre in links]
                #for item in data["Genres"]:
                #    print(item.get())

            if profileData.get("Notes"):
                tag   = profileData["Notes"]
                data["Notes"] = [artistDBLinkClass(ref) for ref in tag.findAll("a")]

               
        apc = artistDBProfileClass(formed=data.get("Formed"), aliases=data.get("Also Known As"),
                                   members=data.get("Members"), notes=data.get("Notes"),
                                   memberof=data.get("Member of"), relatedartists=data.get("Related Artists"),
                                   disbanded=data.get("Disbanded"),
                                   born=data.get("Born"), currently=data.get("Currently"),
                                   genres=data.get("Genres"))
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
    
    
    def getClassicalMedia(self, artist, url):
        artistWorks = self.bsdata.find("div", {"class": "section_artist_works"})
        
        media = {}
        
        uls = artistWorks.findAll("ul")
        mediaType   = None
        for i,ul in enumerate(uls):
            print(ul.attrs)
            for j,li in enumerate(ul.findAll("li")):
                print(li.attrs)
                if 'work_header' in li.attrs.get('class', []):
                    mediaType = li.text
                    continue

                ## Code
                codedata = li.find("span", {"class": "work_numbers"})
                code = None
                if codedata is not None:
                    code = codedata.text

                    
                ## Title
                mainline = li.find("span", {"class": "work_title"})
                maindata = self.getNamesAndURLs(mainline)
                try:
                    album = maindata[0].name
                except:
                    album = None

                try:
                    albumurl = maindata[0].url
                except:
                    albumurl = None


                ## Year
                yeardata = li.find("span", {"class": "work_date"})
                year = None
                if yeardata is not None:
                    year = yeardata.text

                    
                ## Artists        
                albumartists = [artistDBURLInfo(name=artist.name, url=url.url.replace("https://rateyourmusic.com", ""), ID=None)]
                
                print(mediaType,'\t',code,'\t',album,'\t',year)
                
                amdc = artistDBMediaDataClass(album=album, url=album, aclass=None, aformat=None, artist=albumartists, code=code, year=year)
                if media.get(mediaType) is None:
                    media[mediaType] = []
                media[mediaType].append(amdc)
                
        return media
    
                
    def getMedia(self, artist, url):
        amc  = artistDBMediaClass()

        mediadatas = self.bsdata.findAll("div", {"id": "discography"})
        for mediadata in mediadatas:
            h3s        = mediadata.findAll("h3", {"class": "disco_header_label"})
            categories = [x.text for x in h3s]

            sufs    = mediadata.findAll("div", {"class": "disco_showing"})
            spans   = [x.find("span") for x in sufs]
            ids     = [x.attrs['id'] for x in spans]
            letters = [x[-1] for x in ids]


            for mediaType,suffix in dict(zip(categories, letters)).items():
                categorydata = mediadata.find("div", {"id": "disco_type_{0}".format(suffix)})
                albumdatas   = categorydata.findAll("div", {"class": "disco_release"})
                for albumdata in albumdatas:
                    
                    ## Code
                    codedata = albumdata.attrs['id']
                    code     = codedata.split("_")[-1]
                    try:
                        int(code)
                    except:
                        code = None
                        
                    ## Title
                    mainline = albumdata.find("div", {"class": "disco_mainline"})
                    maindata = self.getNamesAndURLs(mainline)
                    try:
                        album = maindata[0].name
                    except:
                        album = None
                        
                    try:
                        albumurl = maindata[0].url
                    except:
                        albumurl = None


                    ## Year
                    yeardata = albumdata.find("span", {"class": "disco_year_y"})
                    if yeardata is None:
                        yeardata = albumdata.find("span", {"class": "disco_year_ymd"})
                        
                    year     = None
                    if yeardata is not None:
                        year = yeardata.text

                    ## Artists        
                    artistdata   = albumdata.findAll("span")[-1]
                    albumartists = self.getNamesAndURLs(artistdata)
                    if len(albumartists) == 0:
                        albumartists = [artistDBURLInfo(name=artist.name, url=url.url.replace("https://rateyourmusic.com", ""), ID=None)]


                    amdc = artistDBMediaDataClass(album=album, url=album, aclass=None, aformat=None, artist=albumartists, code=code, year=year)
                    if amc.media.get(mediaType) is None:
                        amc.media[mediaType] = []
                    amc.media[mediaType].append(amdc)
                    #if self.debug:
                    #    print("Found Album: [{0}/{1}] : {2}  /  {3}".format(len(amc.media[mediaType]), mediaType, code, album, album))

        
        classicalMedia = self.getClassicalMedia(artist, url)
        print(classicalMedia)
        if len(classicalMedia) > 0:
            amc.media.update(classicalMedia)

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