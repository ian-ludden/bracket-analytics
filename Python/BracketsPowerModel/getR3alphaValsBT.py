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


	s1s = [1, 1,  1,  1, 2, 2,  2, 3,  3,  3, 4, 4, 5, 5, 6,  6,  7,  7,  8,  8,  9, 10, 10]
	s2s = [4, 5, 12, 13, 3, 6, 11, 7, 10, 15, 8, 9, 8, 9, 7, 10, 11, 14, 12, 13, 13, 11, 14]

	for index in range(len(s1s)):
		s1 = s1s[index]
		s2 = s2s[index]
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