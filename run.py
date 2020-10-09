import json
import sqlite3
import os
from random import choice

# Opening json files.

with open('languages.json', 'r', encoding="utf-8") as f:
    lang = json.load(f)

with open('settings.json', 'r+', encoding="utf-8") as f:
    settings = json.load(f)

message = lang[settings["language"]]

# Welcome message and shell color
os.system('color 9')
print(message["welcome"])

# Database inclusion operations
connection = sqlite3.connect('words.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS words(word TEXT, translatedWord TEXT,  correctGuess INT, wrongGuess INT)')
connection.commit()


# Function definitions.
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def randomWord():
    sqlCursor = connection.cursor()
    sqlCursor.execute("SELECT * from 'words'")

    allRows = sqlCursor.fetchall()

    if len(allRows) == 0:
        return None
    else:
        wordFromDatabase = choice(allRows)

        try:
            successRateNow = float(wordFromDatabase[2]) / (
                    float(wordFromDatabase[2]) + float(wordFromDatabase[3])) * 100.0
        except ZeroDivisionError:
            successRateNow = 0

        guessNow = int(wordFromDatabase[2])
        requiredSuccessRate = float(settings["requiredSuccessRate"])
        requiredGuess = float(settings["requiredGuess"])

        i = 0

        while i < len(allRows) + 3:
            if len(allRows) == 0:
                return None

            else:
                if requiredSuccessRate > successRateNow or requiredGuess > guessNow:
                    validWord = wordFromDatabase
                    return validWord
                else:
                    allRows.remove(wordFromDatabase)
                    if len(allRows) == 0:
                        return None
                    else:
                        wordFromDatabase = choice(allRows)
                        try:
                            successRateNow = (float(wordFromDatabase[2]) / (
                                    float(wordFromDatabase[2]) + float(wordFromDatabase[3]))) * 100.0
                        except ZeroDivisionError:
                            successRateNow = 0
                        guessNow = int(wordFromDatabase[2])

                        i += 1
                        continue


def updateGuessCounter(guessType, wordTuple):
    if guessType == 'correctGuess':
        sql = 'UPDATE words SET correctGuess = ? WHERE word = ?'
        sqlCursor = connection.cursor()
        sqlCursor.execute(sql, (str(int(wordTuple[2]) + 1), wordTuple[0]))
        connection.commit()

    elif guessType == 'wrongGuess':
        sql = 'UPDATE words SET wrongGuess = ? WHERE word = ?'
        sqlCursor = connection.cursor()
        sqlCursor.execute(sql, (str(int(wordTuple[3]) + 1), wordTuple[0]))
        connection.commit()


def getWordData(nameOfWord):
    sql = "Select * from words where word = ?"
    sqlCursor = connection.cursor()
    sqlCursor.execute(sql, (nameOfWord,))
    rowTuple = sqlCursor.fetchall()
    return rowTuple


def addWordToDatabase(original, translated):
    addSql = ' INSERT INTO words(word, translatedWord, correctGuess, wrongGuess)VALUES(?,?,?,?) '
    checkSql = 'SELECT * FROM words where word = ?'

    sqlCursor = connection.cursor()
    sqlCursor.execute(checkSql, (original,))
    checkWord = sqlCursor.fetchall()

    if len(checkWord) == 0:
        sqlCursor.execute(addSql, (original, translated, 0, 0))
        print(message["successfullyAdded"])
    else:
        print(message["alreadyAdded"])

    connection.commit()


def removeWordFromDatabase(nameOfWord):
    deleteSql = 'DELETE from words where word = ?'
    wordList = 'SELECT * FROM words where word = ?'

    sqlCursor = connection.cursor()
    sqlCursor.execute(wordList, (nameOfWord,))

    thisWord = sqlCursor.fetchall()

    if len(thisWord) == 0:
        print(message["wordNotFound"])
    else:
        sqlCursor.execute(deleteSql, (nameOfWord,))
        print(message["wordDeleted"])

    connection.commit()


while True:
    os.system('color 9')
    print("+" + "-" * 70 + "+\n")
    numInput = input("{}".format(message["firstInfo"]) + "\n+" + "-" * 70 + "+\n")
    print(message["backMenu"])

    clear()
    consoleClearCounter = 0
    while True:
        if numInput == '1':
            os.system('color 06')

            word = randomWord()
            print("+" + "-" * 70 + "+\n")
            if word is None:
                print(message["emptyDatabase"] + "\n")
                break
            else:
                guess = input("'{}' {}".format(word[0], message["guessInput"]))
                print("\n")
                if consoleClearCounter == 2:
                    clear()
                    consoleClearCounter = 0

                consoleClearCounter += 1
                if guess.lower() == word[1]:
                    updateGuessCounter('correctGuess', word)

                    row = getWordData(word[0])
                    wordName = row[0][0]
                    translatedWord = row[0][1]
                    correctCounter = int(row[0][2])
                    wrongCounter = int(row[0][3])

                    print("'{}' {}\n".format(guess, message["correctGuess"]))
                    print("{}{}\n".format(message["correctGuessCounter"], correctCounter, ))

                    if settings["showSuccessRate"] == "On":

                        try:
                            successRate = (
                                    (float(correctCounter) / (float(wrongCounter) + float(correctCounter))) * 100.0)

                            print("{} %{:.2f}\n".format(message["successRate"], successRate))

                        except ZeroDivisionError:
                            print("{}\n".format(message["insufficientData"]))

                elif guess.lower() == 'q':
                    clear()
                    break
                else:
                    updateGuessCounter('wrongGuess', word)

                    row = getWordData(word[0])
                    wordName = row[0][0]
                    translatedWord = row[0][1]
                    correctCounter = int(row[0][2])
                    wrongCounter = int(row[0][3])

                    print("\n'{}' {} '{}'\n".format(guess, message["wrongGuess"], translatedWord))
                    if settings["showSuccessRate"] == "On":

                        try:
                            successRate = (
                                    (float(correctCounter) / (float(wrongCounter) + float(correctCounter))) * 100.0)

                            print("{} %{:.2f}\n".format(message["successRate"], successRate))

                        except ZeroDivisionError:
                            print("{}\n".format(message["insufficientData"]))
        elif numInput == '2':
            cur = connection.cursor()
            cur.execute("SELECT * from 'words'")

            rows = cur.fetchall()

            if len(rows) == 0:
                clear()
                print("+" + "-" * 70 + "+\n")
                print(message["emptyDatabase"] + "\n")
                break

            else:
                learned = dict()
                for e in rows:
                    correctCt = float(e[2])
                    wrongCt = float(e[3])

                    try:
                        successRt = (correctCt / (correctCt + wrongCt)) * 100.0
                    except ZeroDivisionError:
                        successRt = 0

                    if (int(e[2]) >= int(settings["requiredGuess"])) and (
                            float(settings["requiredSuccessRate"]) <= (correctCt / (wrongCt + correctCt)) * 100.0):
                        learned[e[0]] = [successRt, correctCt, wrongCt]

                if len(learned) == 0:
                    clear()

                    print("+" + "-" * 70 + "+\n")
                    print(message["noLearn"])
                    print("\n+" + "-" * 70 + "+\n")
                else:
                    clear()
                    print(message["learnedWords"] + "+" + "-" * 70 + "+\n")
                    print(message["requiredSuccessRate"] + "%{}\n".format(
                        float(settings["requiredSuccessRate"])))
                    print(message["requiredCorrectGuess"] + "{}\n".format(
                        int(settings["requiredGuess"])))

                    for k, v in learned.items():
                        print(">>> {} {} %{:.2f}\n{} {} {} {}\n".format(k, message["successRate"],
                                                                        v[0], message[
                                                                            "correctGuessCounter"], int(v[1]),
                                                                        message["wrongGuessCounter"],
                                                                        int(v[2])))
                    print("\n+" + "-" * 70 + "+\n")
                break
        elif numInput == '3':
            os.system('color c')
            errorInfo = str()
            clear()
            while True:
                print("+" + "-" * 70 + "+\n")

                settingsInput = input(
                    "{}{}".format(message["settingsInput"] + "\n", "\n" + "+" + "-" * 70 + "+\n"))
                if settingsInput == '1':
                    if settings["language"] == "TR":

                        with open('settings.json', 'r+') as f:
                            settings = json.load(f)
                            settings['language'] = "EN"
                            f.seek(0)
                            json.dump(settings, f, indent=4)
                            f.truncate()
                        message = lang[settings["language"]]
                    else:
                        with open('settings.json', 'r+') as f:
                            settings = json.load(f)
                            settings['language'] = "TR"
                            f.seek(0)
                            json.dump(settings, f, indent=4)
                            f.truncate()
                        message = lang[settings["language"]]
                    clear()
                    print(message["languageChanged"]+"<<< {} >>>".format(settings["language"]))
                elif settingsInput == '2':
                    if settings["showSuccessRate"] == "On":
                        clear()
                        print(message["successStatusOff"])

                        with open('settings.json', 'r+') as f:
                            settings = json.load(f)
                            settings['showSuccessRate'] = "Off"
                            f.seek(0)
                            json.dump(settings, f, indent=4)
                            f.truncate()
                    else:
                        clear()
                        print(message["successStatusOn"])

                        with open('settings.json', 'r+') as f:
                            settings = json.load(f)
                            settings['showSuccessRate'] = "On"
                            f.seek(0)
                            json.dump(settings, f, indent=4)
                            f.truncate()
                elif settingsInput == '3':
                    while True:
                        try:
                            clear()
                            print(errorInfo)
                            rateInput = input("{}".format(message["rateInputInfo"]))
                            clear()

                            if rateInput == 'Q' or rateInput == 'q':
                                break

                            if 100 >= float(rateInput) > 0:
                                print(message["rateChanged"] + "%{}".format(rateInput))
                                with open('settings.json', 'r+') as f:
                                    settings = json.load(f)
                                    settings['requiredSuccessRate'] = str(rateInput)
                                    f.seek(0)
                                    json.dump(settings, f, indent=4)
                                    f.truncate()
                                break
                            else:
                                errorInfo = message["invalidRateInput"]
                                continue
                        except ValueError:
                            clear()
                            errorInfo = message["badRateInput"]
                            continue

                        clear()
                        print(message["rateChanged"] + "%{}".format(rateInput))
                        break
                elif settingsInput == '4':
                    errorInfo = str()
                    while True:

                        try:
                            clear()
                            print(errorInfo)
                            guessInput = input("{}".format(message["guessInputInfo"]))
                            clear()

                            if guessInput == 'Q' or guessInput == 'q':
                                break

                            if int(guessInput) >= 0:
                                print(message["guessChanged"] + ">>> {} <<<".format(guessInput))
                                with open('settings.json', 'r+') as f:
                                    settings = json.load(f)
                                    settings['requiredGuess'] = str(guessInput)
                                    f.seek(0)
                                    json.dump(settings, f, indent=4)
                                    f.truncate()
                                break
                            else:
                                clear()
                                errorInfo = message["invalidGuessInput"]
                                continue
                        except ValueError:
                            clear()
                            errorInfo = message["badGuessInput"]
                            continue

                        clear()
                        print(message["guessChanged"] + "%{}".format(rateInput))
                        break
                elif settingsInput.lower() == 'q':
                    numInput = "ExitLoop"
                    break
                else:
                    clear()
                    print("\n[!!!] {} [!!!]\n".format(message["wrongInput"]))
                    continue
        elif numInput == '4':
            os.system('color a')
            clear()
            while True:
                print("+" + "-" * 70 + "+\n")
                verify = False
                originalWord = input("{}".format(message["enterOriginal"]))
                translatedWord = input("{}".format(message["enterTranslated"]))
                verifyInput = input("{}".format(message["enterVerifyForAdd"]))
                clear()

                if verifyInput == 'E' or verifyInput == 'e' or verifyInput == 'Y' or verifyInput == 'y':
                    verify = True

                if originalWord == 'q' or originalWord == 'Q' or translatedWord == 'q' or translatedWord == 'Q':
                    numInput = "ExitLoop"
                    clear()
                    break
                if verify:
                    print("+" + "-" * 70 + "+\n")
                    addWordToDatabase(originalWord, translatedWord)

        elif numInput == '5':
            os.system('color 4')
            while True:
                print("+" + "-" * 70 + "+\n")
                verify = False
                wordToBeDeleted = input("{}".format(message["enterWordToBeDeleted"]))
                verifyInput = input("{}".format(message["enterVerifyForDelete"]))

                if verifyInput == 'E' or verifyInput == 'e' or verifyInput == 'Y' or verifyInput == 'y':
                    verify = True

                if wordToBeDeleted == 'q' or wordToBeDeleted == 'Q':
                    numInput = "ExitLoop"
                    clear()
                    break
                if verify:
                    removeWordFromDatabase(wordToBeDeleted)
        elif numInput == '6':

            cur = connection.cursor()
            cur.execute("SELECT * from 'words'")

            rows = cur.fetchall()

            if len(rows) == 0:
                clear()
                print(message["emptyDatabase"])
                break

            else:
                allWords = dict()
                for e in rows:
                    correctCt = float(e[2])
                    wrongCt = float(e[3])

                    try:
                        successRt = (correctCt / (correctCt + wrongCt)) * 100.0
                    except ZeroDivisionError:
                        successRt = 0

                    allWords[e[0]] = [successRt, correctCt, wrongCt]

                if len(allWords) == 0:
                    clear()

                    print("+" + "-" * 70 + "+\n")
                    print(message["noWord"])
                    print("\n+" + "-" * 70 + "+\n")
                else:
                    clear()
                    print(message["allWords"] + "+" + "-" * 70 + "+\n")

                    for k, v in allWords.items():
                        print(">>> {} {} %{:.2f}\n{} {} {} {}\n".format(k, message["successRate"],
                                                                        v[0], message[
                                                                            "correctGuessCounter"], int(v[1]),
                                                                        message["wrongGuessCounter"],
                                                                        int(v[2])))
                    print("\n+" + "-" * 70 + "+\n")
                break

        elif numInput == "ExitLoop":  # for double break process
            clear()
            break
        else:
            clear()
            print("\n[!!!] {} [!!!]\n".format(message["wrongInput"]))
            break
