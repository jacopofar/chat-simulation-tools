import re
from pathlib import Path

from setuptools import find_packages, setup


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = Path(__file__).parent / 'visualz' / '__init__.py'
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = 'Cannot find version in visualz/__init__.py'
            raise RuntimeError(msg)


install_requires = ['aiohttp',
                    'aiohttp_jinja2']


setup(name='visualz',
      version=read_version(),
      description='Chat log visualizer',
      packages=find_packages(),
      include_package_data=True,
      # necessary to export templates in the package and load them
      package_data={'visualz': ['templates/*']},
      install_requires=install_requires,
      zip_safe=False)
