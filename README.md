# Word-game
This is a word game that tests which player can decipher the word first.

**How to play:**
1. **Start the server:** Run the `server.py` script. 
2. **Connect clients:** Run the `client.py <host> <port> <message> <username>` script on two different machines or terminals.
3. **Start the game** the fastest player to decode the word will be given a point first player to seven wins.
4. **Guess** Guess a 6 letter word if the guessed word shares a letter with the goal word  but the letter is not in the right position a '*' will appear under that guessed word's character location. If the guessed word contains a letter that is in the correct position as the goal word a '$' will appear under the guessed word at that letters position. If a guessed word's character is not in the goal word then a "-" will be displayed under the guess words character position.
5. **Goal of the Game** Both players are given the same english 6 letter word. The first player the guess the word will be given a point. After one player has correctly guessed the word a point will be add the the player who guessed the word correctly, and a new round will begin. The first player to 7 points wins the game.
6. **Winning screen** The first player to 7 will have there name appear on both player screen delcaring them the victor. The option to play again will appear as well.
7. **Features added** /chat /move and /quit
8.  **Synchronization added** clients are now updated in real time.
**Tech used**
* Python
* Sockets
