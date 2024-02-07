#!/usr/bin/env python
"""
   Copyright 2023 Geniza Inc.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       https://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from pathlib import Path

from setuptools import setup, find_packages
from scrapeomatic import __version__
this_directory = Path(__file__).parent

setup_args = dict(
    name='scrapeomatic',
    packages=find_packages(include=['scrapeomatic', 'scrapeomatic.*']),
    version=__version__,
    license='Apache-2.0',
    description='',
    author='Charles S. Givre',
    author_email='charles@geniza.ai',
    url='https://github.com/geniza-ai/scrapomatic',
    long_description = (this_directory / "README.md").read_text(encoding='utf-8'),
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: SQL',
        'Operating System :: OS Independent',
        'Topic :: Internet'
    ],
    install_requires=open('requirements.txt', encoding="utf-8").read().splitlines(),
)


def main() -> None:
    """
    Runs the setup of Scrape-o-matic.
    :return: Nothing
    """
    setup(**setup_args)


if __name__ == '__main__':
    main()
