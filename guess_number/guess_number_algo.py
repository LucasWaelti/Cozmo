import cozmo

import numpy as np
import time

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
    anim.propose_guess(robot, string_guess)
    print('Guess: ',guess)
    return guess

def search():
    # Main algorithm, used to narrow the search range at each try
    # and detect eventual errors from user
    global x,y
    while True:
        guess = propose_guess()
        
        if(check_memory(guess)): # Check if something's wrong
            anim.frustrated(robot)
            break
        #answer = input('Chosen value is smaller "s", greater "g", correct "c"? ')
        answer = anim.get_answer_from_cubes(robot)

        diff = y-x
        if(answer == 'c'):
            anim.wiggle(robot)
            anim.excited(robot)
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

    get_range()
    search()
    reset_memory()

    '''robot.start_freeplay_behaviors()
    while(True):
        time.sleep(1.0)'''

cozmo.robot.Robot.drive_off_charger_on_connect = True
cozmo.run_program(cozmo_program,use_viewer=False,use_3d_viewer=False)
