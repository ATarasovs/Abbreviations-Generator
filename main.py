# Importing libraries
import re
import os
import sys

# Initialize variables and dictionaries that will be used in functions
formattedValues = list()
formattedWords = list()
tempWordsList = list()
abbreviations = list()
updatedAbbreviations = list()
allowedAbbreviations = list()
allowedAbbreviationsList2 = list()
allowedAbbreviationsDict = dict()
abbreviationsDict = dict()
valuesDict = dict()

def main(): # add here the name of the file to input by a user

    wordsFileName = input("Please provide the name of the file without extension ")

    # Open files with words and values for each letter
    wordsFile = open(wordsFileName + ".txt", "r")
    valuesFile = open("values.txt", "r")

    if wordsFile.mode == 'r' and valuesFile.mode == 'r':  # if both files were opened correctly
        wordsList = wordsFile.read().strip().split("\n")  # split words file by new line and remove last empty line
        valuesList = valuesFile.read().strip().split("\n") # split values file by new line and remove last empty line

        valuesDict = createValuesDictionary(valuesList)  # function to create the dictionary of values
        allowedAbbreviationsDict = createAllowedAbbreviationsDict(wordsList)  # function to create the dictionary of values
        letterPositionList = getLetterPositionList(allowedAbbreviationsDict)
        scoreResultsDict = getAbbreviationScores(allowedAbbreviationsDict, wordsList, valuesDict, letterPositionList)
        writeResultsToFile(scoreResultsDict, wordsFileName)

    wordsFile.close()
    valuesFile.close()

def createValuesDictionary(valuesList):
    for item in valuesList:
        formattedValues.append(re.sub(r'[^\w]', '', item))
    for item in formattedValues:
        letter = item[0:1]
        score = item[1::]
        valuesDict.update({letter: score})
    return valuesDict

def createAllowedAbbreviationsDict(wordsList):

    # Format words
    for word in wordsList:
        formattedWords.append(re.sub(r'[^\w]', '', word).upper())
        tempWordsList.append(re.sub("-", " ", word))
    wordsList = tempWordsList
    count = 0

    # Create all possible abbreviations for each word and add to dict
    for word in formattedWords:
        for x in range(1, len(word) - 1):
            for y in range(2, len(word)):
                if y != x & x < y:
                    abbreviations.append(word[0] + word[x] + word[y])
        abbreviationsDict.update({re.sub(r'[^\w\s]', '', wordsList[count]).upper(): list(abbreviations)})  # !!!! should set be used here??????
        abbreviations.clear()
        count = count + 1

    # Remove all the duplicates between abbreviations of different words
    for key, value in abbreviationsDict.items():
        wordAbbreviationSet = set()
        for abbreviation in value:
            wordAbbreviationSet.add(abbreviation)

        for abbreviation in wordAbbreviationSet:
            updatedAbbreviations.append(abbreviation)

    # Count how many times each abbreviation appears
    abbreviationsCountDict = dict()
    for abbreviation in updatedAbbreviations:
        abbreviationsCountDict[abbreviation] = abbreviationsCountDict.get(abbreviation, 0) + 1

    # Create a list with only allowed abbreviations (abbreviations that appear only once)
    for key, value in abbreviationsCountDict.items():
        if value == 1:
            allowedAbbreviations.append(key)

        #    Create a dictionary with allowed abbreviation for each word
    for key, value in abbreviationsDict.items():
        wordAllowedAbbreviations = list()
        for abbreviation in value:
            if abbreviation in allowedAbbreviations:
                wordAllowedAbbreviations.append(abbreviation)
        allowedAbbreviationsDict.update({key: wordAllowedAbbreviations})

    return allowedAbbreviationsDict

def getLetterPositionList(allowedAbbreviationsDict):
    letterPositionList = list()
    for key, value in allowedAbbreviationsDict.items():
        tempLetterPositionList = list()
        splitWordsList = key.split(" ")
        letterPositionInWordScore = 0
        for word in splitWordsList:
            letterPositionScore = 0
            for letter in word:
                if len(word) - 1 > letterPositionScore or len(word) == 1:
                    if letterPositionScore <= 3:
                        tempLetterPositionList.append([letter, letterPositionScore, letterPositionInWordScore])
                    else:
                        tempLetterPositionList.append([letter, 3, letterPositionInWordScore])
                    letterPositionScore = letterPositionScore + 1
                else:
                    if letter == "E":
                        tempLetterPositionList.append([letter, 20, letterPositionInWordScore])  # if last letter is E attach letter position  score 20
                    else:
                        tempLetterPositionList.append([letter, 5, letterPositionInWordScore])
                    letterPositionScore += 1
                letterPositionInWordScore += 1
        letterPositionList.append(tempLetterPositionList)
    return letterPositionList

def getAbbreviationScores(abbreviationsDict, wordsList, valuesDict, letterPositionList):
    count = 0
    scoreResultsDict = dict()
    for key, value in abbreviationsDict.items(): # get key values for each word where key is word and value is abbreviation(s)
        if len(value) > 1: # if there is more than 1 abbreviation
            lowestAbbreviationsList = list()
            previousAbbreviationScore = sys.maxsize
            for abbreviation in value:  # foreach abbreviation
                tempUsedLettersInAbbreviationsList = list()
                abbreviationScore = 0
                abbreviationLetterCount = 0

                abbreviationLetterList = list(abbreviation) # create the list of letters for selected abbreviation
                for letterPosition in letterPositionList[count]:
                    if letterPosition[0] == abbreviationLetterList[abbreviationLetterCount]: # if abbreviation letter the same as letre in the position list
                        tempUsedLettersInAbbreviationsList.append(letterPosition[2])
                        if letterPosition[1] == 0 or letterPosition[1] == 5 or letterPosition[1] == 20:
                            abbreviationScore = abbreviationScore + letterPosition[1]
                        else:
                            abbreviationScore = abbreviationScore + letterPosition[1]
                            for letter, score in valuesDict.items():
                                if letter == letterPosition[0]:
                                    abbreviationScore = abbreviationScore + int(score)
                        abbreviationLetterCount += 1
                        if abbreviationLetterCount == 3: # if all three abbreviation letters were checked
                            if abbreviationScore <= previousAbbreviationScore:
                                if abbreviationScore == previousAbbreviationScore:
                                    lowestAbbreviationsList.append(abbreviation)
                                if abbreviationScore < previousAbbreviationScore:
                                    lowestAbbreviationsList = list()
                                    lowestAbbreviationsList.append(abbreviation)
                                    previousAbbreviationScore = abbreviationScore
                            break
            lowestAbbreviationsSet = set(lowestAbbreviationsList)
            lowestAbbreviations = ' '.join(str(s) for s in lowestAbbreviationsSet)
            scoreResultsDict[wordsList[count]] = lowestAbbreviations
        elif len(value) == 0:
            scoreResultsDict.update({wordsList[count]: " "})
        else:
            scoreResultsDict.update({wordsList[count]: value[0]})
        count += 1
    return scoreResultsDict

def writeResultsToFile(result, wordsFileName):
    fileName = wordsFileName + "_abbrevs" + ".txt"
    if os.path.exists(fileName): # if file exists
        os.remove(fileName) # delete

    resultsFile = open(fileName, 'w')

    if resultsFile.mode == 'w':
        for key, value in result.items():
            resultsFile.write(key)
            resultsFile.write("\n")
            resultsFile.write(value)
            resultsFile.write("\n")

    resultsFile.close()

if __name__== "__main__":
    main()