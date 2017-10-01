from setuptools import setup

setup(
  name = 'Trinitum',
  packages = ['Trinitum'],
  version = '0.05',
  description = 'Dead simple algorithmic cryptocurrency trading system.',
  author = 'Michael Usachenko',
  author_email = 'meu2@illinois.edu',
  url = 'https://github.com/themichaelusa/Trinitum', 
  download_url = 'https://github.com/themichaelusa/Trinitum/archive/0.05.tar.gz', 
  install_requires=['rethinkdb','realtime_talib', 'AsyncPQ', 'pandas', 'numpy', 'gdax', 'ciso8601', 'requests', 'python-dateutil'],
  keywords = ['Trinitum', 'algotrading', 'cryptocurrency', 'bots'],
  classifiers = [],
)