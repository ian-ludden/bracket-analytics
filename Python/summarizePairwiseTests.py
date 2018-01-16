#!/usr/bin/env python
import sys

# This script summarizes the pairwise independence test results.

inputFilename = str(sys.argv[1])

formatType = 'TTT'
nSD = 0 # Count of same region, direct connection
nSI = 0 # Count of same region, indirect connection
nDS = 0 # Count of diff region, same position
nDD = 0 # Count of diff region, diff position

# Max possible values of each:
totalSD = 136
totalSI = 284
totalDS = 90
totalDD = 1260

isFirst = True

with open(inputFilename, 'r') as inputFile:
	for line in inputFile:
		line = line.rstrip('\n')
		if len(line) == 0:
			break
		elif len(line) == 3:
			if not isFirst:
				print '{0} Summary:'.format(formatType)
				print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nSD, 'Same region, direct', nSD * 100.0 / totalSD)
				print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nSI, 'Same region, indirect', nSI * 100.0 / totalSI)
				print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nDS, 'Diff region, same pos', nDS * 100.0 / totalDS)
				print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nDD, 'Diff region, diff pos', nDD * 100.0 / totalDD)
				print ''

			isFirst = False
			formatType = line
			nSD = 0
			nSI = 0
			nDS = 0
			nDD = 0
			continue

		parts = line.split(' ')
		pos1 = int(parts[0])
		pos2 = int(parts[1])

		region1 = int(pos1 / 15)
		region2 = int(pos2 / 15)

		if region1 != region2:
			if (pos2 - pos1) % 15 == 0:
				nDS += 1
				# print 'DS: {0:>02d}, {1:>02d}'.format(pos1, pos2)
			else:
				nDD += 1
		else:
			# By design, pos1 < pos2, which makes
			# it easier to check whether there is a
			# direct connection

			pos1 -= region1 * 15
			pos2 -= region2 * 15

			isDirect = False
			if pos1 < 8:
				round2Game = 8 + int(pos1 / 2)
				round3Game = 12 + int(pos1 / 4)
				round4Game = 14
				isDirect = pos2 == round2Game or pos2 == round3Game or pos2 == round4Game
			elif pos1 < 12:
				round3Game = 12 + int((pos1 - 8) / 2) 
				round4Game = 14
				isDirect = pos2 == round3Game or pos2 == round4Game
			else:
				isDirect = pos2 == 14

			if isDirect:
				nSD += 1
			else:
				nSI += 1

print '{0} Summary:'.format(formatType)
print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nSD, 'Same region, direct', nSD * 100.0 / totalSD)
print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nSI, 'Same region, indirect', nSI * 100.0 / totalSI)
print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nDS, 'Diff region, same pos', nDS * 100.0 / totalDS)
print '\t{0:>4d} {1:<25} ({2:>5.2f}%)'.format(nDD, 'Diff region, diff pos', nDD * 100.0 / totalDD)
print ''