import Common
from functools import reduce
from Common import dbg_print


def version():
    VERSION = '11'
    return VERSION

def solve_word(words, MY_BOT_NAME, excluded_letters, included_letters, greens, rate_multiplier_START, rate_multiplier_SPEED):
    letter_frequency, nmap = Common.map_freq(words)
    all_letters_global = letter_frequency.keys()
    # skipping new letters if there is something already
    srv_status = '200'
    last_word = ''
    tries = 0
    # the rest words
    # res is used instead of status temporary
    #while srv_status in ['200', 200]:
    res_json = {}
    while not 'success' in res_json:
        dbg_print("Try word: " + str(tries))
        tries = tries + 1
        dbg_print('words: ' + str(len(words)))
        dbg_print('excluded_letters: ' + str(excluded_letters))
        dbg_print('included_letters: ' + str(included_letters))
        dbg_print('greens: ' + str(greens))
        srv_status, res, res_json, last_word, excluded_letters, included_letters, greens = \
            pick_best_fitting_word(words, included_letters, letter_frequency, nmap, MY_BOT_NAME, tries, rate_multiplier_START, rate_multiplier_SPEED)
        words = Common.remove_exclude_include(words, last_word, excluded_letters, included_letters, greens)
        # FIXME fake_status, status
        # srv_status, res = Common.server_post(mybotname=MY_BOT_NAME, word='get')
        # dbg_print ('status: ' + str(srv_status))
        # dbg_print ('last_word: ' + str(last_word))
        # dbg_print ('excluded_letters: ' + str(excluded_letters))
        # dbg_print ('included_letters: ' + str(included_letters))
        # dbg_print ('greens: ' + str(greens))

    # depending on win/loose a final word is to be returned back to avoid reusing it in the future
    if 'success' in res_json:
        if res_json['success'] and tries < 7:
            print ("WIN!    Last word was: " + last_word)
            return 1, res_json
        else:
            print("_FAIL!    Last word was: " + last_word)
            return 0, res_json
    return 0, res_json


def pick_most_new_letters(words, letter_frequency, nmap, MY_BOT_NAME, include_letters, green_letters):
    dbg_print("Picking most new letters")
    word = ''
    wv, wvl = Common.value_words(words, letter_frequency, repeatable=False)
    for pair in wvl:
        word = pair[0]
        if len(set(word)) < 5:
            continue
        if not Common.check_IcludeExclude_in(include_letters, green_letters, word):
            break
    if word == '':
        word = wvl[0][0]
    status, res = Common.server_post(mybotname= MY_BOT_NAME, word = word)
    exclude_letters, include_letters, green_letters = Common.parse_server_response(res)
    return status, word, exclude_letters, include_letters, green_letters

def score_include(word, include, K):
    # K = 10
    score = 0
    # Add score per included letters
    for i in range(0,len(word)):
        w = word[i]
        exclude = include[i]
        INC = include.copy()
        INC.remove(exclude)
        local_letter_include = set(reduce(lambda x, y: x+y, INC))
        if w in local_letter_include:
            score = score + 1
    # Substract score per repeatable letters
    return score*K

def score_repeatable(word, K):
    # K = 10
    # A FEE for repeated letters
    score = 0 - (5-len(set(word)))
    return score*K*2

def pick_best_fitting_word(words, included_letters, letter_frequency, nmap, MY_BOT_NAME, tries, rate_multiplier_START = 3000, rate_multiplier_SPEED = 1000):

    K = rate_multiplier_START - tries * rate_multiplier_SPEED
    if K < 0:
        K = 0

    dbg_print("Picking best fitting word")
    wv, wvl = Common.value_words(words, letter_frequency, repeatable=True)
    if len(words) < 10:
        dbg_print (words)
    else:
        dbg_print(len(words))

    # if wvl:
    #     word = wvl[0][0]
    # else:
    #     print("else: ", words)
    #     word = words[0]
    wvl_lev = len(wvl)
    top = {}
    for i in range(0,wvl_lev):
        wvl_base_score = wvl_lev-i
        top[wvl[i][0]] = wvl_base_score + \
                         score_include(wvl[i][0], included_letters, K) + \
                         score_repeatable(wvl[i][0], K)
    dbg_print("TOP >> " + str(Common.sort_dict(top)[0:20]))
    #print(top)
    if len(top) > 0:
        word = Common.sort_dict(top)[0][0]
    else:
        word = 'текст'

    status, res, res_json = Common.server_post(mybotname=MY_BOT_NAME, word=word)
    exclude_letters, include_letters, green_letters = Common.parse_server_response(res)
    return status, res, res_json, word, exclude_letters, include_letters, green_letters