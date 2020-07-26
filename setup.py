import os
import subprocess
import sys

import setuptools

setuptools.setup(
    name='moex',
    version='0.0.1',
    description='Moscow Exchange client',
    packages=setuptools.find_packages(),
    zip_safe=False,

    entry_points={
        'console_scripts': [
            'moex = moexclient.moex:main'
        ],
    }
)
