from setuptools import setup

setup(
  name = 'Trinitum',
  packages = ['Trinitum'], # this must be the same as the name above
  version = '0.23',
  description = 'Dead simple algorithmic cryptocurrency trading system.',
  author = 'Michael Usachenko',
  author_email = 'meu2@illinois.edu',
  url = 'https://github.com/themichaelusa/Trinitum', # use the URL to the github repo
  download_url = 'https://github.com/themichaelusa/Trinitum/archive/0.23.tar.gz', # I'll explain this in a second
  install_requires=['TA-Lib', 'numpy'],
  keywords = ['Trinitum', 'algotrading', 'cryptocurrency', 'bots'], # arbitrary keywords
  classifiers = [],
)