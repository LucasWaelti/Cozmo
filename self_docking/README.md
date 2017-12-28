# Cozmo Self Docking on Charger
This script allows Cozmo to autonomously find its charger, drive towards it and then maneuver to get onto it. 
Some custom approach method had to be implemented as the default approach functions provided by Anki do not offer a sufficient precision. 

## Error Detection
Different strategies were implemented to detect if Cozmo is succeeding in its task or if a problem occured while running the program. 
This task is not easy and is prone to errors, that can occur at different levels. The error handling is based on timeouts and unexpected 
positions of the robot to determine if the whole procedure has to be aborted and restarted or not. 

### TODO:
The cubes clean up is still a work in progress. It is roughly half way implemented. 
