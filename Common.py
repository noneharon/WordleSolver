import requests as r
import json
import re


def dbg_print(text):
    dbg = False
    # dbg = True
    if dbg:
        print (text)

def server_post(**kwargs):
    if 'URL' in kwargs.keys():
        URL = kwargs['URL']
    else:
        URL = 'http://92.55.33.180:40280/'

    if 'mybotname' in kwargs.keys():
        mybotname = kwargs['mybotname']
    else:
        mybotname = 'haron_genX'

    if 'word' in kwargs.keys():
        word = kwargs['word']
    else:
        word = 'get'

    for i in range(0,3):
        #print ("try " + str(i))
        try:
            #print ({'name': mybotname, 'word': word})
            res = r.post(URL, data={'name': mybotname, 'word': word})
        except:
            dbg_print ("post to " + URL + " failed")
        if res:
            dbg_print ("CONNECTED")
            dbg_print (res.status_code)
            dbg_print(res.json())
            #print (res.json())
            break
    return res.status_code, res.json()['state'], res.json()

# def fix_server_reply_error(s):
#     x = re.split(r',\d+:', s)
#     ss = x[0]
#     for i in range(1, len(x)):
#         ss = ss + ":" + x[i]
#     return ss

def parse_server_response(res):
    #print (res)
    leng = 5
    exclude = []
    include = []
    green = []
    for i in range(0,leng):
        include.append([])
        green.append('')

    for last_try in res.split(','):
        mask = last_try.split(':')[-1]
        word = last_try.split(':')[0]
        for flag_id in range(0,len(mask)):
            if mask[flag_id] == 'x':
                exclude.append(word[flag_id])
            elif mask[flag_id] == 'e':
                include[flag_id].append(word[flag_id])
            elif mask[flag_id] == 'm':
                green[flag_id] = word[flag_id]
    return set(exclude), include, green

def flatten_array(array):
    tmp = []
    for i in array:
        if type(i) == list:
            tmp = tmp + i
        elif type(i) == str:
            tmp.append(i)
    return tmp

def check_icludes_in(included_letters, word):
    # checks if letters from included list is in corresponding place of the word
    for i in range(0,len(word)):
        if word[i] in included_letters[i]:
            return False
    # check if all the included letters are in the word
    map_includes = {}
    all_letters = []
    for i in included_letters:
        all_letters = all_letters + i
    all_letters = list(set(all_letters))

    for i in all_letters:
        if not i in word:
            return False

    return True

def check_IcludeExclude_in(included_letters, greens, word):
    all_letters = flatten_array(included_letters) + flatten_array(greens)
    # checks if any letter from included and excluded lists in ANY place of the word
    for i in range(0,len(word)):
        if word[i] in all_letters:
            return True
    return False

def remove_exclude_include(words, word_to_exclude, excluded_letters, included_letters, greens):
    new_words = []
    for word in words:
        if word_to_exclude != word and \
                excluded_letters.intersection(set(word)) == set() and \
                check_icludes_in(included_letters, word):
            new_words.append(word)
    # check greens
    green_words = []
    for word in new_words:
        flag = 0
        for i in range(0,len(word)):
            if greens[i] != '' and greens[i] != word[i]:
                flag = 1
        if flag == 0:
            green_words.append(word)
    return green_words

def sort_dict(markdict):
    marklist = sorted(markdict.items(), key=lambda x: x[1], reverse=True)
    tmp = [list(i) for i in marklist]
    #sortdict = dict(marklist)
    return tmp

def value_words(words, letter_frequency, **kwargs):
    if 'repeatable' in kwargs.keys():
        repeatable = kwargs['repeatable']
    else:
        repeatable = True

    value_dict = {}
    for word in words:
        all_letters = list(letter_frequency.keys())
        word_value = 0
        for let in word:
            if not repeatable:
                if let not in all_letters:
                    continue
            else:
                if let in all_letters:
                    all_letters.remove(let)
            word_value = word_value + letter_frequency[let]
        value_dict[word] = word_value
    return value_dict, sort_dict(value_dict)

def load_dictionary(**kwargs):
    if 'path' in kwargs.keys():
        path = kwargs['path']
    else:
        path = r'russian_nouns.txt'

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    words = []
    for word in lines:
        words.append(word.replace("\n",''))

    if 'len' in kwargs.keys():
        tmp = []
        for word in words:
            if len(word) == kwargs['len']:
                tmp.append(word)
        words = tmp
    return words

def map_freq(words):
    map = {}
    nmap = []
    for word in words:
        for let in range(0,len(word)):
            i = word[let]
            if i in map.keys():
                map[i] = map[i]+1
            else:
                map[i] = 1

            if len(nmap)<=let:
                nmap.append({})
            if i in nmap[let].keys():
                nmap[let][i] = nmap[let][i] + 1
            else:
                nmap[let][i] = 1
    tmp = []
    for i in nmap:
        tmp.append(sort_dict(i))
    nmap = tmp
    return map, nmap