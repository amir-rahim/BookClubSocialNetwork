import json
import multiprocessing
from os import remove
import pandas as pd
from pandas import DataFrame
import csv
import re
from bookinfo import BookInfo
import time
N = False

def ingestISBNSubjectsCSV(f="",t=False):
    tic = time.time()
    file_path = f
    d = {}
    i = 0
    with open(file_path,newline='') as csvfile:
        if N:
            file = [next(csvfile) for x in range(N)]
        else:
            file = csvfile
        reader = csv.reader(file, delimiter=',',quotechar='|')
        for row in reader:
            i =+ 1
            title = row[0]
            isbn = row[1]
            genres = []
            if(len(row) > 1):
                for i in range(2,len(row)):
                    r = row[i]
                    r = replaceSingleQuotes(r)
                    endQuote = "\","
                    startQuote = " \""
                    start = (re.search(startQuote, r).start(0))+2
                    end = re.search(endQuote, r).start(0)
                    subject = (r[start:end])
                    genres.append(subject)
            
            if genres:
                book = BookInfo(t=title, isbn=isbn, g=genres)
                d[title] = book
            
    toc = time.time()
    total = toc-tic
    print('Done in {:.4f} seconds'.format(total))
    return d

def replaceSingleQuotes(row):
    regexes = ["(',)","(':)","( ')","('})","({')"]
    replace = ['",','":',' "','"}','{"']
    for regex, replace in zip(regexes,replace):
        row = re.sub(regex,replace,row )
    return str(row)


def getUniqueSubjectsCount(data):
    uniqueSubjects = {}

    for book in data:
        subjects = data[book].genres
        for subject in subjects:
            if uniqueSubjects.get(subject) is None:
                uniqueSubjects[subject] = 1
            else:
                uniqueSubjects[subject] += 1
    return uniqueSubjects

def getSortedPairsByOccurence(subjects):

    sorted_keys = sorted(subjects, key = subjects.get, reverse=True)
    sortedDict = {}

    for key in sorted_keys:
        sortedDict[key] = subjects[key]
        
    #print(top10)
    return sortedDict

def wordFrequencyDict(books):
    words = {}

    for book in books:
        subjects = books[book].genres
        for subject in subjects:
            subjectLower = subject.lower()
            splitBy = "\\s|,\\s"
            removeNonLetter = "[^A-Za-z0-9]"
            subjectWords = re.split(splitBy, subjectLower)
            for word in subjectWords:
                cleaned = re.sub(removeNonLetter, "", word)
                if(len(cleaned) > 2):
                    
                    if words.get(cleaned) is None:
                        words[cleaned] = 1
                    else:
                        words[cleaned] += 1
                        
    return words

def getAboveX(words, n):
    outdict = {}
    for key in words.keys():
        val = words[key]
        if val >= n:
            outdict[key] = val
            
    return outdict

def getSubjectsBooksDictionary(sortedWords, books):
    genresBookDict = {}
    genresBookCount = {}
    i = 0
    for word in sortedWords:
        tic = time.time()
        i += 1
        if((i % 100) == 0):
            print(str(i) + "th word")
        j = 0
        for book in books:
            j +=1
            #if((j % 1000) == 0):
            #    print(str(j) + "th book in " + str(i) + "th word")
            subjects = books[book].genres
            for subject in subjects:
                subjectLower = subject.lower()
                splitBy = "\\s|,\\s"
                removeNonLetter = "[^A-Za-z0-9]"
                clean = re.sub(removeNonLetter, "", subjectLower)
                subjectWords = re.split(splitBy, clean)
                if word in subjectWords:
                    assignedBooks = genresBookDict.get(word)
                    if assignedBooks is None:
                        genresBookDict[word] = set(book)
                    else:
                        assignedBooks.add(book)
        toc = time.time()
        total = toc-tic
        print(str(i)+' in {:.4f} seconds'.format(total))
    return (genresBookDict)

def getSubjectsBooksDictionaryM(sortedWords, books):
    pool = multiprocessing.Pool()
    result = pool.map(searchBookSubjectsForWord, sortedWords)
    pool.close()
    x = {}
    pool.join()
    for d in result:
        x = {**x, **d}
        
    return x

def searchBookSubjectsForWord(word):
    genresBookDict = {}
    for book in books:
            subjects = books[book].genres
            for subject in subjects:
                subjectLower = subject.lower()
                splitBy = "\\s|,\\s"
                removeNonLetter = "[^A-Za-z0-9]"
                clean = re.sub(removeNonLetter, "", subjectLower)
                subjectWords = re.split(splitBy, clean)
                if word in subjectWords:
                    assignedBooks = genresBookDict.get(word)
                    if assignedBooks is None:
                        genresBookDict[word] = set(book)
                    else:
                        assignedBooks.add(book)
                        
    return genresBookDict

def removeFluff(dict, fluff):
    for word in fluff:
        if word in dict:
            del dict[word]
            
    return dict

books = ingestISBNSubjectsCSV("subjects.csv")
#print(len(books))
subjectTop = False
wordFrequencyAnalysis = True

if subjectTop:
    uniqueSubjects = getUniqueSubjectsCount(books)
    sortedSubjects = getSortedPairsByOccurence(uniqueSubjects)
    
if wordFrequencyAnalysis:
    words = wordFrequencyDict(books)
    sortedWords = getSortedPairsByOccurence(words)
    sortedWordsAbove5k = getAboveX(sortedWords, 100)
    fluff = {"and",'by','in','of','new','one','for','the','into','manwoman','et','etc'}
    cleaned = removeFluff(sortedWordsAbove5k, fluff)
    #print(cleaned)
    print(len(cleaned))
    pair = getSubjectsBooksDictionaryM(cleaned, books)

    
    i = pair.items()
    lp = []
    for k,v in i:
        lp.append((k,len(v)))
    from operator import itemgetter
    sort = sorted(lp,key=itemgetter(1), reverse=True)
    uniqueBooks = {"dummy"}
    for k, v in i:
        if(len(v) >= 100):
            for book in v:
                if not book in uniqueBooks:
                    uniqueBooks.add(book)
    print(sort)
    print(len(uniqueBooks)-1)