#!/usr/bin/env python
import csv
import matplotlib.pyplot as plt
import numpy as np
import sys

def getModelProportions(filename, year, modelName):
	with open(filename, 'rb') as file:
		reader = csv.reader(file)

		foundYear = False
		foundModel = False
		proportions = np.zeros((16,))

		for row in reader:
			if len(row) < 1:
				continue
			if row[0] == str(year):
				foundYear = True
				continue

			if foundYear:
				if modelName in str(row[0]):
					foundModel = True
					foundYear = False
					continue

			if foundModel:
				if "Seed" not in str(row[0]):
					seedNum = int(row[0])
					proportions[seedNum - 1] = float(row[1])
				
					if seedNum == 16:
						break
	return proportions


year = int(sys.argv[1]) # 2013 to 2018
modelIndex = int(sys.argv[2]) # 0 to 4

powerModels = ['model21', 'model23', 'model25', 'model27', 'model31']
btModels = ['bradley-terry-F4_1', 'bradley-terry-F4_2', 'bradley-terry-E8', 'bradley-terry-NCG', 'bradley-terry-power']
names = ['F4_A', 'F4_B', 'E8', 'NCG', 'Standard']

seedNums = np.arange(1, 17, 1)


pModel = powerModels[modelIndex]
btModel = btModels[modelIndex]
name = names[modelIndex]

roundTitle = 'Final Four'
title = '{0} {2} PMF: {1}-BT vs. {1}-Power'.format(year, name, roundTitle)

pFilename = 'f4SeedDistributions_Paper.csv'
pProportions = getModelProportions(pFilename, year, pModel)

btFilename = 'f4SeedDistributions_BT.csv'
btProportions = getModelProportions(btFilename, year, btModel)

fig = plt.figure()
bar_width=0.45

plt.bar(seedNums, pProportions, bar_width, label='{}-Power'.format(name))
plt.bar(seedNums + bar_width, btProportions, bar_width, label='{}-BT'.format(name))

plt.title(title)
plt.xlabel('Seed')
plt.xticks(seedNums + bar_width / 2.0, seedNums)
plt.ylabel('{0} Proportion'.format(roundTitle))
plt.legend(loc='best')
plt.show()