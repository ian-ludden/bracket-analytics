#!/usr/bin/env python
import json
import os.path
import random
import sys
from math import log
from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import SimpleBracket
from bracketClassDefinitions import buildBracketFromJson
from scoringUtils import applyRoundResults
from scoringUtils import scoreBracket
import numpy as np

# Author: 	Ian Ludden
# Date: 	01 Mar 2018
# Modified: 05 Mar 2018

# This script summarizes the experiments generated by
# runExperimentsFlexible.py for the given parameters 
# (and all ranges of alpha values (+/- K)).

numTrials = int(sys.argv[1])
isFixedFirstRoundAlphas = int(sys.argv[2]) == 1
isFixedK = int(sys.argv[3]) == 1
batchNumber = int(sys.argv[4])
minK = float(sys.argv[5])
maxK = float(sys.argv[6])
incrementK = float(sys.argv[7])

espnMin = [1590, 1520, 1760, 1630, 1650]
for year in range(2013, 2018):
	print '{0} Tournament:'.format(year)

	numKValues = int((maxK - minK) / incrementK) + 1

	maxScores = []
	countAboveEspnMin = []
	maxCorrectPicks = []
	percentile95 = []
	percentile99 = []
	proportionsAbovePF = []

	if numTrials < 50001:
		meanScores = []
		varianceScores = []
		medianScores = []

	folderNamesDict = {"10000": "10kTrials", "5000": "5kTrials", "1000000": "OneMillionTrials", "50000": "50kTrials"}

	for index in range(numKValues):
		rangeK = minK + index * incrementK
		folderName = folderNamesDict[str(numTrials)]
		inputFilename = 'Experiments/{6}/Batch{5:02d}/generatedBrackets_{0}_{1}_{2}_{3}_{4:.2f}.json'.format(numTrials, year, isFixedFirstRoundAlphas, isFixedK, rangeK, batchNumber, folderName)
		# inputFilename = 'Experiments/5kTrials/Batch{3:02d}/generatedBrackets_{0}_{1}_{2:.2f}.json'.format(numTrials, year, rangeK, batchNumber)

		with open(inputFilename, 'r') as inputFile:
			dataJson = inputFile.read().replace('\n', '')

		dataPyDict = json.loads(dataJson)
		bracketList = dataPyDict['brackets']

		brackets = []
		for bracketDict in bracketList:
			newBracket = SimpleBracket(bracketDict['bracketVector'], bracketDict['score'], bracketDict['correctPicks'])
			brackets.append(newBracket)

		nBrackets = len(brackets)
		# print 'Total No. of Brackets, {0}'.format(nBrackets)

		# Determine max scoring bracket, as well as 95/99th percentiles
		brackets.sort(key=lambda x: x.scores[0], reverse=True)
		maxScoringBracket = brackets[0]
		bracket95 = brackets[int(0.05 * nBrackets) - 1]
		bracket99 = brackets[int(0.01 * nBrackets) - 1]

		# Determine max correct picks
		brackets.sort(key=lambda x: x.correctPicks, reverse=True)
		maxCorrectPicksBracket = brackets[0]

		# Determine score of Pick Favorite model
		actualBracket = dataPyDict['actualBracket']
		actualBracketVector = [int(actualBracket[i]) for i in range(len(actualBracket))]

		pickFavoriteString = '111111111000101111111111000101111111111000101111111111000101111'
		pickFavoriteVector = [int(pickFavoriteString[i]) for i in range(63)]
		pfScores = scoreBracket(pickFavoriteVector, actualBracketVector, True)
		pfTotalScore = pfScores[0]

		bracketsAbovePickFavorite = [b for b in brackets if b.scores[0] >= pfTotalScore]
		nBracketsAbovePF = len(bracketsAbovePickFavorite)
		proportionAbovePF = nBracketsAbovePF * 1.0 / nBrackets

		bracketsInEspnLeaderboard = [b for b in brackets if b.scores[0] >= espnMin[year-2013]]
		countAboveEspnMin.append(len(bracketsInEspnLeaderboard))

		if numTrials < 50001:
			scores = [x.scores[0] for x in brackets]
			meanScore = np.mean(scores)
			varianceScore = np.var(scores)
			medianScore = np.median(scores)

		maxScores.append(maxScoringBracket.scores[0])
		maxCorrectPicks.append(maxCorrectPicksBracket.correctPicks)
		percentile95.append(bracket95.scores[0])
		percentile99.append(bracket99.scores[0])
		proportionsAbovePF.append(proportionAbovePF)

		if numTrials < 50001:
			meanScores.append(meanScore)
			varianceScores.append(varianceScore)
			medianScores.append(medianScore)

	sys.stdout.write('Max score,')
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0},'.format(maxScores[i]))
	print ''

	if numTrials < 50001:
		sys.stdout.write('Median score,')
		sys.stdout.flush()
		for i in range(numKValues):
			sys.stdout.write('{0},'.format(medianScores[i]))
		print ''

		sys.stdout.write('Mean score,')
		sys.stdout.flush()
		for i in range(numKValues):
			sys.stdout.write('{0},'.format(meanScores[i]))
		print ''

		sys.stdout.write('Var(scores),')
		sys.stdout.flush()
		for i in range(numKValues):
			sys.stdout.write('{0},'.format(varianceScores[i]))
		print ''

	sys.stdout.write('No. in ESPN top 100,')
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0},'.format(countAboveEspnMin[i]))
	print ''

	sys.stdout.write('Max correct picks,')
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0},'.format(maxCorrectPicks[i]))
	print ''

	sys.stdout.write('95th percentile,')
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0},'.format(percentile95[i]))
	print ''

	sys.stdout.write('99th percentile,')
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0},'.format(percentile99[i]))
	print ''

	sys.stdout.write('Proportion >= PF ({0}),'.format(pfTotalScore))
	sys.stdout.flush()
	for i in range(numKValues):
		sys.stdout.write('{0:10.4f},'.format(proportionsAbovePF[i]))
	print ''
	print ''
