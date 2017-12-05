'''
    Written by: @Luc (https://forums.anki.com/u/Luc/summary)
'''

import cozmo
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
from cozmo.util import degrees

import time
import numpy as np

def find_face(robot: cozmo.robot.Robot):
    # Look around for a face
    
    behavior = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
    try:
        face_to_follow = robot.world.wait_for_observed_face(timeout=5)
    except:
        face_to_follow = None
    # Stop looking around, a face appeared
    behavior.stop()
    if(face_to_follow):
        turn_action = robot.turn_towards_face(face_to_follow).wait_for_completed()

''' -------------------------------------------------------------- '''

def play_animation(robot: cozmo.robot.Robot, anim_trig, body = False, para = False):
    # anim_trig = cozmo.anim.Triggers."Name of trigger" (this is an object)
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers" for animations' triggers
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.play_anim_trigger" for playing the animation

    robot.play_anim_trigger(anim_trig,loop_count = 1, in_parallel = para,
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
    if(decide > 0.5):
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

def success(robot: cozmo.robot.Robot):
    decide = np.random.random()
    if(decide > 0.4):
        excited(robot)
    else:
        wiggle(robot)

def bored(robot: cozmo.robot.Robot):
    trigger1 = cozmo.anim.Triggers.NothingToDoBoredIntro 
    trigger2 = cozmo.anim.Triggers.NothingToDoBoredEvent
    trigger3 = cozmo.anim.Triggers.NothingToDoBoredOutro 
    play_animation(robot,trigger1)
    play_animation(robot,trigger2)
    play_animation(robot,trigger3)

''' -------------------------------------------------------------- '''

def propose_guess(robot: cozmo.robot.Robot, guess = ''):
    robot.say_text(guess, voice_pitch = 0.5,play_excited_animation=False).wait_for_completed()

''' -------------------------------------------------------------- '''

# The event handler is non-deterministic regarding the order of events
''' cube1 - red
    cube2 - green
    cube3 - blue'''
cube1 = None
cube2 = None
cube3 = None
# Mapping of events to id, cubes and commands.
# Give ID returned by handler at event as parameter
# to the following dictionnaries to retreive value
ev_cube = {1:None,2:None,3:None}
ev_command = {1:'',2:'',3:''}
ev_light  = {1:None,2:None,3:None}
ev_id = 0

def switch_cube_on(cube,light):
    cube.set_lights(light)
    
def switch_cubes_on():
    global cube1,cube2,cube3

    cube1.set_lights(cozmo.lights.red_light)
    cube2.set_lights(cozmo.lights.green_light)
    cube3.set_lights(cozmo.lights.blue_light)

def switch_cubes_off():
    global cube1,cube2,cube3

    cube1.set_lights_off()
    cube2.set_lights_off()
    cube3.set_lights_off()

def handle_tap_init(evt, **kw):
    global ev_id
    ev_id = evt.obj.object_id


def make_selected_cube_blink(cube,blink_light):
    # Animate tapped cube
    cube.set_light_corners(blink_light,blink_light,blink_light,blink_light)
    time.sleep(0.1)
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
    switch_cubes_off()

def init_cubes(robot: cozmo.robot.Robot):
    global cube1,cube2,cube3,ev_cube,ev_id,ev_command,ev_light
    cube1 = robot.world.get_light_cube(LightCube1Id)  # looks like a paperclip
    cube2 = robot.world.get_light_cube(LightCube2Id)  # looks like a lamp / heart
    cube3 = robot.world.get_light_cube(LightCube3Id)  # looks like the letters 'ab' over 'T'

    # Make sure each cube is off
    switch_cubes_off()
    # Add listener to control initialisation
    handler = robot.add_event_handler(cozmo.objects.EvtObjectTapped, handle_tap_init)

    seq = ['red','green','blue']
    light_seq = [cozmo.lights.red_light,cozmo.lights.green_light,cozmo.lights.blue_light]
    cube_seq = [cube1,cube2,cube3]
    comm_seq = ['g','c','s'] # greater,correct,smaller
    for i in range(0,3):
        print('Tap the ',seq[i],' cube')
        switch_cube_on(cube_seq[i],light_seq[i])
        while(True):
            if(ev_id):
                # Map event to cube
                ev_cube[ev_id] = cube_seq[i]
                ev_command[ev_id] = comm_seq[i]
                ev_light[ev_id] = light_seq[i]
                make_selected_cube_blink(ev_cube[ev_id],light_seq[i])
                switch_cubes_off()
                ev_id = 0
                break
    handler.disable()
    
''' -------------------------------------------------------------- '''
    
def handle_tapped(evt, **kw):
    global ev_id
    ev_id = evt.obj.object_id

def get_answer_from_cubes(robot: cozmo.robot.Robot):
    global cube1,cube2,cube3,ev_cube,ev_id,ev_command,ev_light
    timeOut = 30
    timer = 0
    
    switch_cubes_on()
    handler = robot.add_event_handler(cozmo.objects.EvtObjectTapped, handle_tapped)

    while(True):
        time.sleep(0.5)
        timer += 0.5
        if(ev_id):
            switch_cubes_off()
            make_selected_cube_blink(ev_cube[ev_id],ev_light[ev_id])
            local_id = ev_id
            ev_id = 0 # Deactivate selection
            handler.disable()
            return ev_command[local_id]
        elif(timer > timeOut):
            handler.disable()
            return 'timeOut'
