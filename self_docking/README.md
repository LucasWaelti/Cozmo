# Cozmo - Collecting Cubes And Self Docking on Charger
This program enables Cozmo to drive off its charger, collect its cubes by placing them near its charger and then climbing back onto its charger when it is done. Cozmo will directly try to climb back onto its charger if the battery is low and will ignore its cubes. No further help or markers are required. It is possible that Cozmo does not find a cube or its charger, so it will ask for help if needed. Just place the required object or Cozmo in a position where Cozmo can keep working and let it finish its job! If finding any cube takes too long, Cozmo will give up and go back to its charger. 

## Optimal Setup When Starting
Cozmo should be on its charger when starting (but it will work otherwise too). The cubes must not be stacked or rolled and should be located somewhere in front of the charger. 

This video demonstrates how things work: 
https://youtu.be/xfAxPHdetH0
The video is sped up 4 times and there are therefore no sound. 

## Error Detection
Different strategies were implemented to detect if Cozmo is succeeding in its task or if a problem occured while running the program. This task is not easy and is prone to errors, that can occur at different levels. The error handling is based on timeouts and unexpected 
positions of the robot as well as action failures to determine if the current process has to be aborted/restarted or not. 

## Improvements (TODO)
- Support already stacked or rolled cubes when cleaning up. 
- Stack cubes as a pyramid instead of current configuration. 
- Detect if backup_onto_charger() has succeeded (not possible?).
- Speed up some processes. 
