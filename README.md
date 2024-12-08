# Word-game
This is a word game that tests which player can decipher the word first.

**How to play:**
1. **Start the server:** Run the `python3 server.py -p <port>` script. 
2. **Connect clients:** Run the `python3 client.py -i <host> -p <port> <username>` script on two different machines or terminals.
3. **Start the game** the fastest player to decode the word wins.
4. **Guess** Guess a 5 letter word if the guessed word shares a letter with the goal word  but the letter is not in the right position a '*' will appear under that guessed word's character location. If the guessed word contains a letter that is in the correct position as the goal word a '+' will appear under the guessed word at that letters position. If a guessed word's character is not in the goal word then a "-" will be displayed under the guess words character position.
5. **Goal of the Game** Both players are given the same english 5 letter word. The first player to guess the word wins.
6. **Winning screen** The first player to guess the word right will have their name apear with a winning message a new game with a new word will start.
7. **Features added** /chat /move and /quit
8.  **Synchronization added** clients are now updated in real time.

**Tech used**
* Python
* Sockets
* 5 letter words from kaggle dataset https://www.kaggle.com/datasets/cprosser3/wordle-5-letter-words?resource=download

**Roadmap**
* Taking this project further we would add a more in depth graphical user interface with a web server and clients using javascript and react. We would then add more features to the game for clients to interact with one another. Adding the ability to create user profiles, send invites, add friends, ...etc. This will create a much more in depth and fully developed game for users.

**Retrospective**
1. Things that went well for us as a team was working together and assigning tasks to one another to develop the entire project. The implementation of the client and server went really well as we were able to get them working together right away. This allowed us to work further on adding features and furthering the implementation of the game logic
2. Some things that could have been improved is adding more features as well as implementing a further ui for users. We also could have added encryption with more time. 
