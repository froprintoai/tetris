# tetris by pygame
tetris implemented using pygame
There are three modes to play, single play, online play and cpu play.
Note that server should be deployed at some place if you want to play online mode.

# DEMO
Menu Screen
![Image of Demo Play](https://github.com/froprintoai/tetris/blob/master/img/menu.png?raw=true)
Single Play
![Image of Demo Play](https://github.com/froprintoai/tetris/blob/master/img/demo.png?raw=true)
Online Play
![Image of Demo Play](https://github.com/froprintoai/tetris/blob/master/img/online.png?raw=true)
Play with AI
![Image of Demo Play](https://github.com/froprintoai/tetris/blob/master/img/with_cpu.png?raw=true)
 
# Features
This version of tetris basically follows the rule from Tetris DS.
Super Rotation System is used to determine how each rotation affects the current mino's position. 

# How to play
```
python tetris.py
```

To play online mode, you should edit network configuration in src/server/main.go, src/network_config.py, and deploy the execution file created by following command.
```
go build
```

To play the mode of challenge AI, make sure there is a pit file in the same directory as tetris.py.
The default pit file, tetris-best_475.pit, is the model trained by [here](https://github.com/froprintoai/tetris_gym_env). 

# Requisite
pygame
numpy
torch
gym
 
# Key Mapping

a ... move left

s ... move right

w ... hard drop

z ... soft drop

space bar ... hold

right arrow ... rotate clockwise

left arrow ... rotate counterclockwise
  
# License
This software is released under the MIT License, see LICENSE.txt.
