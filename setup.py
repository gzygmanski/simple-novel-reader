from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='simple-novel-reader',
    version='0.9.212',
    description='An CLI light novel reader',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gzygmanski/simple-novel-reader',
    author='Grzegorz Zygmański',
    author_email='gzygmanski@hotmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Environment :: Console :: Curses',
    ],
    keywords='cli curses ebook epub epub-reader, light-novel-reader light-novels',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        'snr': ['parser/locale.json'],
    },
    python_requires='>=3.5, <4',
    install_requires=['beautifulsoup4', 'lxml', 'langcodes', 'PyHyphen'],
    entry_points={
            'console_scripts': [
            'snr=snr.__main__:main',
        ],
    },
)
