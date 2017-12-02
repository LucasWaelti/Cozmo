import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
from cozmo.util import degrees

import time
import numpy as np

def play_animation(robot: cozmo.robot.Robot, anim_trig, body = False):
    # anim_trig = cozmo.anim.Triggers."Name of trigger" (this is an object)
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers" for animations' triggers
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.play_anim_trigger" for playing the animation

    robot.play_anim_trigger(anim_trig,loop_count = 1, in_parallel = False,
                            num_retries = 0, use_lift_safe = False,
                            ignore_body_track = body, ignore_head_track=False,
                            ignore_lift_track=False).wait_for_completed()

def hesitate_long(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.MeetCozmoFirstEnrollmentSayName #PatternGuessThinking #CodeLabThinking
    play_animation(robot,trigger)
    robot.turn_in_place(degrees(10)).wait_for_completed()

def hesitate_short(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.PatternGuessThinking #CodeLabThinking
    play_animation(robot,trigger,True)

def hesitate(robot: cozmo.robot.Robot):
    decide = np.random.random()
    if(decide > 0.6):
        hesitate_long(robot)
    else:
        hesitate_short(robot)
        transition(robot)

def transition(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.MajorWin # mainly used to reset arms
    play_animation(robot,trigger, True)

def sad(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.MajorFail 
    play_animation(robot,trigger)

def excited(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.CodeLabExcited 
    play_animation(robot,trigger)
    robot.turn_in_place(degrees(-130)).wait_for_completed()

def frustrated(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.FrustratedByFailureMajor  
    play_animation(robot,trigger)

def hiccup(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.Hiccup  
    play_animation(robot,trigger)

def wiggle(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.OnWiggle   
    play_animation(robot,trigger)

''' -------------------------------------------------------------- '''

def propose_guess(robot: cozmo.robot.Robot, guess = ''):
    robot.say_text(guess, voice_pitch = 0.5,play_excited_animation=False).wait_for_completed()

''' -------------------------------------------------------------- '''

def switch_cubes_on(robot: cozmo.robot.Robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    cube1.set_lights(cozmo.lights.red_light)
    cube2.set_lights(cozmo.lights.green_light)
    cube3.set_lights(cozmo.lights.blue_light)

def switch_cubes_off(robot: cozmo.robot.Robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    cube1.set_lights_off()
    cube2.set_lights_off()
    cube3.set_lights_off()

command = ''
def make_selected_cube_blink(robot: cozmo.robot.Robot):
    global command
    
    switch_cubes_off(robot)
    if(command == 'c'):
        blink_light = cozmo.lights.green_light
        cube = robot.world.get_light_cube(LightCube2Id)
    elif(command == 's'):
        blink_light = cozmo.lights.blue_light
        cube = robot.world.get_light_cube(LightCube3Id)
    elif(command == 'g'):
        blink_light = cozmo.lights.red_light
        cube = robot.world.get_light_cube(LightCube1Id)

    cube.set_light_corners(cozmo.lights.white_light,blink_light,blink_light,blink_light)
    time.sleep(0.1)
    cube.set_light_corners(blink_light,cozmo.lights.white_light,blink_light,blink_light)
    time.sleep(0.1)
    cube.set_light_corners(blink_light,blink_light,cozmo.lights.white_light,blink_light)
    time.sleep(0.1)
    cube.set_light_corners(blink_light,blink_light,blink_light,cozmo.lights.white_light)
    time.sleep(0.1)
    cube.set_lights(blink_light)
    time.sleep(0.1)
    switch_cubes_off(robot)
    
def handle_tapped(evt, **kw):
    global command
    ev_id = evt.obj.object_id
    # print('Event: ',evt.obj.object_id)
    ''' 1 - green, 2 - red, 3 - blue'''
    if(ev_id == 3):
        command = 's'
    elif(ev_id == 1):
        command = 'c'
    elif(ev_id == 2):
        command = 'g'
    
def get_answer_from_cubes(robot: cozmo.robot.Robot):
    global command
    command = ''
    timeOut = 30
    timer = 0
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    switch_cubes_on(robot)
    robot.add_event_handler(cozmo.objects.EvtObjectTapped, handle_tapped)

    while(True):
        time.sleep(0.5)
        timer += 0.5
        if(command != ''):
            make_selected_cube_blink(robot)
            return command
        elif(timer > timeOut):
            return 'timeOut'
