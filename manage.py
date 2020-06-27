#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(repository='db', url='sqlite:///db/db.sqlite3', debug='False')
