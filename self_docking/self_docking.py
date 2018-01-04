'''
    Written by @Luc, https://forums.anki.com/u/Luc/activity

    This program enables Cozmo to drive off its charger, collect its cubes
    by placing them near its charger and then climbing back onto its 
    charger when it is done. Cozmo will directly try to climb back onto its charger
    if the battery is low. No further help or markers are required. 
    It is possible that Cozmo does not find a cube or its charger, 
    so it will ask for help if needed. Just place the required object 
    or Cozmo in a position where Cozmo can keep working and let it finish its job!

	TODO (improvements): 
	- Support already stacked or rolled cubes when cleaning up. 
	- Stack cubes as a pyramid instead of current configuration. 
	- Speed up some processes. 
'''

import cozmo
from cozmo.util import degrees, radians, distance_mm, speed_mmps
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id

import time
import math

# Choose on which side of the charger (when facing it),
# Cozmo should put its cubes.
# SIDE = 1 (left), SIDE = -1 (right)
SIDE = -1

# Pitch value when head is horizonal, calculated later.
pitch_threshold = 0

# Define how many search cycles must be engaged (5 sec each) while looking for cubes.
# When this number is reached, Cozmo will stop looking for its cubes and will drive 
# back onto its charger. 
retries = 5

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

########################## Cube lights related code ##########################

def switch_cube_on(cube: cozmo.objects.LightCube):
	cube.set_lights(cozmo.lights.green_light)
	return

def switch_cube_off(cube: cozmo.objects.LightCube):
	cube.set_lights_off()
	return

########################## Cubes related code ##########################

# Cozmo's memory to know which cube still 
# needs to be put next to the charger
cubeIDs = []
cubes = []

def look_for_next_cube():
    # look for a cube that was not put next to the charger yet
    global robot, cubeIDs, cubes, retries

    i = 0
    valid = True
    while(True):
        i += 1
        behavior = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            seen_cube = robot.world.wait_for_observed_light_cube(timeout=5,include_existing=True)
        except:
            seen_cube = None
        behavior.stop()
        
        if(seen_cube == None):
            frustrated(robot)
            robot.say_text('Cube?',duration_scalar=0.5).wait_for_completed()
        else:
            # A cube was seen but we have to know if it has to be moved
            if(len(cubeIDs) == 0):
                cubeIDs.append(seen_cube.object_id)
                cubes.append(seen_cube)
                return seen_cube # communicate that this cube has to be moved
            else:
                for i in range(0,len(cubeIDs)):
                    if(seen_cube.object_id == cubeIDs[i]):
                        valid = False # that cube was already taken care of
                if(valid):
                    cubeIDs.append(seen_cube.object_id)
                    cubes.append(seen_cube)
                    return seen_cube
                else:
                    valid = True

        if(i >= retries):
        	print('ERROR: Aborting clean up, Cozmo cannot find all its cubes.')
        	break
    return 0

def pickUp_cube(cube: cozmo.objects.LightCube):
    global robot
    action = robot.pickup_object(cube,use_pre_dock_pose=True, in_parallel=False, num_retries=5)
    action.wait_for_completed()
    if(action.has_failed):
    	print('ERROR: Picking cube ' + str(cube.cube_id) + ' has failed.')
    	print('MESSAGE: Aborting clean up, engaging docking procedure.')
    	return 0
    return 1
def putDown_cube(cube: cozmo.objects.LightCube):
    global robot
    action = robot.place_object_on_ground_here(cube, in_parallel=False, num_retries=2)
    action.wait_for_completed()
    return 1
def stack_cube(target: cozmo.objects.LightCube):
    global robot
    action = robot.place_on_object(target, in_parallel=False, num_retries=2)
    action.wait_for_completed()
    return 1

def clean_up_cubes():
    global cubeIDs,SIDE

    cubeIDs = []
    switch_cube_off(robot.world.get_light_cube(LightCube1Id))
    switch_cube_off(robot.world.get_light_cube(LightCube2Id))
    switch_cube_off(robot.world.get_light_cube(LightCube3Id))

    go_to_charger()
    turn_around()
    
    # I. Find first cube and put it next to charger
    cube = look_for_next_cube()
    if not cube:
    	return
    switch_cube_on(cube)
    print(cubeIDs)
    success = pickUp_cube(cube)
    if not success:
    	switch_cube_off(cube) 
    	return
    charger = go_to_charger()
    final_adjust(charger,60)
    robot.turn_in_place(degrees(SIDE*60)).wait_for_completed()
    robot.drive_straight(distance_mm(100),speed_mmps(40)).wait_for_completed()
    putDown_cube(cube)
    switch_cube_off(cube)
    # Get back in front of charger
    robot.drive_straight(distance_mm(-70),speed_mmps(40)).wait_for_completed()
    robot.turn_in_place(degrees(SIDE*180-SIDE*60)).wait_for_completed()
    robot.drive_straight(distance_mm(40),speed_mmps(40)).wait_for_completed()

    # II. Find next cube and stack on first placed cube
    cube = look_for_next_cube()
    if(cube == None):
    	return
    switch_cube_on(cube)
    print(cubeIDs)
    success = pickUp_cube(cube)
    if not success:
    	switch_cube_off(cube)
    	return
    charger = go_to_charger()
    robot.turn_in_place(degrees(SIDE*70)).wait_for_completed() #SIDE*180
    stack_cube(cubes[0])
    switch_cube_off(cube)
    # Get back in front of charger
    #robot.drive_straight(distance_mm(-70),speed_mmps(40)).wait_for_completed()
    charger = go_to_charger()
    final_adjust(charger,100,80)
    robot.turn_in_place(degrees(SIDE*180)).wait_for_completed() #-SIDE*70
    robot.set_lift_height(height=0,max_speed=10,in_parallel=False).wait_for_completed()
    #robot.drive_straight(distance_mm(40),speed_mmps(40)).wait_for_completed()

    # III. Go get the last cube and lay it in front of the others
    cube = look_for_next_cube()
    if(cube == None):
    	return
    switch_cube_on(cube)
    print(cubeIDs)
    success = pickUp_cube(cube)
    if not success:
    	switch_cube_off(cube)
    	return
    turn_around()
    charger = go_to_charger()
    final_adjust(charger,80)
    robot.turn_in_place(degrees(SIDE*60)).wait_for_completed()
    robot.go_to_object(cubes[0], distance_mm(120), in_parallel=False, num_retries=1).wait_for_completed()
    putDown_cube(cube)
    switch_cube_off(cube)
    # Get back in front of charger
    robot.drive_straight(distance_mm(-40),speed_mmps(40)).wait_for_completed()
    robot.turn_in_place(degrees(SIDE*180-SIDE*60)).wait_for_completed()
    robot.drive_straight(distance_mm(50),speed_mmps(40)).wait_for_completed()
    turn_around()
    return

########################## Charger related code ##########################

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
    #action = robot.go_to_pose(charger.pose)
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
	# Allow Cozmo to turn the least possible. Without it, Cozmo could
	# spin on itself several times or turn for instance -350 degrees
	# instead of 10 degrees. 
    global PI

    # Retreive supplementary turns (in radians)
    while(angle >= 2*PI):
        angle -= 2*PI
    while(angle <= -2*PI):
        angle += 2*PI
    # Select shortest rotation to reach the target
    if(angle > PI):
    	angle -= 2*PI
    elif(angle < -PI):
    	angle += 2*PI
    return angle

def check_tol(charger: cozmo.objects.Charger,dist_charger=40):
    # Check if the position tolerance in front of the charger is respected
    global robot,PI

    distance_tol = 5 # mm, tolerance for placement error
    angle_tol = 5*PI/180 # rad, tolerance for orientation error

    try: 
        charger = robot.world.wait_for_observed_charger(timeout=2,include_existing=True)
    except:
        print('WARNING: Cannot see the charger to verify the position.')

    # Calculate positions
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
    # dist_charger in mm, distance if front of charger
    c_coord[0] -=  dist_charger*math.cos(c_zRot)
    c_coord[1] -=  dist_charger*math.sin(c_zRot)

    # Direction and distance to target position (in front of charger)
    distance = math.sqrt((c_coord[0]-r_coord[0])**2 + (c_coord[1]-r_coord[1])**2 + (c_coord[2]-r_coord[2])**2)

    if(distance < distance_tol and math.fabs(r_zRot-c_zRot) < angle_tol):
    	return 1
    else: 
    	return 0

def final_adjust(charger: cozmo.objects.Charger,dist_charger=40,speed=20,critical=False):
    # Final adjustement to properly face the charger.
    # The position can be adjusted several times if 
    # the precision is critical, i.e. when climbing
    # back onto the charger.  
    global robot,PI

    while(True):
        # Calculate positions
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
	    # dist_charger in mm, distance if front of charger
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
	    robot.drive_straight(distance_mm(distance),speed_mmps(speed)).wait_for_completed()
	    # Face the charger
	    angle = clip_angle((c_zRot-theta_t))
	    robot.turn_in_place(radians(angle)).wait_for_completed()

        # In case the robot does not need to climb onto the charger
	    if not critical:
	        break
	    elif(check_tol(charger,dist_charger)):
	    	print('CHECK: Robot aligned relativ to the charger.')
	    	break
    return

def restart_procedure(charger: cozmo.objects.Charger):
    global robot

    robot.stop_all_motors()
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.pose.invalidate()
    charger.pose.invalidate()
    print('ABORT: Driving away')
    #robot.drive_straight(distance_mm(150),speed_mmps(80),in_parallel=False).wait_for_completed()
    robot.drive_wheels(80,80,duration=2)
    turn_around()
    robot.set_lift_height(height=0,max_speed=10,in_parallel=True).wait_for_completed()
    # Restart procedure
    get_on_charger()
    return

def get_on_charger():
    global robot,pitch_threshold

    robot.set_head_angle(degrees(0),in_parallel=False).wait_for_completed()
    pitch_threshold = math.fabs(robot.pose_pitch.degrees)
    pitch_threshold += 1 # Add 1 degree to threshold
    print('Pitch threshold: ' + str(pitch_threshold))

    # Drive towards charger
    go_to_charger()

    # Let Cozmo first look for the charger once again. The coordinates
    # tend to be too unprecise if an old coordinate system is kept.
    if robot.world.charger is not None and robot.world.charger.pose.is_comparable(robot.pose):
        robot.world.charger.pose.invalidate()
    charger = find_charger()

    # Adjust position in front of the charger
    final_adjust(charger,critical=True)
    
    # Turn around and start going backward
    turn_around()
    robot.drive_wheel_motors(-120,-120)
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.set_head_angle(degrees(0),in_parallel=True).wait_for_completed()

    # This section allow to wait for Cozmo to arrive on its charger
    # and detect eventual errors. The whole procedure will be restarted
    # in case something goes wrong.
    timeout = 1 # seconds before timeout
    t = 0
    # Wait for back wheels to climb on charger
    while(True):
        time.sleep(.1)
        t += 0.1
        if(t >= timeout):
            print('ERROR: robot timed out before climbing on charger.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) >= pitch_threshold):
            print('CHECK: backwheels on charger.')
            break
    # Wait for front wheels to climb on charger
    timeout = 2
    t = 0
    while(True):
        time.sleep(.1)
        t += 0.1
        if(math.fabs(robot.pose_pitch.degrees) > 20 or t >= timeout):
            # The robot is climbing on charger's wall -> restart
            print('ERROR: robot climbed on charger\'s wall or timed out.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) < pitch_threshold):
            print('CHECK: robot on charger, backing up on pins.')
            robot.stop_all_motors()
            break

    # Final backup onto charger's contacts
    robot.set_lift_height(height=0,max_speed=10,in_parallel=True).wait_for_completed()
    robot.backup_onto_charger(max_drive_time=3)
    if(robot.is_on_charger):
    	print('PROCEDURE SUCCEEDED')
    else: 
    	restart_procedure(charger)
    	return

    # Celebrate success
    robot.drive_off_charger_contacts().wait_for_completed()
    celebrate(robot) # A small celebration where only the head moves
    robot.backup_onto_charger(max_drive_time=3)
    return

########################## Battery related code ##########################

def check_battery():
	global robot

	if(robot.battery_voltage < 3.5):
		print('Battery is low, directly docking to charger without cleaning up.')
		return 1
	else:
		return 0

########################## General code ##########################

def turn_around():
    global robot
    robot.turn_in_place(degrees(-178)).wait_for_completed()
    return

########################## Main ##########################

robot = None

def init_robot(cozmo_robot: cozmo.robot.Robot):
    global robot
    robot = cozmo_robot

def execute_procedure():
    low_battery = check_battery()
    if not low_battery:
        clean_up_cubes()
    get_on_charger()
    return

def cozmo_program(cozmo_robot: cozmo.robot.Robot):
    global robot
    init_robot(cozmo_robot)

    # Get off charger if on it
    if(robot.is_on_charger):
    	robot.drive_off_charger_contacts().wait_for_completed()
    	robot.drive_straight(distance_mm(110),speed_mmps(80)).wait_for_completed()

    execute_procedure()
    return

if __name__ == "__main__":
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    cozmo.run_program(cozmo_program,use_viewer=True,use_3d_viewer=False)
