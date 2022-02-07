import random
from string import ascii_lowercase
import re
import pickle
from collections import Counter

# A class that plays Wordle
# A game where you have 6 chances to guess a 5 letter word
# Each guess offers some information about what letters are in the word
# This is the website for the original game: https://www.powerlanguage.co.uk/wordle/

class wordle():
    """[summary]
    This class contains functions to play wordle with a focus on testing 
    different starting strategies. You can offer a list of starting words
    and simulate how often each starting word would guess the target word
    within six guesses. The primary guessing function tries to create a 
    guess based on the most common letters among words that are still 
    valid given the knowledge attained from previous guesses.
    
    ### Methods ###
    
    sim: defines several games of wordle designed to test a series of strategies
    play: plays a single game of wordle. Target word and initial guesses can be specified
    guess: chooses the next word to guess in a game of wordle
    update_knowledge: stores information about what letters are valid based on words guessed
    most_common_letters: identifies the most common letters from a list of words
    word_from_common: creates a word using most common letters
    __init__: sets up some properties of the wordle class and loads the default wordlist
    __str__: designed to print stats summarizing simulations run
    export_results: dump simulation results to a pickle file
    """

    def __init__(self):
        # Load our potential 5 letter words
        # This default list is custom, the words
        # from the wordle website are also available in the sim method
        # guess_num is the current guess number for the current game
        # knowledge stores what we know about the current target word
        # games stores the results of all games
        # wins an total track the results of individual strategies
        
        with open('data/five_letter_words2.txt') as word_file:
            self.word_uni = list(set(word_file.read().split()))
        self.guess_num = None
        self.knowledge = None
        self.games = []
        self.wins = Counter()
        self.total = Counter()

    def __str__(self):
        # Prints information about games played so far.
        print_str = "Games played: " + str(len(self.games)) + '\n'
        for key in self.wins.keys():
            print_str += 'Win percent for %s: ' % (key)
            print_str += str(round(self.wins[key] / self.total[key] * 100,2)) + "%"
            print_str += '\n'
        
        return print_str
            
    def most_common_letters(self, word_list):
        # Fine the most common letters in the word list
        cnt = Counter()
        for word in word_list:
            for letter in word:
                cnt[letter] += 1
            
        sorted(cnt.elements())
        most_common_letters = ''
        for pair in cnt.most_common(15):
            most_common_letters += pair[0]
        
        return most_common_letters

    def word_from_common(self, common_letters, word_list, length):
        # Try to make a word using common letters from the word list
        for word in word_list:
            test = set(word) - set(common_letters[:length])
            if len(test) == (length - 5):
                return word
   
        # If it gets here it should mean there is no word of 
        # length 'length' given the letters.
        return ''

    def update_wordlist(self, old_list):
        # Create a regex that applies our knowledge
        learn_knowledge = re.compile("[%s][%s][%s][%s][%s]" % (self.knowledge[0], self.knowledge[1], self.knowledge[2], self.knowledge[3], self.knowledge[4]))
        
        # Use regex to filter possible words based on what letters are applicable
        filtered_words = list(filter(learn_knowledge.match, old_list))
        
        # Make sure guesses contain letters we know are in the word
        banned = []
        # We don't elim words on the first guess
        if self.guess_num > 1:
            # If we haven't guessed any correct letters, we cant ban words
            if self.knowledge[5] != '':
                # We don't want words that don't contain letters we know are in the target word
                for aletter in self.knowledge[5]:
                    for aword in filtered_words:
                        if aletter not in aword:
                            banned.append(aword)
        
        # Remove the banned words
        banned = set(banned)
        for aword in banned:
            filtered_words.remove(aword)
            
        return filtered_words
    
    def guess(self, possible_words, guess_list = []):
   
        # Choose a random word from eligible words
        # We could make this smarter
        
        # If there were pre determined guesses for this game, we guess them first
        if self.guess_num <= len(guess_list):
            current_guess = guess_list[self.guess_num - 1]
        
        # Otherwise we are going to try to make a word from the most common letters available
        # The idea is this gives us the best chances of finding all our letters quickly 
        else:
            current_guess = ''
            length = 5
            common_letters = self.most_common_letters(possible_words)
            while current_guess == '':
                current_guess = self.word_from_common(common_letters,possible_words,length)
                length += 1
                if length > 20:
                    # This is a way to exit if word_from_common can't make a word
                    current_guess = random.choice(possible_words)
                    print("Will is a dummy, a random word was guessed")
                    break
                
        return current_guess
     
        
    def update_knowledge(self, current_guess, target_word):
        # This method is using the information wordle gives us after each
        # guess to create a string of valid letters in each of the 5 positions
        # as well as a list of known letters. This allows a regex to be made
        # in another method to filter out words that don't contain the letters
        # we know are in the word.
        for index, letter in enumerate(current_guess):
            
            # If letter not in word, remove it from the knowledge in all indices
            # This is the 'black' scenario from the web version of the game
            if letter not in target_word:
                for index2, knowl in enumerate(self.knowledge[0:5]):
                    self.knowledge[index2] = knowl.replace(letter,"")
            else:
                # If the letter is in the correct spot, lock that spot for the knowledge
                # This is the 'green' scenario from the web version
                if letter == target_word[index]:
                    self.knowledge[index] = letter
                    if letter not in self.knowledge[5]:
                        self.knowledge[5] = letter + self.knowledge[5]
                else:
                    # letter is not in the correct spot, remove it from knowledge for just
                    # that index. This is the 'yellow' scenario from the web game
                    self.knowledge[index] = self.knowledge[index].replace(letter,"")
                    if letter not in self.knowledge[5]:
                        self.knowledge[5] = letter + self.knowledge[5]
        
        return None
        
    def play(self, guess_list = [], target_word = None):
        
        # Reset the game
        # All letters are valid at the start
        # All words are valid
        # Reset counters and storage variables
        game_letters = ascii_lowercase
        self.knowledge = [game_letters] * 5
        self.knowledge.append('')
        self.guess_num = 1
        possible_words = self.word_uni
        match = False
        this_guess = None
        all_guesses = []

        # This categorizes our games so we can summarize the results later
        if guess_list == []:
            name = "Random"
        else:
            name = guess_list[0] + str(len(guess_list))
        
        # Choose a random word to be guessed if we didn't specify a target
        if target_word == None:
            target_word = random.choice(self.word_uni)

        # make up to six guesses
        while self.guess_num < 7:
            
            # Revise the list of possible words based on what we know
            possible_words = self.update_wordlist(possible_words)
            
            # Guess a word and record it
            this_guess = self.guess(possible_words, guess_list)
            all_guesses.append(this_guess)

            # Check if we guessed correctly
            # If yes, return the game results
            # If no, update knowledge and guess again until we have guessed six times
            if this_guess == target_word:
                match = True
                return (name, target_word, match, self.guess_num, all_guesses)
            else:
                self.guess_num += 1
                self.update_knowledge(this_guess,target_word)
        
        # If we don't guess correctly after six guesses, return game results
        return (name, target_word, match, 6, all_guesses)
    
    def sim(self, word_num, guess_lists, domain_name = 'custom', seed = 314159):
        random.seed(seed)
        
        # We have some different word lists available for simulation
        # Wordle lists come from the javascript on the wordle website
        if domain_name == 'wordle1':
            self.word_uni = pickle.load(open("data/wordle_list_1.p", "rb"))
        elif domain_name == 'wordle2':
            self.word_uni = pickle.load(open("data/wordle_list_2.p", "rb"))
        elif domain_name == 'custom':
            #loaded as part of init
            None
            
        # Getting target words
        if word_num == "all":
            target_words = self.word_uni
        elif len(self.word_uni) < word_num:
            print("Not enough words to do that many outcomes. Use 'all' to take all available words")
        else:
            target_words = random.sample(self.word_uni, word_num)
        
        # Play each strategy for each word, record the results
        for word in target_words:
            # Random first guess strategy
            random_result = self.play(target_word=word)
            self.wins[random_result[0]] += random_result[2]
            self.total[random_result[0]] += 1
            self.games.append(random_result)
            for glist in guess_lists:
                # play each of the predefined guess strategies
                result = self.play(guess_list = glist, target_word=word)
                self.wins[result[0]] += result[2]
                self.total[result[0]] += 1
                self.games.append(result)
                
        return None
    
    def export_results(self, filename = 'wordle_results.p'):
        pickle.dump(self.games, open("filename", "wb"))
        print("data written to: ",filename)
        return None
    
mywordle = wordle()   
guess_lists = [["stare"],["acorn","tiles"],["stove"],["adieu"],["irate"],["arose"]]
mywordle.sim(word_num='all',guess_lists=guess_lists,domain_name='wordle1')  
print(mywordle)