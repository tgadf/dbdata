from distutils.core import setup
import setuptools
import pkg_resources
import os
import sys
from shutil import copyfile
from setuptools.command.install import install
    
setup(
  name = 'dbdata',
  py_modules = [
      'artistDBBase', 'dbArtistsBase', 'dbBase', 'dbUtils',
      'artistAllMusic', 'dbArtistsAllMusic', 
      'artistDiscogs', 'dbArtistsDiscogs', 
      'artistMusicBrainz', 'dbArtistsMusicBrainz', 
      'artistDeezer', 'dbArtistsDeezer', 
      'artistLastFM', 'dbArtistsLastFM', 
      'artistRateYourMusic', 'dbArtistsRateYourMusic',
      'artistRockCorner', 'dbArtistsRockCorner',
      'artistAlbumOfTheYear', 'dbArtistsAlbumOfTheYear',
      'artistAB', 'dbArtistsAceBootlegs', 
      'artistCL', 'dbArtistsCDandLP', 
      'artistDP', 'dbArtistsDatPiff', 
      'artistMS', 'dbArtistsMusicStack'],
  version = '0.0.1',
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
  install_requires=['utils==0.0.1', 'multiartist==0.0.1', 'musicdb==0.0.1', 'matchAlbums==0.0.1', 'jupyter_contrib_nbextensions'],
  dependency_links=['git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1', 'git+ssh://git@github.com/tgadf/multiartist.git#egg=multiartist-0.0.1', 'git+ssh://git@github.com/tgadf/musicdb.git#egg=musicdb-0.0.1']
)
 
