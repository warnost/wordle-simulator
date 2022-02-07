
#https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt
def load_words():
    with open('words_alpha.txt') as word_file:
        valid_words = set(word_file.read().split())

    return valid_words


if __name__ == '__main__':
    english_words = load_words()

import enchant
d = enchant.Dict("en_US")   
    
five_letter_words = []
for word in english_words:
    if len(word) == 5 and d.check(word):
        five_letter_words.append(word)
        


textfile = open("five_letter_words2.txt","w")
for word in five_letter_words:
    textfile.write(word + "\n")
print(len(five_letter_words))       
print(five_letter_words[:20])