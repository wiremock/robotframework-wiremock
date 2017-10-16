from distutils.core import setup


setup(name='robotframework-wiremock',
      packages=['WireMockLibrary'],
      package_dir={'': 'src'},
      version='0.0.1',
      description='Robot framework library for WireMock',
      author='Timo Yrjola',
      author_email='timo.yrjola@gmail.com',
      url='https://github.com/tyrjola/robotframework-wiremock',
      download_url='https://github.com/tyrjola/robotframework-wiremock/archive/0.0.1.tar.gz',
      keywords='testing robotframework wiremock',
      classifiers=[],
      install_requires=['requests'])
