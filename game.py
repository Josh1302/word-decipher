class Game:
    def __init__(self,guesses,word_size):
        self.guesses = guesses
        self.word_length = word_size
    
    def dict(self,file):
        try:
            with open(file) as file:
                s = []
                for i in file:
                    if(len(i) == self.word_length):
                        s.append(i)
        except FileNotFoundError:
            print("Error: File Not Found!"+file)
        except Exception as e:
            print("Error: ",e)