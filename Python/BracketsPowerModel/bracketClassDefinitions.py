#!/usr/bin/env python
import json
import os.path
import sys

# Defines a class that represents a bracket for a given year
class Bracket:
	def __init__(self, year, regions, finalfour, fullvector):
		self.year = int(year)
		self.regions = regions
		self.finalFour = finalfour
		self.fullVector = fullvector

	def jsonDefault(object):
		return object.__dict__

	def __str__(self):
		return '{self.year} = {self.fullVector}'.format(self=self)


# Defines a simplified bracket representation used for brackets
# generated by the power model.
class SimpleBracket:
	def __init__(self, vector, scores, correctPicks=-1, alphaValues=[]):
		self.vector = vector
		self.scores = scores
		self.correctPicks = correctPicks
		self.alphaValues = alphaValues

	def jsonDefault(object):
		return object.__dict__

	def __str__(self):
		return 'Bracket: {self.vector}\nScores: {self.scores}\n{self.correctPicks} correct picks'.format(self=self)


# Defines a class that represents one of the four regions in a bracket
class Region:
	def __init__(self, name, vector):
		self.name = name
		self.vector = vector

	def __str__(self):
		return '{self.name}: {self.vector}'.format(self=self)

# This function builds a Bracket object from the JSON file with the given name.
def buildBracket(filename):
	if not os.path.isfile(filename):
		print 'File \'%s\' not found.', (filename)
		return []

	with open(filename, 'r') as bracketJsonFile:
		jsonData = bracketJsonFile.read().replace('\n', '')

	jsonToPython = json.loads(jsonData)
	bracketData = jsonToPython['bracket']

	return buildBracketFromJson(bracketData)

# This function builds a Bracket object from a dictionary created from its JSON.
def buildBracketFromJson(bracketDict):
	regionsData = bracketDict['regions']

	regions = []
	for region in regionsData:
		regions.append(Region(region['name'], region['vector']))

	return Bracket(bracketDict['year'], regions, bracketDict['finalfour'], bracketDict['fullvector'])


# ################################################################################
# # This script loads a JSON file, builds a Bracket object for it,               
# # and then makes a copy of the original JSON file using json.dumps().          
# ################################################################################
# year = int(sys.argv[1])

# filename = str(year) + '.json'
# newFilename = str(year) + '_COPY.json'



# print str(bracket)
# print ''

# for region in bracket.regions:
# 	print str(region)
# print ''

# bracketJsonFile = open(newFilename, 'w')
# fileContent = json.dumps(jsonToPython)
# # fileContent = """\
# # {
# # 	"bracket": {
# # 		"year": "%s",
# # 		"regions": [
# # 			{"name": "%s", "vector": "%s"},
# # 			{"name": "%s", "vector": "%s"},
# # 			{"name": "%s", "vector": "%s"},
# # 			{"name": "%s", "vector": "%s"}
# # 		],
# # 		"finalfour": "%s",
# # 		"fullvector": "%s"
# # 	}
# # }
# # """ % (str(year), regionNames[0], regionVectors[0], regionNames[1], regionVectors[1], regionNames[2], regionVectors[2], regionNames[3], regionVectors[3], finalFour, fullVector)
# bracketJsonFile.write(fileContent)
# bracketJsonFile.close()
