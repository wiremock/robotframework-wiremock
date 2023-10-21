from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

exec(open('./src/WireMockLibrary/version.py').read())

setup(name='robotframework-wiremock',
      packages=['WireMockLibrary'],
      package_dir={'': 'src'},
      version=VERSION,
      description='Robot framework library for WireMock',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Timo Yrjola',
      author_email='timo.yrjola@gmail.com',
      url='https://github.com/tyrjola/robotframework-wiremock',
      download_url='https://github.com/tyrjola/robotframework-wiremock/archive/{}.tar.gz'.format(VERSION),
      install_requires=['requests >= 2.18.4'],
      keywords='testing robotframework wiremock',
      classifiers=[])
