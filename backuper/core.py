# coding: utf-8
import datetime
import os
import zipfile
from subprocess import call

import boto3
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Backuper:
    """
    Simple and straightforward implementation for s3 mysql backups.
    """

    def __init__(self):
        self.settings = self.read_settings()
        if not self.settings:
            raise ImproperlyConfigured('To use backups, you need to add S3_BACKUPER settings')

    @staticmethod
    def read_settings():
        return getattr(settings, 'S3_BACKUPER', None)

    def get_dump_args(self, database):
        return {
            'mysql': [
                self.settings['mysql']['mysqldump'],
                '-h',
                database['host'],
                '-u',
                database['user'],
                '-p%s' % database["password"],
                database['name']
            ]
        }[database['type']]

    def make_dumps(self):
        zips = []
        dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        for database in self.settings['db']:
            sql_filename = os.path.join(self.settings['tmp_dir'], '%s.dump.sql' % database["name"])
            with open(sql_filename, 'w') as fd:
                call(
                    self.get_dump_args(database=database),
                    stdout=fd
                )

            zip_filename = os.path.join(self.settings['tmp_dir'], '%s_%s.zip' % (sql_filename, dt))
            with open(sql_filename, 'r') as fd:
                z = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
                z.writestr(sql_filename, fd.read())

            os.remove(sql_filename)
            zips.append(zip_filename)

        self.store(zips)

    def store(self, zips):
        aws = self.settings['aws']
        s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=aws['access_key_id'],
            aws_secret_access_key=aws['secret_access_key']
        )
        bucket = s3.Bucket(aws['bucket'])
        for zip_filename in zips:
            with open(zip_filename, 'rb') as fd:
                bucket.put_object(Key=zip_filename, Body=fd)
            os.remove(zip_filename)
