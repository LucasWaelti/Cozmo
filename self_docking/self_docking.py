# PATH to the file: C:\Users\Lucas Waelti\Documents\Cozmo\self_docking
'''
    Written by @Luc, https://forums.anki.com/u/Luc/activity
'''

import cozmo
from cozmo.util import degrees, radians, distance_mm, speed_mmps

import time
import math

robot = None

def init_robot(cozmo_robot: cozmo.robot.Robot):
    global robot
    robot = cozmo_robot

########################## Animations ##########################

def play_animation(robot: cozmo.robot.Robot, anim_trig, body = False, lift = False, para = False):
    # anim_trig = cozmo.anim.Triggers."Name of trigger" (this is an object)
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers" for animations' triggers
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.play_anim_trigger" for playing the animation

    robot.play_anim_trigger(anim_trig,loop_count = 1, in_parallel = para,
                            num_retries = 0, use_lift_safe = False,
                            ignore_body_track = body, ignore_head_track=False,
                            ignore_lift_track = lift).wait_for_completed()

        
def frustrated(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.FrustratedByFailureMajor  
    play_animation(robot,trigger)

def celebrate(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.CodeLabCelebrate  
    play_animation(robot,trigger,body=True,lift=True,para=True)

##########################Cubes related code##########################

# Cozmo's memory to know which cube still 
# needs to be put next to the charger
cubeIDs = []

def look_for_next_cube():
    # look for a cube that was not put next to the charger yet
    global robot, cubeIDs
    
    valid = True
    while(True):
        
        behavior = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            seen_cube = robot.world.wait_for_observed_light_cube(timeout=5,include_existing=True)
        except:
            seen_cube = None
        behavior.stop()
        
        if(seen_cube == None):
            frustrated(robot)
        else:
            # A cube was seen but we have to know if it has to be moved
            #print(seen_cube)
            if(len(cubeIDs) == 0):
                cubeIDs.append(seen_cube.object_id)
                return seen_cube # communicate that this cube has to be moved
            else:
                for i in range(0,len(cubeIDs)):
                    if(seen_cube.object_id == cubeIDs[i]):
                        valid = False # that cube was already taken care of
                if(valid):
                    cubeIDs.append(seen_cube.object_id)
                    return seen_cube
                else:
                    valid = True
    return None

def pickUp_cube(cube: cozmo.objects.LightCube):
    global robot
    action = robot.pickup_object(cube,use_pre_dock_pose=True, in_parallel=False, num_retries=2)
    action.wait_for_completed()
    return
def putDown_cube(cube: cozmo.objects.LightCube):
    global robot
    action = robot.place_object_on_ground_here(cube, in_parallel=False, num_retries=0)
    action.wait_for_completed()
    return
def stack_cube(target: cozmo.objects.LightCube):
    global robot
    action = robot.place_on_object(target, in_parallel=False, num_retries=0)
    action.wait_for_completed()
    return 

def clean_up_cubes():
    global cubeIDs

    cubeIDs = []
    charger = find_charger()
    print('Charger located')
    go_to_charger()
    turn_around()
    
    cube = look_for_next_cube()
    print(cubeIDs)
    pickUp_cube(cube)
    putDown_cube(cube)

    while(len(cubeIDs) < 3):
        look_for_next_cube()
        print(cubeIDs)
    return

##########################Charger related code##########################

def find_charger():
    global robot

    while(True):
        
        behavior = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            seen_charger = robot.world.wait_for_observed_charger(timeout=10,include_existing=True)
        except:
            seen_charger = None
        behavior.stop()
        if(seen_charger != None):
            #print(seen_charger)
            return seen_charger
        frustrated(robot)
        robot.say_text('Charge?',duration_scalar=0.5).wait_for_completed()
    return None

def go_to_charger():
    # Driving towards charger without much precision
    global robot

    charger = None
    ''' cf. 08_drive_to_charger_test.py '''
    # see if Cozmo already knows where the charger is
    if robot.world.charger:
        # make sure Cozmo was not delocalised after observing the charger
        if robot.world.charger.pose.is_comparable(robot.pose):
            print("Cozmo already knows where the charger is!")
            charger = robot.world.charger
        else:
            # Cozmo knows about the charger, but the pose is not based on the
            # same origin as the robot (e.g. the robot was moved since seeing
            # the charger) so try to look for the charger first
            pass
    if not charger:
        charger = find_charger()
    
    action = robot.go_to_object(charger,distance_from_object=distance_mm(80), in_parallel=False, num_retries=5)
    action.wait_for_completed()
    return charger

def disp_coord(charger: cozmo.objects.Charger):
    # Debugging function used to diplay coordinates of objects
    # (Not currently used)
    global robot

    r_coord = robot.pose.position #.x .y .z, .rotation otherwise
    r_zRot = robot.pose_angle.degrees # or .radians
    c_coord = charger.pose.position
    c_zRot = charger.pose.rotation.angle_z.degrees

    print('Recorded coordinates of the robot and charger:')
    print('Robot: ',end=' ')
    print(r_coord)
    print(r_zRot)
    print('Charger: ',end=' ')
    print(c_coord)
    print(c_zRot)
    print('\n')

PI = 3.14159265359
def clip_angle(angle=3.1415):
    # Retreive supplementary turns that aren't useful (in radians)
    global PI
    if(angle >= 2*PI):
        while(angle >= 2*PI):
            angle -= 2*PI
        return angle
    elif(angle <= -2*PI):
        while(angle <= -2*PI):
            angle += 2*PI
        return angle
    return angle

def final_adjust(charger: cozmo.objects.Charger):
    # Final adjustement to properly face the charger
    global robot,PI

    r_coord = [0,0,0]
    c_coord = [0,0,0]
    # Coordonates of robot and charger
    r_coord[0] = robot.pose.position.x #.x .y .z, .rotation otherwise
    r_coord[1] = robot.pose.position.y
    r_coord[2] = robot.pose.position.z
    r_zRot = robot.pose_angle.radians # .degrees or .radians
    c_coord[0] = charger.pose.position.x
    c_coord[1] = charger.pose.position.y
    c_coord[2] = charger.pose.position.z
    c_zRot = charger.pose.rotation.angle_z.radians

    # Create target position 
    dist_charger = 40 # mm, distance if front of charger
    c_coord[0] -=  dist_charger*math.cos(c_zRot)
    c_coord[1] -=  dist_charger*math.sin(c_zRot)

    # Direction and distance to target position (in front of charger)
    distance = math.sqrt((c_coord[0]-r_coord[0])**2 + (c_coord[1]-r_coord[1])**2 + (c_coord[2]-r_coord[2])**2)
    vect = [c_coord[0]-r_coord[0],c_coord[1]-r_coord[1],c_coord[2]-r_coord[2]]
    # Angle of vector going from robot's origin to target's position
    theta_t = math.atan2(vect[1],vect[0])

    print('CHECK: Adjusting position')
    # Face the target position
    angle = clip_angle((theta_t-r_zRot))
    robot.turn_in_place(radians(angle)).wait_for_completed()
    # Drive toward the target position
    robot.drive_straight(distance_mm(distance),speed_mmps(20)).wait_for_completed()
    # Face the charger
    angle = clip_angle((c_zRot-theta_t))
    robot.turn_in_place(radians(angle)).wait_for_completed()
    print('CHECK: Robot aligned')
    return

def restart_procedure(charger: cozmo.objects.Charger):
    global robot

    robot.stop_all_motors()
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.pose.invalidate()
    charger.pose.invalidate()
    print('Driving away')
    #robot.drive_straight(distance_mm(150),speed_mmps(80),in_parallel=False).wait_for_completed()
    robot.drive_wheels(80,80,duration=2)
    turn_around()
    robot.set_lift_height(height=0,max_speed=10,in_parallel=True).wait_for_completed()
    # Restart procedure
    get_on_charger()
    return

def get_on_charger():
    global robot

    charger = go_to_charger()

    final_adjust(charger)
    
    turn_around()
    robot.drive_wheel_motors(-100,-100)
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.set_head_angle(degrees(0),in_parallel=True).wait_for_completed()

    timeout = 2 # seconds before timeout
    t = 0
    # Wait for backwheels to climb on charger
    while(True):
        time.sleep(.5)
        t += 0.5
        if(t >= timeout):
            print('ERROR: robot timed out before climbing on charger.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) > 1.7):
            print('CHECK: backwheels on charger.')
            break
        
    # Wait for front wheels to climb on charger
    t = 0
    while(True):
        # print(robot.pose_pitch.degrees)
        time.sleep(.1)
        t += 0.1
        if(math.fabs(robot.pose_pitch.degrees) > 20 or t >= timeout):
            # The robot is climbing on charger's wall -> restart
            print('ERROR: robot climbed on charger\'s wall or timed out.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) < 1.7):
            print('CHECK: robot on charger, backing up on pins.')
            robot.stop_all_motors()
            break

    robot.set_lift_height(height=0,max_speed=100,in_parallel=True).wait_for_completed()
    robot.backup_onto_charger(max_drive_time=3)
    print('PROCEDURE SUCCEEDED')

    # Celebrate success
    robot.drive_off_charger_contacts().wait_for_completed()
    celebrate(robot)
    robot.backup_onto_charger(max_drive_time=3)
    return

########################## General code ##########################

def turn_around():
    global robot
    robot.turn_in_place(degrees(180)).wait_for_completed()
    return

########################## Main ##########################

def cozmo_program(cozmo_robot: cozmo.robot.Robot):
    global robot, cubeIDs
    init_robot(cozmo_robot)
    
    get_on_charger()
    return

if __name__ == "__main__":
    cozmo.robot.Robot.drive_off_charger_on_connect = True
    cozmo.run_program(cozmo_program,use_viewer=True,use_3d_viewer=False)
