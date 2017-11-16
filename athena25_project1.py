import re

# Information regarding the story text that will be used extensively during queries.
# Default values are set here until detailed information can be obtained from files.
stopWords = []
grimmsStoriesText = []
grimmsStoriesTitles = []
grimmsStoriesStartingLines = []

# Reads stopwords from file and loads them into an array.
print('Loading stopwords...')
stopWordsFile = open('stopwords.txt', 'r')
for line in stopWordsFile:
    word = line.rstrip()
    stopWords.append(word)
stopWordsFile.close()
print(stopWords)


# Updates the last four line read.
def updateLines(aLine):
    global fourthLine
    global thirdLine
    global secondLine
    global currentLine

    fourthLine = thirdLine
    thirdLine = secondLine
    secondLine = currentLine
    currentLine = aLine


# Observes the last four lines read to see if they indicate the start of a new story.
# A new story is indicated by two blank lines, a line with only capitalLetters, and then another blank line.
def isNewStory():
    global fourthLine
    global thirdLine
    global secondLine
    global currentLine

    if fourthLine == '' and thirdLine == '' and re.findall('[^a-z0-9]', secondLine) == list(secondLine) and secondLine != '' and currentLine == '':
        return True
    else:
        return False


# Reads in the text file of The Brothers Grimm Stories line by line and saves each line into an array.
# Appends titles of stories to appropriate array in the order listed in the file.
# Uses array to store line numbers that mark the beginning or end of a story.
print('\nBuilding index...')
storyNumber = 0
lineNumber = 0
linesPastIntroduction = 0
fourthLine = None
thirdLine = None
secondLine = None
currentLine = None
haveReadIntroduction = False
grimmsStoriesFile = open('grimms.txt', 'r')
for line in grimmsStoriesFile:
    grimmsStoriesText.append(line.rstrip())
    updateLines(line.rstrip())
    lineNumber += 1
    
    if haveReadIntroduction:
        linesPastIntroduction += 1
        if isNewStory() and linesPastIntroduction > 1:
            grimmsStoriesTitles.append(secondLine)
            grimmsStoriesStartingLines.append(lineNumber)
            storyNumber += 1
            print(str(storyNumber) + ' ' + secondLine)

    if currentLine == '*****':
        grimmsStoriesStartingLines.append(lineNumber + 1)
        break
    
    if currentLine == 'THE BROTHERS GRIMM FAIRY TALES':
        haveReadIntroduction = True
grimmsStoriesFile.close()


# Takes in an array of words and filters out any words that are listed as a stopword.
def removeStopWords(searchWords):
    global stopWords

    lineNumber = 0;
    filteredSearchWords = []
    for word in searchWords:
        if word not in stopWords:
            filteredSearchWords.append(word)
            
    return filteredSearchWords


# Returns a dictionary of all the lines in a specified story that contain a certain query word.
# Dictionary keys are line numbers.
# Dictionary values are the corresponding lines that have all occurences of the query word formatted for emphasis.
def findQueryWordInStory(queryWord, story):
    global grimmsStoriesText
    global grimmsStoriesTitles
    global grimmsStoriesStartingLines

    startingLine = grimmsStoriesStartingLines[grimmsStoriesTitles.index(story)]
    endingLine = grimmsStoriesStartingLines[grimmsStoriesTitles.index(story) + 1] - 1
    matchingLines = {}
    for lineNumber in range(startingLine, endingLine):
        line = grimmsStoriesText[lineNumber - 1]
        punctuationRemovedLine = line.replace('.', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace(',', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace(';', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace('-', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace('\'', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace(':', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace('!', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace('?', ' ')
        punctuationRemovedLine = punctuationRemovedLine.replace('"', ' ')
        
        punctuation = re.search(r'[^a-zA-Z0-9 ]', punctuationRemovedLine)
        if punctuation != None:
            punctuationRemovedLine = punctuationRemovedLine.replace(punctuation.group(), ' ')
        
        
        lineWords = punctuationRemovedLine.split()
        for word in lineWords:
            word = word.lower()
            if word == queryWord.lower():
                copiedLine = punctuationRemovedLine.lower()
                formattedLine = line
                startIndex = 0
                endIndex = len(formattedLine)
                formattedWord = '**' + queryWord.upper() + '**'
                    
                while startIndex < endIndex:
                    index = copiedLine.find(word, startIndex)
                    if index == -1:
                        break
                    else:
                        previousCharIndex = index - 1
                        nextCharIndex = index + len(queryWord)
                        if previousCharIndex >= 0:
                            if nextCharIndex < len(copiedLine):
                                previousChar = formattedLine[previousCharIndex]
                                nextChar = formattedLine[nextCharIndex]
                                if previousChar.isalpha() or previousChar.isdigit() or nextChar.isalpha() or nextChar.isdigit() or nextChar == '-':
                                    startIndex = nextCharIndex
                                else:
                                    copiedLine = copiedLine[:index] + formattedWord + copiedLine[nextCharIndex:]
                                    formattedLine = formattedLine[:index] + formattedWord + formattedLine[nextCharIndex:]
                                    startIndex = index + len(formattedWord)
                                    endIndex = len(copiedLine)
                            else:
                                formattedLine = formattedLine[:index] + formattedWord
                                break
                        else:
                            nextChar = formattedLine[nextCharIndex]
                            if nextChar.isalpha() or nextChar.isdigit() or nextChar == '-':
                                startIndex = nextCharIndex
                            else:
                                copiedLine = copiedLine[:index] + formattedWord + copiedLine[nextCharIndex:]
                                formattedLine = formattedLine[:index] + formattedWord + formattedLine[nextCharIndex:]
                                startIndex = index + len(formattedWord)
                                endIndex = len(copiedLine)
                                
                matchingLines[lineNumber] = formattedLine
                   
    return matchingLines


# Returns a dictionary of all the query word that appear in a given story, as well as all the lines in that story that contain the each word.
# Dictionary keys are the given query words.
# Dictionary values are dictionaries that contain all the lines in the specified story that contain the query word key.
def findAllQueryWordsInStory(queryWords, story):
    matchingWords = {}
    for queryWord in queryWords:
        matchingLines = findQueryWordInStory(queryWord, story)
        if any(matchingLines):
            matchingWords[queryWord] = matchingLines

    return matchingWords


# Returns a dictionary of all the stories that contain at least one of the given query words.
# Dictionary keys are the story titles.
# Dictionary values are dictionaries that contain all the query words that appear in the story, which in turn contain all lines in the specified
#   story that contain the query word key.
# Called when console input is of the format "<first-word> or <final-word>"
def findAllQueryWordsInAllStories(queryWords):
    global grimmsStoriesTitles
    
    matchingStories = {}
    for story in grimmsStoriesTitles:
        matchingWords = findAllQueryWordsInStory(queryWords, story)
        if any(matchingWords):
            matchingStories[story] = matchingWords

    return matchingStories


# Returns a filtered dictionary of stories that contain all of the given words.
# Called when console input is of the format "<first-word> <second-word> ... <second-word>"
def doAndQuery(queryWords):
    matchingStories = findAllQueryWordsInAllStories(queryWords)
    filteredStories = {}
    
    for story in matchingStories:
        containsAllQueryWords = True
        for queryWord in queryWords:
            matchingLines = matchingStories[story].setdefault(queryWord, {})
            if not any(matchingLines):
                containsAllQueryWords = False
                
        if containsAllQueryWords:
            filteredStories[story] = matchingStories[story]

    return filteredStories


# Returns a filtered dictionary of stories that contain at least one of the given words.
def doOrQuery(queryWords):
    matchingStories = findAllQueryWordsInAllStories(queryWords)
    filteredStories = {}
    
    for story in matchingStories:
        containsAQueryWord = False
        for queryWord in queryWords:
            matchingLines = matchingStories[story].setdefault(queryWord, {})
            if any(matchingLines):
                containsAQueryWord = True
                break
                
        if containsAQueryWord:
            filteredStories[story] = matchingStories[story]

    return filteredStories


# Returns a filtered dictionary of stories in which a given word appears more than a certain number of times.
# Called when console input is of the format "<first-word> morethan <integer>"
def doMorethanIntegerQuery(queryWord, minimum):
    matchingStories = findAllQueryWordsInAllStories([queryWord])
    filteredStories = {}
    
    for story in matchingStories:
        matchingLines = matchingStories[story].setdefault(queryWord, {})
        queryWordAppearances = 0
        for line in matchingLines:
            queryWordAppearances += matchingLines[line].count('**' + queryWord.upper() + '**')
            
        if queryWordAppearances > minimum:
            filteredStories[story] = matchingStories[story]
                
    return filteredStories


# Returns a filtered dictionary of stories in which a given word appears more frequently than another word.
# Called when console input is of the format "<first-word> morethan <second-word>"
def doMorethanWordQuery(firstWord, secondWord):
    firstWordMatchingStories = findAllQueryWordsInAllStories([firstWord])
    secondWordMatchingStories = findAllQueryWordsInAllStories([secondWord])
    filteredStories = {}
    
    for story in firstWordMatchingStories:
        firstWordMatchingLines = firstWordMatchingStories[story][firstWord]
        firstWordAppearances = 0
        for line in firstWordMatchingLines:
            firstWordAppearances += firstWordMatchingLines[line].count('**' + firstWord.upper() + '**')
            
        secondWordMatchingLines = secondWordMatchingStories.setdefault(story, {}).setdefault(secondWord, {})
        secondWordAppearances = 0
        for line in secondWordMatchingLines:
            secondWordAppearances += secondWordMatchingLines[line].count('**' + secondWord.upper() + '**')
            
        if firstWordAppearances > secondWordAppearances:
            filteredStories[story] = firstWordMatchingStories[story]
                
    return filteredStories


# Returns a filtered dictionary of stories in which two words appear within one line of each other.
# Called when console input is of the format "<first-word> near <second-word>"
def doNearQuery(queryWords):
    firstWord = queryWords[0]
    secondWord = queryWords[1]
    firstWordMatchingStories = findAllQueryWordsInAllStories([firstWord])
    secondWordMatchingStories = findAllQueryWordsInAllStories([secondWord])
    filteredStories = {}
    
    if any(firstWordMatchingStories):
        for story in firstWordMatchingStories:
            firstWordFilteredLines = {}
            secondWordFilteredLines = {}
            firstWordMatchingLines = firstWordMatchingStories.setdefault(story, {}).setdefault(firstWord, {})
            secondWordMatchingLines = secondWordMatchingStories.setdefault(story, {}).setdefault(secondWord, {})
            
            for firstWordLine in firstWordMatchingLines:
                isNearSecondWord = False
                for secondWordLine in secondWordMatchingLines:
                    if abs(firstWordLine - secondWordLine) <= 1:
                        isNearSecondWord = True
                        break

                if isNearSecondWord:
                    firstWordFilteredLines[firstWordLine] = firstWordMatchingLines[firstWordLine]
                    
            for secondWordLine in secondWordMatchingLines:
                isNearFirstWord = False
                for firstWordLine in firstWordMatchingLines:
                    if abs(firstWordLine - secondWordLine) <= 1:
                        isNearFirstWord = True
                        break
                
                if isNearFirstWord:
                    secondWordFilteredLines[secondWordLine] = secondWordMatchingLines[secondWordLine]

            if any(firstWordFilteredLines):
                allNearLines = {}
                allNearLines[firstWord] = firstWordFilteredLines
                allNearLines[secondWord] = secondWordFilteredLines
                filteredStories[story] = allNearLines

    return filteredStories


# Prints a formatted query that had only one query word.
# The format differs from that for queries with multiple query words, as the one specified query word is not printed as a subheading.
def printSingleWordQueryResults(matchingStories, queryWord):
    global grimmsStoriesTitles

    if any(matchingStories):
        for story in grimmsStoriesTitles:
            matchingStory = matchingStories.setdefault(story, {})
            if any(matchingStory):
                print('     ' + story)
                matchingLines = matchingStory[queryWord]
                for lineNumber in sorted(matchingLines):
                    print('       ' + str(lineNumber) + ' ' + matchingLines[lineNumber])
    else:
        print('    --')


# Prints a formatted query that had multiple query words.
def printMultipleWordQueryResults(matchingStories, queryWords):
    global grimmsStoriesTitles
    
    if any(matchingStories):
        for story in grimmsStoriesTitles:
            matchingStory = matchingStories.setdefault(story, {})
            if any(matchingStory):
                print('     ' + story)
                for queryWord in queryWords:
                    print('       ' + queryWord)
                    matchingLines = matchingStory.setdefault(queryWord, {})
                    if any(matchingLines):
                        for lineNumber in sorted(matchingLines):
                            print('         ' + str(lineNumber) + ' ' + matchingLines[lineNumber])
                    else:
                        print('        --')
    else:
        print('    --')


# Performs and prints out queries until "qquit" is entered.
# Input is case-insensitive
# Prompts the user for input, then decides which type of query to perform.
# Stopwords are removed from input prior to querying.
# Formatting and printing of query results are done based on which type of query was used.
print('\n\nWelcome to the Grimms\' Fairy Tales search system!\n')
enteredLine = ''
enteredWords = ''
queryWords = ''
while enteredWords != 'qquit':
    enteredLine = input('\nPlease enter your query: ')
    enteredWords = enteredLine.split()
    
    isOrQuery = False
    isMorethanIntegerQuery = False
    isMorethanWordQuery = False
    isNearQuery = False
    if len(enteredWords) == 3:
        if enteredWords[1].lower() == 'or':
            isOrQuery = True
        elif enteredWords[1].lower() == 'morethan':
            if enteredWords[2].isdigit():
                isMorethanIntegerQuery = True
            else:
                isMorethanWordQuery = True
        elif enteredWords[1].lower() == 'near':
            isNearQuery = True
    elif len(enteredWords) == 1:
        if enteredWords[0] == 'qquit':
            break
    
    queryWords = removeStopWords(enteredWords)
    
    print('\nquery =  ' + enteredLine)
    if len(queryWords) == 0:
        print('    --')
    elif len(queryWords) == 1:
        queryWord = queryWords[0]
        matchingStories = doAndQuery(queryWords)
        printSingleWordQueryResults(matchingStories, queryWord)
    elif len(queryWords) == 2:
        matchingStories = {}
        if isOrQuery:
            matchingStories = findAllQueryWordsInAllStories(queryWords)
        elif isNearQuery:
            matchingStories = doNearQuery(queryWords)
        else:
            matchingStories = doAndQuery(queryWords)
        printMultipleWordQueryResults(matchingStories, queryWords)
    elif isMorethanIntegerQuery:
        queryWord = queryWords[0]
        minimum = int(queryWords[2])
        matchingStories = doMorethanIntegerQuery(queryWord, minimum)
        printSingleWordQueryResults(matchingStories, queryWord)
    elif isMorethanWordQuery:
        firstWord = queryWords[0]
        secondWord = queryWords[2]
        matchingStories = doMorethanWordQuery(firstWord, secondWord)
        printMultipleWordQueryResults(matchingStories, [firstWord, secondWord])
    else:
        matchingStories = doAndQuery(queryWords)
        printMultipleWordQueryResults(matchingStories, queryWords)
