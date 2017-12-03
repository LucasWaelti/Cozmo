ShowCase
Game - Cozmo guesses your secret number

# What it is about
With this program, Cozmo will try to guess the number you are thinking about (by default the search range is [0,60]). 
This idea came to me after seeing this post: https://forums.anki.com/t/number-guessing-game/10846
In the post above, the user is supposed to guess a number picked by Cozmo. But I think the other way around is also pretty interesting. That's why I imagined this simple algorithm to implement this functionality.

# How it works
When starting the program, you will be asked to sequentially tap on each cube when their light goes up (it's required for the event handling). You can specify a new range for the search by typing the 2 limit values (`lower higher`) of the new range, separated by a space. It will be checked wether the input is valid or not and the range will be asked again if an error is detected. Any range is possible, you could select `-3000 5000` as your custom range if you want! 
On the other hand, if you want to use the default range, just press `Enter` without specifying anything and the program will further execute. 

To make Cozmo guess what is your secret number, you can only tell him if your number is greater or smaller than his guess. To do so, you can tap on each cube with the according color:

- blue: your number is smaller
- green: that's it! Cozmo guessed right
- red: your number is greater

When Cozmo finally finds your number, he plays a few animations celebrating and the program terminates.

If you mess things up and give weird answers, Cozmo will eventually be aware of it and will quit the game, kind of frustrated. 

If you don't give any answer quickly enough (after 30 seconds), Cozmo will show that it got bored and will exit the program.

You also need to have the file `guess_number_anim.py` next to `guess_number.py` in order to run the program. It contains the animation functions for Cozmo and the cubes. 

At the end of each game, you can press `Enter` to restart a new one or leave by pressing any key followed by `Enter`. 
