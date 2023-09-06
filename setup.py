from setuptools import setup
from setuptools import find_packages

pkg_location = 'stockalyzer' # src
pkg_name     = 'stockalyzer'
vfile = './'+pkg_name+'/_version.py'
vers = {}

requirements = [
    "numpy",
    "pandas",
    "matplotlib",
    "import_ipynb",
    "yfinance",
    "pandas_datareader",
    "kafka-python",
    "jupyter",
    "pyyaml",
    "backtrader",
    "pytest",
    "uvloop",
    "memory_profiler",
    "pathos",
    "ordered_set",
    "scipy",
    "statsmodels"
]

with open(vfile) as f:
   exec(f.read(), {}, vers)

with open('README.md') as f:
    long_description = f.read()

setup(name=pkg_name,
      version=vers['__version__'],
      author='J Feibelman',
      author_email='jason.feibelman@gmail.com',
      maintainer_email='jason.feibelman@gmail.com',
      py_modules=[pkg_name],
      description='Libraries for stock analysis, monitoring, and alerting',
      long_description=long_description,
      long_description_content_type='text/markdown; charset=UTF-8',
      url='http://github.com/jrfeibelman/stockalyzer',
      platforms='Cross platform (Linux, Mac OSX, Windows)',
      license="BSD-style",
      package_dir={'': pkg_location},
      packages=find_packages(where=pkg_location),
      install_requires=requirements,
      python_requires=">=3.9",
      classifiers=['Development Status :: 3 - Alpha',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Framework :: Matplotlib',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'Intended Audience :: Financial and Insurance Industry',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Office/Business :: Financial',
                   'Topic :: Office/Business :: Financial :: Investment',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   ],
      keywords=['finance','candlestick','ohlc','market','investing','technical analysis'],
      )
