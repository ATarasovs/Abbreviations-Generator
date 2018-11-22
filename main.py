# Import libraries
import re
import os
import sys

# Initialize global variables that will be used in functions
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

# The main function will get the input from the user with the
# name of the file that will be used to create abbreviations.
# Files will be read line by line and split into appropriate.
# createValuesDictionary(), createAllowedAbbreviationsDict(),
# getLetterPositionList(), getAbbreviationScores() and
# writeResultsToFile() functions are called.
def main():

    # Get input from the user - the name of the text file
    wordsFileName = input("Please provide the name of the file without extension: ")

    # Open files with words and values for each letter
    wordsFile = open(wordsFileName + ".txt", "r")
    valuesFile = open("values.txt", "r")

    if wordsFile.mode == 'r' and valuesFile.mode == 'r':  # Check if both files were opened correctly
        wordsList = wordsFile.read().strip().split("\n")  # split words file by new line and remove last empty line
        valuesList = valuesFile.read().strip().split("\n") # split values file by new line and remove last empty line

        # function to create the dictionary of values
        valuesDict = createValuesDictionary(valuesList)

        # function to create the dictionary of allowed abbreviations
        allowedAbbreviationsDict = createAllowedAbbreviationsDict(wordsList)

        # function to get the list of letter positions
        letterPositionList = getLetterPositionList(allowedAbbreviationsDict)

        # function to get the dictionary of abbreviations scores
        scoreResultsDict = getAbbreviationScores(allowedAbbreviationsDict, wordsList, valuesDict, letterPositionList)

        # function to create the file with words and abrreviations
        writeResultsToFile(scoreResultsDict, wordsFileName)

    # Close files
    wordsFile.close()
    valuesFile.close()

# The createValuesDictionary function creates a dictionary of letters and its scores.
def createValuesDictionary(valuesList):

    for item in valuesList:  # for each item in the list of values
        letter = item[0:1]  # letter is the first symbol of the item
        score = item[2::]  # score is the third symbol of the item
        valuesDict.update({letter: score})

    return valuesDict  # return the dictionary of values

# The createAllowedAbbreviationsDict function creates a dictionary of allowed
# abbreviations for each word
def createAllowedAbbreviationsDict(wordsList):

    # Format words by looping through each word in the wordsList
    for word in wordsList:
        formattedWords.append(re.sub(r'[^\w]', '', word).upper())
        tempWordsList.append(re.sub("-", " ", word))
    wordsList = tempWordsList

    count = 0

    # Create all possible abbreviations for each word and add to abbreviationsDict
    for word in formattedWords:
        for x in range(1, len(word) - 1):
            for y in range(2, len(word)):
                if y != x & x < y:
                    abbreviations.append(word[0] + word[x] + word[y])
        abbreviationsDict.update({re.sub(r'[^\w\s]', '', wordsList[count]).upper(): list(abbreviations)})
        abbreviations.clear()
        count += 1

    # Remove all the duplicates between abbreviations of different words and add to updatedAbbreviations list
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

    # Create a dictionary with allowed abbreviation for each word
    for key, value in abbreviationsDict.items():
        wordAllowedAbbreviations = list()
        for abbreviation in value:
            if abbreviation in allowedAbbreviations:
                wordAllowedAbbreviations.append(abbreviation)
        allowedAbbreviationsDict.update({key: wordAllowedAbbreviations})

    return allowedAbbreviationsDict  # return the dictionary with allowed abbreviations for each word

# The getLetterPositionList function creates the list that stores the position
# of the letter in each word in each phrase. Each item contains a letter,
# the position of the letter according to the abbreviation requirements
# and the position of the word in the list.
def getLetterPositionList(allowedAbbreviationsDict):

    letterPositionList = list()
    for key, value in allowedAbbreviationsDict.items(): # for each item in the dictionary of allowed abbreviations
        tempLetterPositionList = list()
        splitWordsList = key.split(" ")  # create the list of words  by splitting words by space
        letterPositionInWordScore = 0
        for word in splitWordsList:  # for each word in the list of split words
            letterPositionScore = 0
            for letter in word:   # for each letter of the word
                # if letter is not the last or first letter of the word
                if len(word) - 1 > letterPositionScore or len(word) == 1:
                    if letterPositionScore <= 3: # if letter is second or third
                        tempLetterPositionList.append([letter, letterPositionScore, letterPositionInWordScore])
                    else:  # if the position of letter is more than 3
                        tempLetterPositionList.append([letter, 3, letterPositionInWordScore])
                    letterPositionScore = letterPositionScore + 1
                else:  # if letter is the last
                    if letter == "E":  # if it is "E"
                        tempLetterPositionList.append([letter, 20, letterPositionInWordScore])
                    else:  # if it is not "E"
                        tempLetterPositionList.append([letter, 5, letterPositionInWordScore])
                    letterPositionScore += 1
                letterPositionInWordScore += 1
        letterPositionList.append(tempLetterPositionList)  # append temporary list for each phrase to letterPositionList
    return letterPositionList  # return letterPositionList

# The getAbbreviationScores function creates the dictionary that contains the abbreviation and
# it's smallest score in the way of key->value.
def getAbbreviationScores(abbreviationsDict, wordsList, valuesDict, letterPositionList):
    count = 0
    scoreResultsDict = dict()
    for key, value in abbreviationsDict.items():  # for each item in the dictionary of abbreviations
        if len(value) > 1:  # if there is more than 1 abbreviation
            lowestAbbreviationsList = list()
            previousAbbreviationScore = sys.maxsize  # assign the maximum value as the score of previous abbreviation
            for abbreviation in value:  # for each abbreviation in the value
                tempUsedLettersInAbbreviationsList = list()
                abbreviationScore = 0
                abbreviationLetterCount = 0

                abbreviationLetterList = list(abbreviation) # create the list of letters for selected abbreviation
                for letterPosition in letterPositionList[count]:  # for each letter in position list

                    # if abbreviation letter is the same as letter in the position list
                    if letterPosition[0] == abbreviationLetterList[abbreviationLetterCount]:

                        # if the letter is the first or the last in the word
                        if letterPosition[1] == 0 or letterPosition[1] == 5 or letterPosition[1] == 20:
                            abbreviationScore = abbreviationScore + letterPosition[1]

                        else: # if the letter not the first and last

                            # abbreviation score = score in position list
                            abbreviationScore = abbreviationScore + letterPosition[1]
                            for letter, score in valuesDict.items():  # for each item in values dictionary
                                if letter == letterPosition[0]:  # if letter is the same as letter in the value

                                    # abbreviation score = score in position list + score from values dictionary
                                    abbreviationScore = abbreviationScore + int(score)
                        abbreviationLetterCount += 1

                        if abbreviationLetterCount == 3:  # if it is the last letter of abbreviation

                            # if the current score is lower or equal to the previous score
                            if abbreviationScore <= previousAbbreviationScore:

                                # if the current score is equal to the previous score
                                if abbreviationScore == previousAbbreviationScore:
                                    lowestAbbreviationsList.append(abbreviation)  # append abbreviation to the list

                                    # if the current score is lower than the previous score
                                if abbreviationScore < previousAbbreviationScore:
                                    lowestAbbreviationsList = list()  # remove all items from the list
                                    lowestAbbreviationsList.append(abbreviation)  # append abbreviation to the list
                                    previousAbbreviationScore = abbreviationScore
                            break
            lowestAbbreviationsSet = set(lowestAbbreviationsList)  # remove duplicates from the list
            lowestAbbreviations = ' '.join(str(s) for s in lowestAbbreviationsSet)

            # add the word with it's abbreviations to the dictionary
            scoreResultsDict[wordsList[count]] = lowestAbbreviations
        elif len(value) == 0:  # if there is no abbreviations
            scoreResultsDict.update({wordsList[count]: " "})
        else:  # if there is one abbreviation
            scoreResultsDict.update({wordsList[count]: value[0]})
        count += 1
    return scoreResultsDict  # return the dictionary with words and its abbreviations

# The writeResultsToFile function creates the text file and writes words and abbreviations
# with the smallest score to that file
def writeResultsToFile(result, wordsFileName):

    fileName = wordsFileName + "_abbrevs" + ".txt"

    if os.path.exists(fileName): # if file exists
        os.remove(fileName) # remove the file

    resultsFile = open(fileName, 'w')  # open the file

    if resultsFile.mode == 'w':  # check if the file was opened correctly
        for key, value in result.items():  # for each item in the abbreviation scores dictionary
            resultsFile.write(key)  # word
            resultsFile.write("\n")
            resultsFile.write(value)  # abbreviation(s)
            resultsFile.write("\n")

    resultsFile.close()  # close the file

# Check if the module has been imported
if __name__== "__main__":
    main() # call main function