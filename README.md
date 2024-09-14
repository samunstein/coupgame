Coup game

# How to run
Set wanted amount of players in config.py. Then run servermain.py, and as many clientmain.py as you configured. 

# How to code own logic
Go to game/logic/, and look at ClientLogic abstract class. Make a class that implements all the methods, and set it as the logic in clientmain.py. 

Sorry, I'll come up with some way of doing it without having to edit clientmain.py and without involving circular imports. At some point.