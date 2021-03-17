from dbArtistsBase import dbArtistsBase
from fileUtils import getBaseFilename
from fsUtils import isFile
from ioUtils import getFile, saveFile


#################################################################################################################################
#
# Primary
#
#################################################################################################################################
class dbArtistsPrimary(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        
        
    def parse(self, modVal, previousDays=None, force=False, debug=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force)
        dbdata   = self.getDBData(modVal, force)

        newData  = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            info     = self.artist.getData(ifile)
            #print("\t",ifile,' ==> ',info.ID.ID,' <-> ',artistID)
            if info.ID.ID != artistID:
                if self.debug is True:
                    print("Error for {0}".format(info.meta.title))
                continue
            dbdata[artistID] = info
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        return newData > 0
            
 
        
#################################################################################################################################
#
# Credit
#
#################################################################################################################################
class dbArtistsCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setCredit()
        self.dbArtists = dbArtists
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force=True)
        dbdata   = self.getDBData(modVal, force=False)
    
        newData = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            info     = self.artist.getData(ifile)
            
            currentKeys = []
            if dbdata.get(artistID) is not None:
                currentKeys = list(dbdata[artistID].media.media.keys())
            else:
                dbdata[artistID] = info
                newData += 1
                continue
            
            keys = list(set(list(info.media.media.keys()) + currentKeys))
            for k in keys:
                v = info.media.media.get(k)
                if v is None:
                    continue
                iVal  = {v2.code: v2 for v2 in v}
                dVal  = dbdata[artistID].media.media.get(k)
                if dVal is None:
                    Tretval = iVal
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
 
        
#################################################################################################################################
#
# Unofficial
#
#################################################################################################################################
class dbArtistsUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setUnofficial()
        self.dbArtists = dbArtists
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, previousDays, force=True)
        dbdata   = self.getDBData(modVal, force=False)
    
        newData = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            info     = self.artist.getData(ifile)
            
            currentKeys = []
            if dbdata.get(artistID) is not None:
                currentKeys = list(dbdata[artistID].media.media.keys())
            else:
                dbdata[artistID] = info
                newData += 1
                continue
            
            keys = list(set(list(info.media.media.keys()) + currentKeys))
            for k in keys:
                v = info.media.media.get(k)
                if v is None:
                    continue
                iVal  = {v2.code: v2 for v2 in v}
                dVal  = dbdata[artistID].media.media.get(k)
                if dVal is None:
                    Tretval = iVal
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        return newData > 0
                
                
    
#################################################################################################################################
#
# Extra
#
#################################################################################################################################
class dbArtistsExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setExtra()
        
        
    def parse(self, modVal, previousDays=None, force=False):
        newFiles = self.getArtistFiles(modVal, force=True)
        dbdata   = self.getDBData(modVal, force=False)
    
        newData = 0
        for j,ifile in enumerate(newFiles):
            if force is True:
                if j % 100 == 0:
                    print("\tProcessed {0}/{1} files.".format(j,len(newFiles)))
            artistID = getBaseFilename(ifile)
            if len(artistID.split("-")) != 2:
                print("Error with extra file: {0}".format(ifile))
                continue
                
            try:
                artistID = artistID.split("-")[0]
            except:
                print("Error with extra file: {0}".format(ifile))
                continue
                
            info     = self.artist.getData(ifile)
            
            currentKeys = []
            if dbdata.get(artistID) is not None:
                currentKeys = list(dbdata[artistID].media.media.keys())
            else:
                dbdata[artistID] = info
                newData += 1
                continue
            
            keys = list(set(list(info.media.media.keys()) + currentKeys))
            for k in keys:
                v = info.media.media.get(k)
                if v is None:
                    continue
                iVal  = {v2.code: v2 for v2 in v}
                dVal  = dbdata[artistID].media.media.get(k)
                if dVal is None:
                    Tretval = iVal
                else:
                    Tretval = {v2.code: v2 for v2 in dVal}
                    Tretval.update(iVal)
                dbdata[artistID].media.media[k] = list(Tretval.values())
            newData += 1
            
        if newData > 0:
            self.saveDBData(modVal, dbdata, newData)
            
        return newData > 0


#################################################################################################################################
#
# Parse From Raw HTML
#
#################################################################################################################################
class dbArtistsRawHTML(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
            
    def parse(self, previousDays=None, force=False):
        newFiles = self.getArtistRawHTMLFiles(previousDays, force)

        for ifile in newFiles:
            print("Parsing {0}".format(ifile))
            htmldata = getFile(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            print("  ID={0}".format(artistID))
            savename = self.dutils.getArtistSavename(artistID)
            saveFile(idata=htmldata, ifile=savename, debug=False)        
        
        #self.dbArtists.parseDownloadedFiles(previousDays=None, force=False)


#################################################################################################################################
#
# Parse From Raw Files
#
#################################################################################################################################
class dbArtistsRawFiles(dbArtistsBase):
    def __init__(self, dbArtists, datatype):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.datatype  = datatype
        self.dbArtists = dbArtists
            
    def parse(self, previousDays=None, force=False):
        newFiles = self.getArtistRawFiles(datatype=self.datatype, previousDays=previousDays, force=force)
        for ifile in newFiles:
            print("Parsing {0}".format(ifile),'\t',end='')
            htmldata = getFile(ifile)
            retval   = self.artist.getData(ifile)
            artistID = retval.ID.ID
            savename = self.dutils.getArtistSavename(artistID)
            saveFile(idata=htmldata, ifile=savename, debug=False)        
        #self.dbArtists.parseDownloadedFiles(previousDays=None, force=False)

            

#################################################################################################################################
#
# Assert Credit (Find Credit For AllMusic)
#
#################################################################################################################################
class dbArtistsAssertCredit(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        
        self.ignores={'0000443702': 'a lee', '0003182105': 'a mase', '0000920605': 'a carrillo', '0000576005': 'a jones', '0001550818': 'a p project', '0001675418': 'orazio mori', '0003137018': 'jude okoye', '0002486218': 'sim simi', '0000587118': 'scott dente phil keaggy wes king', '0003172118': 'waje', '0002204118': 'kazufumi matsunaga', '0002191318': 'stanley rosenzweig', '0000463818': 'michael guzei', '0001080218': 'r b king', '0002174618': 'ernesto halffter', '0002044118': 'abeti', '0003013918': 'aster murphy', '0001792518': 'gétatchew adamassu', '0003442018': 'emilia morton', '0003527718': 'jessa mae gabon', '0001334418': 'iwan sujono', '0002476018': 'the preachers', '0003994618': 'bak balint', '0001650818': 'eno mocchiutti', '0000640718': 'kwame hadi', '0000222718': 'joey b ellis tynetta hare', '0001516818': 'pappy tipton', '0001745218': 'sheriff roosevelt', '0001644418': 'ballet theater orchestra', '0001461018': 'bussy caine', '0001836118': 'matt king', '0000750018': 'paul f wells', '0001932618': 'jon senge', '0001962518': 'brigitte senge', '0001969618': 'fatoumata haidara', '0002150018': 'paul cut clear watson', '0002172618': 'edmund najera', '0002323318': 'tom glass', '0001054318': 'sandra akanke isidore', '0003725518': 'blk jck', '0002592718': 'baily bridges', '0003333318': 'mike de jager', '0000102218': 'the helicopters', '0001611518': 'jabu mdluli', '0000040218': 'surfers for satan', '0001971618': 'riku purtola', '0002469418': 'riku karvonen', '0001904018': 'shukuma black mambazo', '0001432018': 'wendy malan', '0001797718': 'milton mazibuko', '0003223618': 'deli mazibuko', '0000731318': 'russel kwan', '0003326018': 'plüsh', '0001068718': 'sibongiseni mbanjwa', '0001840618': 'abdoul gadir salem', '0002066818': 'muhammad gubara', '0001987118': 'saida parker', '0001216918': 'aziz goksel', '0000724918': 'zmoke da don', '0003907818': 'adam peter mills', '0002894518': 'ignatius ebayus', '0001532918': 'dick ncube trio', '0001535418': 'albert nyathi', '0001012418': 'vibes', '0003757218': 'francois luambo', '0002310618': 'chad', '0001800119': 'a dent', '0002260422': 'yu yu wang', '0000572322': 'a carlos', '0000181336': 'm dean', '0000639849': 'a mafia', '0000920463': 'a g', '0001780169': 'gt clinton', '0002207470': 'mao yuan', '0003108073': 'a muhammad jones', '0003198676': 'x x', '0003807477': 'nils', '0001581977': 'a moe', '0003288278': 'aminata kabba', '0002792878': 'a ron', '0003789984': 'antonio josé orozco ferrón', '0003071484': 'm dean', '0001390984': 'a lee', '0000588289': 'brian eno skin rachid taha', '0002153389': 'the producer', '0003221789': 'rachel coe', '0001040889': 'tshila', '0003637389': 'henry nkhata', '0003509189': 'simon magaya', '0001579889': 'machache baloyi', '0002428689': 'solomon dykes', '0001839089': 'pépé kallé with empie bakuba', '0001095389': 'chad', '0000484101': 'a ingram', '0003480802': 'stepz', '0000486205': 'a ricci', '0001403807': 'kwan nai chung', '0001030512': 'juno', '0003928914': 'nino', '0001051817': 'a wave', '0000604719': 'a ingram', '0002401322': 'a b', '0003950423': 'pop', '0003616828': 'bkon', '0001073829': 'a lee', '0002178932': 'james horner barry mann cynthia weil', '0001934736': 'a john', '0000459239': 'a b', '0002981543': 'a mango', '0003624145': 'a q', '0002710647': 'chris parker', '0000757249': 'the blue belles', '0002367353': 'a rose', '0001181856': 'jason carroll and the smooth jazz sym', '0001567159': 'the a kings', '0001924360': 'a donna', '0002437663': 'carlos centel battey', '0001402964': 'a a', '0002340867': 'm a', '0001016568': 'raffi tchamanian', '0003530869': 'x 1', '0001934770': 'pee wee', '0000920472': 'a head', '0003665473': 'jon jon', '0001094574': 'a dona', '0002219176': 'a ranieri tenti', '0001763677': 'a russo', '0002215978': 'a rossi', '0003821279': 'a ali', '0000486780': 'a rice', '0001995381': 'chris parker', '0000575083': 'a diaz', '0003350684': 'ming wang wang', '0001266785': 'a rose', '0002457187': 'hi fi', '0000041189': 'all stars', '0000500091': 'the kid', '0001039592': 'a maz', '0001093996': 'the soulquarians'}
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        newFiles = self.getArtistFiles(modVal, force=True)
        force    = False
        dbdata   = self.getDBData(modVal, force=force)

        newData  = 0
        for j,ifile in enumerate(newFiles):
            artistID = getBaseFilename(ifile)
            isKnown  = dbdata.get(artistID)
            if isKnown is None:
                info     = self.artist.getData(ifile)
                meta     = info.meta
                self.metadata[artistID] = {"title": meta.title, "url": meta.url}
                
    def getResults(self):
        return self.metadata
    
    def downloadUnknownArtistCredits(self):
        for artistID,artistIDData in self.metadata.items():
            if artistID in self.ignores.keys():
                print("Ignoring {0} artistID".format(artistID))
                continue
            savename = self.dutils.getArtistSavename(artistID, credit=True)
            if isFile(savename):
                continue
            title  = artistIDData["title"]
            title  = title.replace("Artist Search for ", "")
            title  = title.replace(" | AllMusic", "")
            artist = title[1:-1]
            if len(artist) < 1:
                continue
            self.dbArtists.searchForArtistCredit(artist=artist, artistID=artistID)
            

            
            
#################################################################################################################################
#
# Assert Extra (Find Credit For AllMusic)
#
#################################################################################################################################
class dbArtistsAssertExtra(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        dbdata   = self.getDBData(modVal, force=False)
        for artistID,artistData in dbdata.items():
            pages = artistData.pages
            if pages.pages is None:
                continue
            if pages.pages == 1:
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useURL=True):
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useName=True):
                continue
            self.metadata[artistID] = {"Name": artistData.artist.name, "URL": artistData.url.url, "Pages": list(range(2,pages.pages+1))}
                
    def getResults(self):
        return self.metadata
    
    def downloadMissingArtistExtras(self, force=False):
        print("Found {0} artists to get".format(len(self.metadata)))
        for artistID,artistPageData in self.metadata.items():
            artistName = artistPageData["Name"]
            artistURL  = artistPageData["URL"]
            pages      = artistPageData["Pages"]
            for page in pages:
                url      = self.dbArtists.getArtistURL(artistURL, page=page)
                savename = self.dutils.getArtistSavename(artistID, page=page)
                if isFile(savename) and force is False:
                    continue
                #vals = {artistURL: artistName}
                #import json
                try:
                    self.dutils.downloadArtistURL(url, savename)
                except:
                    print("Error downloading {0}".format(url))
            

            
            
#################################################################################################################################
#
# Assert Unofficial (Find Credit For Discogs)
#
#################################################################################################################################
class dbArtistsAssertUnofficial(dbArtistsBase):
    def __init__(self, dbArtists):        
        super().__init__(dbArtists)
        self.setPrimary()
        self.dbArtists = dbArtists
        self.metadata = {}
        
        
    def parse(self):
        for modVal in range(100):
            self.parseModVal(modVal)
            print("{0}\t{1}".format(modVal,len(self.metadata)))
            
    def parseModVal(self, modVal):
        dbdata   = self.getDBData(modVal, force=False)
        for artistID,artistData in dbdata.items():
            mediaCounts = artistData.mediaCounts
            if mediaCounts.counts.get("Unofficial") is None:
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useURL=True):
                continue
            if self.dbArtists.isIgnore(url=artistData.url.url, name=artistData.artist.name, useName=True):
                continue
            self.metadata[artistID] = {"Name": artistData.artist.name, "URL": artistData.url.url}
                
    def getResults(self):
        return self.metadata
    
    def downloadMissingArtistUnofficials(self, force=False):
        print("Found {0} artists to get".format(len(self.metadata)))
        for artistID,artistPageData in self.metadata.items():
            artistName = artistPageData["Name"]
            artistURL  = artistPageData["URL"]
            url        = self.dbArtists.getArtistURL(artistURL, unofficial=True)
            savename   = self.dutils.getArtistSavename(artistID, unofficial=True)
            if isFile(savename) and force is False:
                continue
            try:
                self.dutils.downloadArtistURL(url, savename)
            except:
                print("Error downloading {0}".format(url))