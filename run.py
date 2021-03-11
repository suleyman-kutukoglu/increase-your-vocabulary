import json
import sqlite3
import os
from random import choice

# "I" and "i" are not the same letters in the Turkish alphabet. In the Turkish alphabet, "I" and "ı" are the same
# letter.
lower_map = {
    ord(u'I'): u'ı',
    ord(u'İ'): u'i',
}

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


def random_word():
    required_success_rate = float(settings["requiredSuccessRate"])
    required_correct_guess = int(settings["requiredGuess"])

    sql_unlearned_words = "SELECT * from 'words' where correctGuess = 0 OR (correctGuess < {} OR (((correctGuess*1.0/(correctGuess+wrongGuess))*100) < {}))".format(
        required_correct_guess, required_success_rate)
    cursor.execute(sql_unlearned_words)

    all_words = cursor.fetchall()
    random_word_from_all_words = choice(all_words)
    return random_word_from_all_words


def update_guess_counter(guess_type, word_tuple):
    sql_cursor = connection.cursor()
    update_word_name = word_tuple[0]
    if guess_type == 'correctGuess':
        update_sql = 'UPDATE words SET correctGuess = ? WHERE word = ?'
        sql_cursor.execute(update_sql, (str(int(word_tuple[2]) + 1), update_word_name))
    elif guess_type == 'wrongGuess':
        update_sql = 'UPDATE words SET wrongGuess = ? WHERE word = ?'
        sql_cursor.execute(update_sql, (str(int(word_tuple[3]) + 1), update_word_name))
    connection.commit()


def get_word_data(name_of_word):
    sql = "Select * from words where word = ?"
    sql_cursor = connection.cursor()
    sql_cursor.execute(sql, (name_of_word,))
    row_tuple = sql_cursor.fetchall()
    return row_tuple


def add_word_to_database(original_word, add_translated_word):
    add_sql = ' INSERT INTO words(word, translatedWord, correctGuess, wrongGuess)VALUES(?,?,?,?) '
    check_sql = 'SELECT word FROM words where word = ?'

    sql_cursor = connection.cursor()
    sql_cursor.execute(check_sql, (original_word.lower(),))
    check_word = sql_cursor.fetchall()

    if len(check_word) == 0:
        sql_cursor.execute(add_sql, (original_word.lower(), add_translated_word.translate(lower_map).lower(), 0, 0))
        print(message["successfullyAdded"])
    else:
        print(message["alreadyAdded"])

    connection.commit()


def remove_word_from_database(name_of_word):
    delete_sql = 'DELETE from words where word = ?'
    word_list = 'SELECT * FROM words where word = ?'

    sql_cursor = connection.cursor()
    sql_cursor.execute(word_list, (name_of_word.lower(),))

    this_word = sql_cursor.fetchall()

    if len(this_word) == 0:
        return False
    else:
        sql_cursor.execute(delete_sql, (name_of_word.lower(),))
        connection.commit()
        return True


def print_all_words():
    word_counter = int()
    cursor.execute("SELECT * from 'words'")

    all_words = cursor.fetchall()

    if len(all_words) == 0:
        clear()
        print(message["emptyDatabase"])
        return True
    elif len(all_words) == 0:
        clear()
        print("+" + "-" * 70 + "+\n")
        print(message["noWord"])
        print("\n+" + "-" * 70 + "+\n")
    else:
        clear()
        print(message["allWords"] + "+" + "-" * 70 + "+\n")
        for K in all_words:
            original_word = K[0]
            print_translated_word = K[1]
            correct_guess = K[2]
            wrong_guess = K[3]

            if correct_guess == 0 and wrong_guess == 0:
                success_rate = 0
            else:
                success_rate = (correct_guess * 1.0 / (correct_guess + wrong_guess)) * 100
            print(">>> {} ==> {}\n>>> {}%{:.2f}\n>>> {} {}\n>>> {} {}\n".format(original_word, print_translated_word,
                                                                                message["successRate"],
                                                                                success_rate, message[
                                                                                    "correctGuessCounter"],
                                                                                correct_guess,
                                                                                message[
                                                                                    "wrongGuessCounter"],
                                                                                wrong_guess))
            word_counter += 1
            print("\n+" + "-" * 70 + "+\n")
    print(message["printWordsEnd"] + str(word_counter) + "\n")
    return True


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

            word = random_word()
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

                word_data = get_word_data(word[0])
                word_name = word_data[0][0]
                translated_word = word_data[0][1]
                correct_counter = int(word_data[0][2])
                wrong_counter = int(word_data[0][3])

                if guess.translate(lower_map).lower() == word[1]:
                    update_guess_counter('correctGuess', word)
                    print("'{}' {}\n".format(guess, message["correctGuess"]))
                    print("{}{}\n".format(message["correctGuessCounter"], correct_counter, ))

                    if settings["showSuccessRate"] == "On":
                        try:
                            successRate = (
                                    (float(correct_counter) / (float(wrong_counter) + float(correct_counter))) * 100.0)

                            print("{} %{:.2f}\n".format(message["successRate"], successRate))

                        except ZeroDivisionError:
                            print("{} %0.0\n")

                elif guess.lower() == 'q':
                    clear()
                    break
                elif guess == '?':
                    print("{} ==> {}\n".format(word_name, translated_word))

                else:
                    update_guess_counter('wrongGuess', word)
                    print("\n'{}' {} '{}'\n".format(guess, message["wrongGuess"], translated_word))
                    if settings["showSuccessRate"] == "On":
                        try:
                            successRate = (
                                    (float(correct_counter) / (float(wrong_counter) + float(correct_counter))) * 100.0)

                            print("{} %{:.2f}\n".format(message["successRate"], successRate))

                        except ZeroDivisionError:
                            print("{} %0.0\n")
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
                learned_word_counter = int()
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
                        learned_word_counter += 1
                    print("\n+" + "-" * 70 + "+\n")
                    print("Total: {}\n".format(learned_word_counter))

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
                    print(message["languageChanged"] + "<<< {} >>>".format(settings["language"]))
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

                if originalWord.lower() == 'q':
                    numInput = "ExitLoop"
                    clear()
                    break

                translated_word = input("{}".format(message["enterTranslated"]))

                if translated_word.lower() == 'q':
                    numInput = "ExitLoop"
                    clear()
                    break

                verifyInput = input("{}".format(message["enterVerifyForAdd"]))
                clear()

                if verifyInput.lower() == 'e' or verifyInput.lower() == 'y':
                    verify = True

                if verify:
                    print("+" + "-" * 70 + "+\n")
                    add_word_to_database(originalWord, translated_word)

        elif numInput == '5':
            status_message = str()
            os.system('color c')
            while True:
                if consoleClearCounter == 1:
                    clear()
                    consoleClearCounter = 0
                print("+" + "-" * 70 + "+\n")
                print(status_message, end="")
                verify = False
                wordToBeDeleted = input("{}".format(message["enterWordToBeDeleted"]))
                consoleClearCounter += 1

                if wordToBeDeleted.lower() == 'q':
                    numInput = "ExitLoop"
                    clear()
                    break

                verifyInput = input("{}".format(message["enterVerifyForDelete"]))

                if verifyInput.lower() == 'y' or verifyInput.lower() == 'e':
                    verify = True

                elif verifyInput.lower() == 'q':
                    numInput = "ExitLoop"
                    clear()
                    break

                if verify:
                    if remove_word_from_database(wordToBeDeleted):
                        status_message = message["wordDeleted"]
                    else:
                        status_message = message["wordNotFound"]

        elif numInput == '6':
            if print_all_words():
                break

        elif numInput == "ExitLoop":  # for double break process
            clear()
            break
        else:
            clear()
            print("\n[!!!] {} [!!!]\n".format(message["wrongInput"]))
            break
