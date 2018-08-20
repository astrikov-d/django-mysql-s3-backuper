# coding: utf-8
import datetime
import os
import tarfile

from subprocess import call

import boto3
from botocore.exceptions import ParamValidationError
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
        args = [
            self.settings['mysql']['mysqldump'],
            '-h',
            database['host'],
            '-u',
            database['user'],
            '-p%s' % database["password"],
            database['name']
        ]
        for table in database.get('exclude', []):
            args.extend([
                '--ignore-table',
                '%s.%s' % (database['name'], table)
            ])
        return args

    def make_dumps(self):
        archives = []
        dt = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        for database in self.settings['db']:
            sql_filename = '%s.dump.sql' % database['name']
            sql_filepath = os.path.join(self.settings['tmp_dir'], sql_filename)
            with open(sql_filepath, 'w') as fd:
                call(
                    self.get_dump_args(database=database),
                    stdout=fd
                )
            archive_filename = '%s_%s.tar.gz' % (sql_filename, dt)
            prefix = database.get('prefix')
            if prefix:
                archive_filename = '%s_%s' % (prefix, archive_filename)
            archive_filepath = os.path.join(self.settings['tmp_dir'], archive_filename)
            with tarfile.open(archive_filepath, 'w:gz') as tar:
                tar.add(sql_filepath, arcname=sql_filename)

            os.remove(sql_filepath)
            archives.append({
                'path': archive_filepath,
                'name': archive_filename
            })

        self.store(archives)

    def store(self, archives):
        aws = self.settings['aws']
        s3 = boto3.client(
            's3', 'us-east-2',
            aws_access_key_id=aws['access_key_id'],
            aws_secret_access_key=aws['secret_access_key'],
        )
        os.chdir(self.settings['tmp_dir'])
        for archive_data in archives:
            try:
                s3.upload_file(archive_data['name'], aws['bucket'], archive_data['name'])
            except ParamValidationError:
                pass
            os.remove(archive_data['path'])
