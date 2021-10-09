from artistDBBase import artistDBBase, artistDBDataClass
from artistDBBase import artistDBNameClass, artistDBMetaClass, artistDBIDClass, artistDBURLClass, artistDBPageClass
from artistDBBase import artistDBProfileClass, artistDBMediaClass, artistDBMediaAlbumClass
from artistDBBase import artistDBMediaDataClass, artistDBMediaCountsClass, artistDBFileInfoClass
from artistDBBase import artistDBTextClass, artistDBLinkClass
from strUtils import fixName

from webUtils import removeTag, getHTML
from dbUtils import utilsLastFM

import json
from copy import deepcopy
from hashlib import md5


class artistLastFM(artistDBBase):
    def __init__(self, debug=False):
        super().__init__(debug)
        self.dutils = utilsLastFM()
        self.debug  = False
        
        
    ##############################################################################################################################
    ## Parse Data
    ##############################################################################################################################
    def getData(self, inputdata):
        self.getDataBase(inputdata)
        self.checkData()
        
        artist      = self.getName()
        meta        = self.getMeta()
        url         = self.getURL()
        ID          = self.getID(url.url)
        pages       = self.getPages()
        profile     = self.getProfile()        
        media       = self.getMedia(artist)
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
        try:
            artistdiv  = self.bsdata.find("script", {"id": 'initial-tealium-data'})
            artistdata = artistdiv.attrs['data-tealium-data']
        except:
            artistdata = None
            
        if artistdata is None:
            try:
                artistdiv  = self.bsdata.find("div", {"id": "tlmdata"})
                artistdata = artistdiv.attrs['data-tealium-data']
            except:
                anc = artistDBNameClass(name=None, err = "NoTealiumData")

        
        try:
            artistvals = json.loads(artistdata)
            artist     = artistvals["musicArtistName"]
        except:
            anc = artistDBNameClass(name=None, err="NoArtistName")
            return anc


        anc = artistDBNameClass(name=artist, err=None)
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
        metalink = self.bsdata.find("meta", {"property": "og:url"})
        if metalink is None:
            auc = artistDBURLClass(err="NoLink")
            return auc
        
        try:
            url = metalink.attrs["content"]
        except:
            auc = artistDBURLClass(err="NoContent")
            return auc

        auc = artistDBURLClass(url=url)
        return auc

    

    ##############################################################################################################################
    ## Artist ID
    ##############################################################################################################################
    def getID(self, url):        
        artistID = self.dutils.getArtistID(url, debug=False)
        aic = artistDBIDClass(ID=artistID)
        return aic


    
    ##############################################################################################################################
    ## Artist Pages
    ##############################################################################################################################
    def getPages(self):
        pageData = self.bsdata.find("ul", {"class": "pagination-list"})
        if pageData is None:
            err = "pagination-list"
            apc = artistDBPageClass(err=err)
            return apc
        
        lis = pageData.findAll("li", {"class": "pagination-page"})
        ppp = 20

        if len(lis) > 1:
            lastPage = self.getNamesAndURLs(lis[-1])
            try:
                tot = lastPage[0].name
            except:
                tot = None
                #raise ValueError("Error getting last page from {0}".format(lastPage))
                
            try:
                tot = int(tot)
                apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=False, more=True)
            except:
                tot = 1
                apc   = artistDBPageClass(ppp=ppp, tot=tot, redo=False, more=False)

        else:
            tot = 1
        
        return apc
    
    

    ##############################################################################################################################
    ## Artist Variations
    ##############################################################################################################################
    def getProfile(self):  
        generalData = {}
        
        ##
        ## General
        ##
        metadata = self.bsdata.find("div", {"class": "metadata-and-wiki-row"})
        if metadata is not None:
            dls = metadata.findAll("dl")
            for dl in dls:
                dts = [dt.text for dt in dl.findAll("dt")]    
                dds = dl.findAll("dd")
                attrKeys = dts
                attrVals = []
                for dd in dds:
                    refs    = dd.findAll("a")
                    attrVals.append([artistDBTextClass(dd)] if len(refs) == 0 else [artistDBLinkClass(ref) for ref in refs])
                dlData = dict(zip(attrKeys,attrVals))
                generalData["Metadata"] = dlData


        wikicolumns = self.bsdata.findAll("div", {"class": "wiki-column"})
        for wikicolumn in wikicolumns:
            wikiblocks = wikicolumn.findAll("div", {"class": "wiki-block"})
            for wikiblock in wikiblocks:
                refs  = wikiblock.findAll("a")
                links = [artistDBLinkClass(ref) for ref in refs] if (isinstance(refs, list) and len(refs) > 0) else None
                for ref in refs:
                    removeTag(wikiblock, ref)
                text  = artistDBTextClass(wikiblock)
                if generalData.get("Wiki") is None:
                    generalData["Wiki"] = {"Text": [], "Refs": []}
                generalData["Wiki"]["Text"].append(text)
                for ref in refs:
                    generalData["Wiki"]["Refs"] += links    
        if generalData.get("Wiki") is not None:
            keep = {(ref.href,ref.text): ref for ref in generalData["Wiki"]["Refs"]}
            generalData["Wiki"]["Refs"] = list(keep.values())


        similarData = self.bsdata.find("ol", {"class": "catalogue-overview-similar-artists-full-width"})
        similarData = self.bsdata.find("section", {"class": "artist-similar-sidebar"}) if similarData is None else similarData
        lis  = similarData.findAll("li") if similarData is not None else None
        refs = [li.find("a", {"class": "link-block-target"}) for li in lis] if lis is not None else None
        similarArtists = [artistDBLinkClass(ref) for ref in refs] if (isinstance(refs, list) and len(refs) > 0) else None
        extraData = similarArtists
        

        ##
        ## Tags
        ##
        tags = self.bsdata.find("section", {"class": "catalogue-tags"})
        refs = tags.findAll("a") if tags is not None else None
        tagsData = [artistDBLinkClass(ref) for ref in refs] if (isinstance(refs, list) and len(refs) > 0) else None


        ##
        ## External
        ##
        external = self.bsdata.find("section", {"class": "external-links-section"})
        refs = external.findAll("a") if external is not None else None
        externalData = [artistDBLinkClass(ref) for ref in refs] if (isinstance(refs, list) and len(refs) > 0) else None
        
        generalData = generalData if len(generalData) > 0 else None
        
        apc = artistDBProfileClass(general=generalData, tags=tagsData, extra=extraData, external=externalData)
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
    
    
    def getMedia(self, artist):
        amc  = artistDBMediaClass()
        name = "Albums"
        amc.media[name] = []
        
        mediaType = "Albums"

        albumsection = self.bsdata.find("section", {"id": "artist-albums-section"})
        if albumsection is None:
            if self.debug:
                print("\t\tNo Album Section!")
            amc.media[mediaType] = []
            return amc

            
            
            raise ValueError("Cannot find album section!")
            
        
            
        ols = albumsection.findAll("ol", {"class": "buffer-standard"}) # resource-list--release-list resource-list--release-list--with-20"})
        if self.debug:
            print("\t\tFound {0} Resource Lists".format(len(ols)))
        for ol in ols:
            lis = ol.findAll("li", {"class": "resource-list--release-list-item-wrap"})
            for il, li in enumerate(lis):
                h3 = li.find("h3", {"class": "resource-list--release-list-item-name"})
                if h3 is None:
                    if self.debug:
                        print("\t\tNo <h3> in artist list section ({0}/{1}): {2}".format(il,len(lis), li))
                    continue
                    raise ValueError("No <h3> in artist list section ({0}/{1}): {2}".format(il,len(lis), li))
                linkdata = self.getNamesAndURLs(h3)
                if len(linkdata) == 0:
                    continue
                #print(linkdata[0].get())
                
                ## Name
                album = linkdata[0].name

                #amdc = artistDBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=None, code=code, year=year)

                ## URL
                url = linkdata[0].url
                
                ## Code
                code = self.dutils.getArtistID(album)
                
                ## Year
                year = None
                codedatas = li.findAll("p", {"class", "resource-list--release-list-item-aux-text"})
                if len(codedatas) == 2:
                    codedata = codedatas[1].text
                    vals     = [x.strip() for x in codedata.split("\n")]
                    if len(vals) == 5:
                        try:
                            year = vals[2][:-2]
                            year = year.split()[-1]
                            year = int(year)
                        except:
                            year = None
                

                amdc = artistDBMediaDataClass(album=album, url=url, aclass=None, aformat=None, artist=[artist.name], code=code, year=year)
                if amc.media.get(mediaType) is None:
                    amc.media[mediaType] = []
                amc.media[mediaType].append(amdc)
                if self.debug:
                    print("\t\tAdding Media ({0} -- {1})".format(album, url))

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