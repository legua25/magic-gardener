# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict, Counter
from math import log

def entropy(data, attr):

	size = len(data)
	if size <= 1: return 0.0

	freqs = defaultdict(float)
	for value in data: freqs[getattr(value, attr)] += 1.0

	if len(freqs) <= 1: return 0.0

	out = 0.0
	for value in freqs.itervalues():

		prop = (value / size)
		out -= (prop * log(prop, len(freqs)))

	return out
def info_gain(data, attr, split):

	sys_entropy = entropy(data, attr)

	child = defaultdict(list)
	for value in data: child[getattr(value, split)].append(value)

	size = float(len(data))
	def __gen__():

		for value in child.itervalues():

			prop = len(value) / size
			yield (prop * entropy(value, attr))

	return sys_entropy - sum([ value for value in __gen__() ])
def mode_value(data, attr): return Counter([ getattr(value, attr) for value in data ]).most_common(1)[0]
def best_partition(data, attrs):

	out = []
	for split in attrs:
		out.append((max([ info_gain(data, attr, split) for attr in attrs ]), split))

	return sorted(out, reverse = True)[0][1]
def split_data(data, attr):

	parts = defaultdict(list)
	for value in data: parts[getattr(value, attr)].append(value)

	return parts

class EntropyLeaf(object):

	def __init__(self, value):
		self._value = value

	@property
	def value(self): return self._value

	def classify(self, value, default = b'p'): return self._value

	def __str__(self): return str(self._value)
	def __repr__(self): return 'leaf(%s)' % self._value
class EntropyNode(object):

	def __init__(self, label):

		self._label = label
		self.children = {}

	@property
	def label(self): return self._label

	def classify(self, value, default = None):

		attr = getattr(value, self._label)

		if attr in self.children: return self.children[attr].classify(value, default = default)
		return default

	def __str__(self): return '(%s %s)' % (self._label, ' '.join(map(lambda i: '[%s: %s]' % (i[0], i[1]), self.children.iteritems())))

class EntropyTree(object):

	def __init__(self, data, attrs, class_attr):

		self._root = EntropyTree._build_nodes(data, attrs, class_attr)
		self._attrs = attrs

	@property
	def attributes(self): return self._attrs

	def classify(self, value, default = None): return self._root.classify(value, default = default)

	def __str__(self): return str(self._root)

	@staticmethod
	def _build_nodes(data, attrs, class_attr, default = None, trace = 0):

		attrs = [ attr for attr in attrs if attr != class_attr ]
		if bool(data) and bool(attrs):

			count = Counter([ getattr(value, class_attr) for value in data ])
			if len(count) == 1: return EntropyLeaf(count.most_common(1)[0][0])
			else:

				default = mode_value(data, class_attr)[0]
				best = best_partition(data, attrs)
				node = EntropyNode(best)

				# Split along best-rated attribute
				attr_values = split_data(data, best)
				remaining = [ attr for attr in attrs if attr != best ]

				print '%s Creating node for attribute %s.' % ('>' * trace, best)

				for value in attr_values:
					node.children[value] = EntropyTree._build_nodes(attr_values[value], remaining, class_attr, default = default, trace = (trace + 1))

				return node

		return EntropyLeaf(default)
