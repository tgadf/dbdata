from setuptools import setup
from setuptools.command.install import install
from sys import prefix
from shutil import copyfile
from pathlib import Path

class PostInstallCommand(install):
    def run(self):
        dbDataPrefix = Path(prefix).joinpath("dbdata")
        if not dbDataPrefix.exists():
            print("Install: Making Prefix Dir [{0}]".format(dbDataPrefix))
            dbDataPrefix.mkdir()
        dbIgnoreFilename = dbDataPrefix.joinpath("dbIgnoreData.yaml")
        if not dbIgnoreFilename.exists():
            print("Install: Creating Prefix Data From Local Data")
            copyfile("dbIgnoreData.yaml", dbIgnoreFilename)
    
setup(
  name = 'dbdata',
  py_modules = ['artistDBBase', 'artistIDBase', 'dbArtistsBase', 'dbBase', 'dbUtils', 'dbArtistsID', "dbArtistsMetadata",
      'dbArtistsParse', 'dbArtistsParseExtra', 'dbArtistsParseCredit', 'dbArtistsParseSong', 'dbArtistsParseUnofficial',
      'artistAllMusic', 'dbArtistsAllMusic', 
      'artistDiscogs', 'dbArtistsDiscogs', 
      'artistMusicBrainz', 'dbArtistsMusicBrainz', 
      'artistDeezer', 'dbArtistsDeezer', 
      'artistLastFM', 'dbArtistsLastFM', 
      'artistRateYourMusic', 'dbArtistsRateYourMusic',
      'artistAlbumOfTheYear', 'dbArtistsAlbumOfTheYear',
      'artistKWorbSpotify', 'dbArtistsKWorbSpotify',
      'artistKWorbiTunes',  'dbArtistsKWorbiTunes'],
  version = '0.0.1',
  #cmdclass={'install': PostInstallCommand},
  data_files = [],
  description = 'A Python Wrapper for Music DB Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/dbdata',
  keywords = ['Discogs', 'music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions', 'python-Levenshtein', 'thefuzz', 'strsimpy', 'tqdm'],
  dependency_links=['git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1', 'git+ssh://git@github.com/tgadf/dbdata.git#egg=dbdata-0.0.1', 'git+ssh://git@github.com/tgadf/multiartist.git#egg=multiartist-0.0.1', 'git+ssh://git@github.com/tgadf/musicdb.git#egg=musicdb-0.0.1']
)
 
