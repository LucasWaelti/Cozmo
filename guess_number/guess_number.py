'''
    Written by: @Luc (https://forums.anki.com/u/Luc/summary)
    
    This little program makes Cozmo guess a number between 0 and 60.
    When starting the program, you can specify a new range by typing
    the 2 limit values of the new range, separated by a space. It will
    be checked wether the input is valid or not and the range will be
    asked again if an error is detected. If you want to use the default
    range, just press Enter without specifying anything. 

    To make Cozmo guess what is your secret number, you can only tell
    him if your number is greater or smaller than his guess. To do so,
    you can tap on each cube with the right color:

    - blue: your number is smaller
    - green: that's it! Cozmo guessed right
    - red: your number is greater

    When Cozmo finally finds your number, he plays a few animations
    celebrating and the program is then over, ready to restart.

    If you mess things up and give weird answers, Cozmo will eventually
    be aware of it and will quit the program.

    If you don't give any answer quickly enough, Cozmo will get bored
    and exit the program.

    You need to have the file "guess_number_anim.py" in order to use
    this file. It contains the animation functions for Cozmo and the cubes. 
'''

import cozmo

import numpy as np
import time
import sys  # Only used to flush stdout buffer

import guess_number_anim as anim

robot = None

def init_robot(cozmo_robot: cozmo.robot.Robot):
    global robot
    robot = cozmo_robot

''' ----------------------Search logic------------------------- '''
guess_memory = []
x = 0
y = 0
error_detected = False

def reset_memory():
    global guess_memory
    guess_memory = []

def check_memory(guess):
    # Verify if the guess was already made before
    global guess_memory

    for i in range(0,len(guess_memory)):
        if(i == len(guess_memory)-1):
            # No check, this is the last guess!
            continue
        elif(guess == guess_memory[i]):
            print('Cozmo is confused... Something went wrong!')
            error_detected = True
            return True
    return False

def make_guess():
    # Produce a guess given a certain range.
    # The guess is patially random to avoid that Cozmo always uses
    # the same values while searching.
    global x,y,guess_memory

    diff = y-x
    if(diff == 2):
        guess = x + 1
    elif(diff == 1):
        guess = x
    elif(np.random.random() > 0.5):
        guess = x + diff/2 + np.random.random()*diff*0.1
    else:
        guess = x + diff/2 - np.random.random()*diff*0.1
    guess = int(guess)
    guess_memory.append(guess)
    return guess

def propose_guess():
    global robot
    guess = make_guess()
    string_guess = str(guess) + '?'
    anim.hesitate(robot)
    anim.find_face(robot)
    anim.propose_guess(robot, string_guess)
    print('Guess: ',guess)
    return guess

def search():
    # Main algorithm, used to narrow the search range at each try
    # and detect eventual errors from user
    global x,y,robot
    
    while True:
        guess = propose_guess()
        
        if(check_memory(guess)): # Check if something's wrong
            anim.frustrated(robot)
            anim.sad(robot)
            break
        #answer = input('Chosen value is smaller "s", greater "g", correct "c"? ')
        answer = anim.get_answer_from_cubes(robot)

        diff = y-x
        if(answer == 'c'):
            anim.success(robot)
            break
        elif(answer == 's'):
            y = guess
            if(diff == 1):
                y = y+1
        elif(answer == 'g'):
            x = guess
            if(diff == 1):
                x = x+1
        elif(answer == 'timeOut'):
            print('Timeout: no input from user')
            anim.bored(robot)
            anim.switch_cubes_off()
            break

def get_range():
    # Get the range of search 
    global x,y
    input_range = input("Range of search (press Enter for default): ")
    if(input_range == ''):
        x = 0
        y = 60
        print('Using default range: ','[',x,',',y,']')
        y = y + 1 # Small hack because of upper limit
    else:
        # Use special range
        x,y = input_range.split(' ')
        x = int(x)
        y = int(y)
        if(x >= y):
            print('The range specified is invalid')
            get_range()
            return
        print('Using custom range: ','[',x,',',y,']')
        y = y + 1 # Small hack because of upper limit
        
''' ----------------------Search logic: End------------------------- '''

def cozmo_program(c_robot: cozmo.robot.Robot):
    global robot
    init_robot(c_robot)

    anim.init_cubes(robot)
    print('Initialisation successful')
    anim.wiggle(robot)

    while(True):
        get_range()

        anim.find_face(robot)
        
        print('Color code:\n- Red: number is greater\n- Green: guess is correct')
        print('- Blue: number is smaller')
        
        search()
        
        reset_memory()
        error_detected = False

        sys.stdout.flush()
        again = input('Press Enter to restart a game or any key followed by Enter to exit: ')
        if(again != ''):
            break


cozmo.robot.Robot.drive_off_charger_on_connect = True
cozmo.run_program(cozmo_program,use_viewer=False,use_3d_viewer=False)
