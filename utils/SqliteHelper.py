#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime


class SqliteHelper(object):
    def __init__(self, db_path):
        self.db_path = db_path

        if os.path.exists(self.db_path):
            return

        print('create database')
        with self.__connect() as conn:
            c = conn.cursor()
            c.execute(
                'CREATE TABLE hunt (id integer primary key autoincrement, date timestamp,'
                ' client_ip text, hit text,is_failed boolean default false)')
            conn.commit()

    def put_all(self, client_ip, hits):
        now = datetime.utcnow()
        data = [[now, client_ip, h] for h in hits]
        with self.__connect() as conn:
            c = conn.cursor()
            c.executemany('INSERT INTO hunt(date,client_ip,hit) VALUES (?,?,?)', data)
            conn.commit()

    def pull_one(self):
        with self.__connect() as conn:
            c = conn.cursor()
            c.execute('SELECT id, date, client_ip, hit FROM hunt WHERE not is_failed ORDER BY date asc')
            return c.fetchone()

    def set_failed(self, db_id):
        with self.__connect() as conn:
            c = conn.cursor()
            c.execute('UPDATE hunt SET is_failed=? WHERE id=?', (True, db_id))
            conn.commit()

    def delete_one(self, db_id):
        with self.__connect() as conn:
            c = conn.cursor()
            c.execute('delete from hunt where id = ?', (db_id,))
            conn.commit()

    def __connect(self):
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
