# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from peewee import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = SqliteDatabase(os.path.join(BASE_DIR, 'data.sqlite3'))
DATABASE.connect()

class WeatherRecord(Model):

	class Meta(object):

		database = DATABASE
		db_table = 'weather'
		order_by = [ 'date' ]

	date = DateTimeField(null = False, index = True)
	pressure = FloatField(null = False)
	temperature = FloatField(null = False)
	humidity = FloatField(null = False)
	water = BooleanField(null = False)

if __name__ == '__main__':
	DATABASE.create_tables([ WeatherRecord ])
