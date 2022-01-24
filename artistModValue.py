from hashlib import md5

class artistModValue:
    def __init__(self):
        self.maxModValue = 100

    def getModVal(self, artistID):
        if artistID is None:
            return None
        
        if isinstance(artistID, str):
            if artistID.isdigit():
                modValue = int(artistID) % self.maxModValue
            else:
                m = md5()
                m.update(artistID.encode('utf-8'))
                hashval = m.hexdigest()
                iHash = int(hashval, 16)
                modValue = iHash % self.maxModValue
        elif isinstance(artistID, int):
            modValue = artistID % self.maxModValue
        else:
            raise ValueError("Can not get mod value for [{0}]".format(artistID))

        return modValue