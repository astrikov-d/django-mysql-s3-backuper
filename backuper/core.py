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
            sql_filename = '%s.dump.sql' % database["name"]
            sql_filepath = os.path.join(self.settings['tmp_dir'], sql_filename)
            with open(sql_filepath, 'w') as fd:
                call(
                    self.get_dump_args(database=database),
                    stdout=fd
                )

            zip_filename = '%s_%s.zip' % (sql_filename, dt)
            zip_filepath = os.path.join(self.settings['tmp_dir'], zip_filename)
            with open(sql_filepath, 'r') as fd:
                z = zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED)
                z.writestr(sql_filename, fd.read())

            os.remove(sql_filepath)
            zips.append({
                'path': zip_filepath,
                'name': zip_filename
            })

        self.store(zips)

    def store(self, zips):
        aws = self.settings['aws']
        s3 = boto3.resource(
            service_name='s3',
            aws_access_key_id=aws['access_key_id'],
            aws_secret_access_key=aws['secret_access_key']
        )
        bucket = s3.Bucket(aws['bucket'])
        for zip_data in zips:
            with open(zip_data['path'], 'rb') as fd:
                bucket.put_object(Key=zip_data['name'], Body=fd)
            os.remove(zip_data['path'])
