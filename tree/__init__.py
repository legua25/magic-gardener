# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from data.model import WeatherRecord, DATABASE
from argparse import ArgumentParser
from json import loads as from_json
from datetime import datetime
from time import strftime
from serial import Serial
from ml import EntropyTree
from csv import DictReader
from cPickle import dump
import logging

logging.basicConfig(filename = 'tree.log', level = logging.DEBUG)

if __name__ == '__main__':

	# Parse console arguments
	cmd = ArgumentParser('THC')
	cmd.add_argument('-T', '--train',
	    type = str,
	    help = 'Trains the decision tree using the provided data source and stores the resulting serialized tree'
	)
	cmd.add_argument('-t', '--scan_time',
	    type = int,
	    default = 600000,
	    help = 'The time lapse between each sensor scan cycle, in milliseconds (defaults to 10 min)'
	)
	cmd.add_argument('-m', '--moisture',
	    type = float,
	    help = 'The moisture threshold for the plant to irrigate, as a normalized value from 0.0 to 1.0 inclusive'
	)
	cmd.add_argument('-s', '--src',
	    type = str,
	    help = 'The TTY port from which to listen, usually in this format: /dev/<port>'
	)
	args = cmd.parse_args()

	if bool(args.train) is True:

		if bool(args.train) is False: raise ValueError('Missing source data repository')

		src = args.train
		with open(src, 'r') as f:

			# Create database tables
			DATABASE.create_tables([ WeatherRecord ])

			# Open the *.csv stream
			csv = DictReader(f)
			training = []

			for item in csv:

				# Interpret the input values as the application demands
				item['pressure'] = float(item['pressure'])
				item['temperature'] = float(item['temperature'])
				item['humidity'] = float(item['humidity'])
				item['water'] = bool(int(item['water']))

				# Generate a record entry for this item
				logging.debug('Read record: %s' % item)
				training.append(WeatherRecord.create(
					date = item['date'],
					pressure = item['pressure'],
					temperature = item['temperature'],
					humidity = item['humidity'],
					water = item['water']
				))

		# Create and serialize the tree structure
		tree = EntropyTree(training, class_attr = 'water', attrs = [
		    'humidity',
		    'temperature',
		    'pressure'
		])
		logging.debug('Finished training tree: total entries: %i' % len(training))

		# Serialize tree
		with open('tree.dat', 'wb') as f:
			dump(tree, f)

	else:

		# The standard boot mode is selected
		if bool(args.moisture) is False: raise ValueError('Missing moisture threshold value')
		elif bool(args.src) is False: raise ValueError('Missing source port value')

		# Obtain initialization arguments
		moisture = max(0.0, min(1.0, args.moisture))
		src = args.src
		time = max(0.0, args.scan_time)

		# Initialize serial port and check if terminal is active, log system initialization
		s = Serial(src, 9600)
		version = from_json(s.readline())
		logging.info('Version: %s' % version['version'])
		logging.info('Refresh interval: %i ms' % time)
		logging.info('Moisture threshold: %.2f' % moisture)

		# Deserialize current tree structure
		with open('tree.dat', 'rb') as f:

			from cPickle import load
			tree = load(f)

		# Initialize agent with tree and start loop
		from apscheduler.schedulers.blocking import BlockingScheduler

		try:

			timeout = BlockingScheduler()
			watering = False

			def agent_fn():

				global watering

				# Gather data from sensors
				s.write(b's')
				value = from_json(s.readline())

				# If the moisture is lower than the threshold, recollect the data and irrigate if needed
				if not watering:
					if value['moisture'] < moisture:

						try:

							w = WeatherRecord(
								date = strftime(b'%m/%d/%Y %H:%M:%S', datetime.now().timetuple()),
								humidity = value['humidity'],
								pressure = value['pressure'],
								temperature = value['temperature'],
								water = False
							)

							# Use classifier to attempt to predict output values
							if tree.classify(w, default = False):

								s.write(b'r')
								watering = from_json(s.readline())['active']
							else:

								# Employ sensor data to perform an action if needed
								t = datetime.strptime(w.date, b'%m/%d/%Y %H:%M:%S')

								if (6 <= t.hour < 10) or (17 <= t.hour < 19):
									if (w.humidity < 60.0) and (w.pressure < 1010.0) and (w.temperature > 15.5):

										s.write(b'r')
										watering = from_json(s.readline())['active']

						except BaseException: raise KeyboardInterrupt()
				else:

					# If we're watering, we should stop
					s.write(b'r')
					watering = from_json(s.readline())['active']

			timeout.add_job(agent_fn, 'interval', seconds = (time / 1000.0))
			timeout.start()

		except (KeyboardInterrupt, SystemExit): pass
