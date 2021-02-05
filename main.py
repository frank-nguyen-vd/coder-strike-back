import sys
import math

class Env:
    Max_Yaw_Angle = 16
    Max_Acceleration = 650

def debug(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(f"Debug: {msg}", file=sys.stderr, flush=True)

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

prev_x = None
prev_y = None
velocity = None
thrust = 100
max_acceleration = 0
prev_velocity = 0

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]


    if velocity == None:
        velocity = 0
    else:
        velocity = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
    prev_x = x
    prev_y = y

    if velocity > 250 and next_checkpoint_dist < 1000:
        thrust = 0
    elif abs(next_checkpoint_angle) >= 60:
        thrust = 30
    elif abs(next_checkpoint_angle) >= 45:
        thrust = 60
    elif abs(next_checkpoint_angle) >= 20:
        thrust = 80
    else:
        thrust = 100

    # You have to output the target position
    # followed by the power (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(f"{str(next_checkpoint_x)} {str(next_checkpoint_y)} {thrust}")
