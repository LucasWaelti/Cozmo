'''
Let Cozmo help you while building some stuff!
With this program, Cozmo will play the role of a level.
Just put Cozmo on the surface you would like to adjust
and give Cozmo a check when the job is done!
'''
import time 
import math

import cozmo
from cozmo.util import degrees, radians, distance_mm, speed_mmps
from cozmo.objects import LightCube1Id, LightCube2Id, LightCube3Id
from cozmo.lights import Light, Color

global robot 

global delta

global MAX_ANGLE
global LIFT_POSITION

def play_animation(robot: cozmo.robot.Robot, anim_trig, body = False, lift = False, parallel = False):
    # anim_trig = cozmo.anim.Triggers."Name of trigger" (this is an object)
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.anim.html#cozmo.anim.Triggers" for animations' triggers
    # Refer to "http://cozmosdk.anki.com/docs/generated/cozmo.robot.html#cozmo.robot.Robot.play_anim_trigger" for playing the animation

    robot.play_anim_trigger(anim_trig,loop_count = 1, in_parallel = parallel,
                            num_retries = 0, use_lift_safe = False,
                            ignore_body_track = body, ignore_head_track=False,
                            ignore_lift_track = lift).wait_for_completed()

def celebrate(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.CodeLabCelebrate  
    play_animation(robot,trigger,body=True,lift=True,parallel=True)




def setMaxAngle(max_ang=20):
	global MAX_ANGLE
	MAX_ANGLE = max_ang

def calculateColor(abs_angle=0):
	'''
		This function will attribute a color corresponding to the error abs_angle.
		The maximun error is set at MAX_ANGLE
	'''
	# RGB tuple (0-255)
	global MAX_ANGLE
	slope = 255/MAX_ANGLE

	if(abs_angle > 20):
		abs_angle = 20

	G = 255 - slope*abs_angle
	G = int(G)
	R = slope*abs_angle
	R = int(R)
	if(abs_angle <= MAX_ANGLE/2):
		B = slope*abs_angle
	else:
		B = 255 - slope*abs_angle
	B = int(B)

	color = Color(rgb = (R,G,B))
	return color 

def getColor(pitch_angle=0):
	abs_angle = math.fabs(pitch_angle)
	color = calculateColor(abs_angle)
	return color

def setBackpackColors():
	global robot,delta,LIFT_POSITION

	print("Robot\'s pitch in radians: ")
	while(True):
		pitch = robot.pose_pitch.degrees
		pitch -= delta
		#print(pitch)

		backLights = Light(getColor(pitch))
		lightOff = Light(Color(rgb=(0,0,0)))
		if(pitch > 0.04):#Forward
			robot.set_backpack_lights(lightOff,backLights,backLights,lightOff,lightOff)
		elif(pitch < -0.04):
			robot.set_backpack_lights(lightOff,lightOff,backLights,backLights,lightOff)
		else:
			robot.set_center_backpack_lights(backLights)
		
		if(math.fabs(robot._lift_position.ratio - LIFT_POSITION) > 0.05):
			print('Check detected!')
			break
		time.sleep(.1)
	robot.set_backpack_lights_off()
	return

def init(r: cozmo.robot.Robot):
	global robot,delta
	robot = r 
	
	setMaxAngle()

	robot.set_head_angle(cozmo.util.Angle(degrees=0), accel=10.0, max_speed=10.0, 
		duration=0.0, warn_on_clamp=True, in_parallel=False, num_retries=0).wait_for_completed()
	robot.pose.invalidate()
	delta = robot.pose_pitch.degrees
	return	

def level(robot: cozmo.robot.Robot):
	global LIFT_POSITION
	init(robot)
	robot.set_lift_height(0.8).wait_for_completed()
	LIFT_POSITION = robot._lift_position.ratio
	setBackpackColors()
	robot.set_lift_height(0.0).wait_for_completed()
	celebrate(robot)
	return

if __name__ == '__main__':
	cozmo.run_program(level,use_viewer=False,use_3d_viewer=False)