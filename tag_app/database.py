from kivy.logger import Logger

import sqlite3
import os


class Database:

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        # not bulletproof and should be removed in future. UI should not create db file.
        db_exist = os.path.isfile(self.filename)
        folder = os.path.dirname(self.filename)

        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

        Logger.info("Database: {}, {}".format(db_exist, self.filename))

        self.connection = sqlite3.connect(self.filename)

        if not db_exist:
            self._create()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

    def _create(self):
        c = self.connection.cursor()
        c.execute('CREATE TABLE labels (product_id text, label text, start_time real, end_time real, processed integer, random_hash text)')

        self.connection.commit()

    def insert(self, product_id, start_time, end_time, label, random_hash):
        c = self.connection.cursor()
        values = (product_id, label, start_time, end_time, 0, random_hash)
        c.execute('INSERT INTO labels VALUES (?, ?, ?, ?, ?, ?)', values)

        self.connection.commit()
