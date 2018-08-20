Simple s3 mysql-backup scripts
========================

Features
--------

- Dump specified MySQL databases
- Tar.gz-iping dumped files
- Upload them to s3 bucket

Installation
------------

`pip install django-mysql-s3-backuper`

Configuration
-------------

Add this to your django settings.py file:

```
S3_BACKUPER = {
    'db': [
        {
            'host': 'localhost',
            'port': '3306',
            'name': 'top_secret',
            'user': 'top_secret',
            'password': 'top_secret',
            'exclude': ['table1', 'table2'],
            'prefix': 'foo'  # Optional prefix if you are dumping databases with same name.
        }
    ],
    'mysql': {
        'mysqldump': '/usr/bin/mysqldump'  # Path to your mysqldump.
    },
    'aws': {
        'access_key_id': 'top_secret',  # Secure credentials from your AWS account.
        'secret_access_key': 'top_secret',
        'bucket': 'top_secret'  # Bucket for storage.
    }
}
```