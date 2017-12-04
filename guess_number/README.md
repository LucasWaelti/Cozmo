# What it is about
With this program, Cozmo will try to guess the number you are thinking about (by default the search range is [0,60]). 
https://www.youtube.com/watch?v=Oj2uBXrqvrE
In the video, Cozmo makes guesses in French but the program should work fine for any language implemented in your Cozmo. As you can see, Cozmo takes some time before making its first guess because it is looking for me. Cozmo sees me then before its second guess and faces me. 
This idea came to me after seeing [this post](https://forums.anki.com/t/number-guessing-game/10846), so thank you @Cadwallader01 for the idea!
In the post above, the user is supposed to guess a number picked by Cozmo. But I think the other way around is also pretty interesting. That's why I imagined this simple algorithm to implement this functionality.

# How it works
When starting the program, you will be asked to sequentially tap on each cube when their light goes up (it's required for the event handling, at least in the way I implemented it). You can specify a new range for the search by typing the 2 limit values (`lower higher`) of the new range, separated by a space. It will be checked wether the input is valid or not and the range will be asked again if an error is detected. Any range is possible, you could select `-3000 5000` as your custom range if you want! 
On the other hand, if you want to use the default range, just press `Enter` without specifying anything and the program will further execute. 

To make Cozmo guess what is your secret number, you can only tell him if your number is greater or smaller than its guess. To do so, you can tap on each cube with the according color:

- blue: your number is smaller
- green: that's it! Cozmo guessed right
- red: your number is greater

When Cozmo finally finds your number, he plays a few animations celebrating and the program terminates.

While playing, Cozmo will look for face and will face it if it founds one. Cozmo will make a guess anyway, even if no face is detected.

If you mess things up and give weird answers, Cozmo will eventually be aware of it and will quit the game, kind of frustrated. 

If you don't give any answer quickly enough (after 30 seconds), Cozmo will show that it got bored and will exit the program.

At the end of each game, you can press `Enter` to restart a new game or leave by pressing any key followed by `Enter`. 

# The code!
[guess_number.py](https://github.com/LucasWaelti/Cozmo/blob/master/guess_number/guess_number.py) and 
[guess_number_anim.py](https://github.com/LucasWaelti/Cozmo/blob/master/guess_number/guess_number_anim.py)

## Remarks
I have tested the code a few times now and it should be robust enough. So if you decide to try it out, hopefully it will work just fine!

### Requirements
All you need is to download both files `guess_number_anim.py` and `guess_number.py` and run this last one and start playing. You will need the `numpy` module to be installed. 

### Advice
Simply be careful when starting the program, informations will be displayed in the command prompt to help you setup the game. Once it is launched, you do not need to care about it while playing, tho the guesses that Cozmo makes are also displayed on the screen in case the audio wasn't too good. 

### Feedback
I would really appreciate hearing back from those who try this little game. Any remark, suggestion or bug report would be appreciated!
