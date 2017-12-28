# Cozmo Self Docking on Charger
This script allows Cozmo to autonomously find its charger, drive towards it and then maneuver to get onto it. 
Some custom approach method had to be implemented as the default approach functions do not offer a sufficient precision. 

## Error Detection
Different strategies were implemented to detect if Cozmo is succeeding in its task or if a problem occured while running the program. 
This task is not easy and is prone to errors, occuring at different possible levels. The error handling is based on timeouts and unexpected 
position of the robot to determine if the whole procedure has to be restarted or not. 
