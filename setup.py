import os
import sys

from setuptools import find_packages, setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = find_packages()

setup(
    name='django-mysql-s3-backuper',
    version='0.0.1',
    description='Simple s3 backups for django projects based on MySQL',
    long_description='Simple s3 backups for django projects based on MySQL',
    author='Dmitry Astrikov',
    author_email='astrikov.d@gmail.com',
    url='http://astrikov.ru',
    packages=packages,
    include_package_data=True,
    py_modules=['backuper'],
    install_requires=[
        'Django>=2.0.0',
        'boto3==1.7.72'
    ],
    license='MIT License',
    zip_safe=False,
    keywords='django mysql s3 aws backup',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ]
)
