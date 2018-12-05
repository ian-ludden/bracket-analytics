#!/usr/bin/env python

import csv
import sys
import numpy as np

for year in range(2013, 2020):
	print(year)

	params = np.zeros((16,))

	filename = 'bradleyTerry/params-{0}.csv'.format(year)

	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)

		for row in reader:
			if len(row) > 1:
				seedNumStr = str(row[0])
				if len(seedNumStr) > 0 and seedNumStr[0] == "s":
					seedNum = int(seedNumStr[1:])
					params[seedNum - 1] = row[1]

	for s1 in range(1, 9):
		s2 = 17 - s1
		p1 = params[s1 - 1]
		p2 = params[s2 - 1]
		if p2 == 0:
			alphaVal = 2
		elif p1 == 0:
			alphaVal = -2
		else:
			alphaVal = (np.log(p1) - np.log(p2)) / np.log(s2 * 1.0 / s1)
		print("{0}v{1},{2:5.3f}".format(s1, s2, alphaVal))

	print(",,")
	print(",,")