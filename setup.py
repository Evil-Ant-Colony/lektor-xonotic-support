# Copyright (c) 2018 Sebastian Schmidt
# MIT License (see License)

from setuptools import setup

setup(
    name='lektor-xonotic-support',
    version='0.1',
    author='Sebastian Schmidt',
    author_email='schro.sb@gmail.com',
    license='MIT',
    py_modules=['lektor_xonotic_mapinfo'],
    entry_points={
        'lektor.plugins': [
            'xonotic-support = lektor_xonotic_support:XonoticSupportPlugin',
        ]
    },
    install_requires=["Pillow",]
)
