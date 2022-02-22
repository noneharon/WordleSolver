import Common
import os
import gen8 as genX

global letter_frequency
global all_letters_global
global words
from Common import dbg_print
import time

words = Common.load_dictionary(path = r'server_dict.txt', len = 5)

# MY_BOT_NAME = 'haron_gen' + str(genX.version())
MY_BOT_NAME = 'test'
URL = 'http://92.55.33.180:40280/'
# time.sleep(60*30)

#letter_frequency, nmap = Common.map_freq(words)

#all_letters_global = letter_frequency.keys()

#print (Common.sort_dict(letter_frequency))

#for dep in range(0,5):
#    tmp = ''
#    for letter in nmap:
#        #print (letter)
#        tmp = tmp + letter[dep][0]
#    print (tmp)



#wv, wvl = Common.value_words(words, letter_frequency, repeatable = False)
#print ("Most Valuable words")
#for i in range(0,10):
#    print (wvl[i][0])

def init(words, MY_BOT_NAME):
    dbg_print ("__INIT__")
    status, res, res_test = Common.server_post(mybotname=MY_BOT_NAME, word='get')
    dbg_print (res)
    exclude_letters, include_letters, green_letters = Common.parse_server_response(res)
    words = Common.remove_exclude_include(words, '', exclude_letters, include_letters, green_letters)
    return exclude_letters, include_letters, green_letters

if __name__ == "__main__":
    # clear = lambda: os.system('cls')
    START_RANGE  = range(3400,4000,200)
    # START_RANGE = [3800]
    SPEED_RANGE = range(300,500,50)
    # SPEED_RANGE = [400]
    STATS = {}
    for rate_multiplier_START in START_RANGE:
        STATS[rate_multiplier_START]={}
        for rate_multiplier_SPEED in SPEED_RANGE:
            dbg_print("-----------------")
            dbg_print("STATS for " + str(rate_multiplier_START+rate_multiplier_SPEED))
            dbg_print("-----------------")
            N = 1000
            results = {"Win":0,"Lose":0}
            for i in range(0,N):
                dbg_print("Staring SOLVER cycle # " + str(i))
                exclude_letters, include_letters, green_letters = init(words, MY_BOT_NAME)
                result, res_json = genX.solve_word(words, MY_BOT_NAME, exclude_letters, include_letters, green_letters, rate_multiplier_START, rate_multiplier_SPEED)
                if result == 1:
                    results["Win"] = results["Win"] + 1
                else:
                    results["Lose"] = results["Lose"] + 1
                # clear()
                dbg_print (results)
                dbg_print (res_json)
                # waitt = input("PRESS ENTER TO CONTINUE... ");
            STATS[rate_multiplier_START][rate_multiplier_SPEED] = results
    print(STATS)