#!/usr/bin/env python3
import random
class Game:
    def __init__(self,guesses,word_size,file):
        self.guesses = guesses
        self.word_length = word_size
        self.dict = []
        try:
            with open(file,"r") as file:
                for line in file:
                    for words in line.split():
                        if(len(words) == self.word_length):
                            self.dict.append(words)
        except FileNotFoundError:
            print("Error: File Not Found!"+file)
        except Exception as e:
            print("Error: ",e)
        self.word = self.select_word()
        

    def select_word(self):
        rand = random.randint(0,len(self.dict)-1)
        self.word = self.dict[rand]
        return self.word
    
    def contains(self,word):
        for i in self.dict:
            if(i == word):
                return True
        return False
    
    def hint(self,guess):
        hint = ""
        if len(guess) != len(self.word):
            print("Error: Guess is not the correct length. Length is:",self.word_length)
        for i in range(0,len(guess),1):
            if guess[i] == self.word[i]:
                hint += "="
            else:
                hint += '-'
        return hint

            
    


    