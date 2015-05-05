# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from argparse import ArgumentParser
from model import WeatherRecord, DATABASE
from csv import DictReader
from time import strptime

if __name__ == '__main__':

	# Parse console arguments
	cmd = ArgumentParser(version = '1.0')
	cmd.add_argument('file', type = str)
	args = cmd.parse_args()

	# Read the CSV and convert them into objects
	with open(args.file, 'r') as f:

		csv = DictReader(f)
		DATABASE.connect()

		for item in csv:

			# Interpret the input values as the application demands
			item['date'] = strptime(item['date'], b'%m/%d/%Y %H:%M:%S')
			item['pressure'] = float(item['pressure'])
			item['temperature'] = float(item['temperature'])
			item['humidity'] = float(item['humidity'])
			item['water'] = bool(int(item['water']))

			record = WeatherRecord.create(
				date = item['date'],
				pressure = item['pressure'],
				temperature = item['temperature'],
				humidity = item['humidity'],
				water = item['water']
			)

			print record
