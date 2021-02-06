import sys
import math

def debug(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(f"Debug: {msg}", file=sys.stderr, flush=True)

class Tools:
    @staticmethod
    def calc_dist(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    @staticmethod
    def conv_rad_to_deg(angle_rad):
        return angle_rad / math.pi * 180

class GameEnv:
    Max_Yaw_Angle = 16
    Max_Engine_Power = 100
    Map_Width = 16000
    Map_Height = 9000

    @staticmethod
    def calc_acceleration(engine_power, speed):
        acceleration = -0.15 * speed + engine_power
        if acceleration < 0:
            acceleration = 0

        return acceleration
    

class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y        

class CheckPoint:
    def __init__(self, x, y, radius):
        self.pos = Position(x, y)
        self.radius = radius

class Pod:
    def __init__(self, x=None, y=None, angle_to_chkpt=None, dist_to_chkpt=None, speed=None, acceleration=None):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y

        self.speed = speed
        self.prev_speed = speed

        self.acceleration = acceleration

        # trajectory is the direction of velocity
        # negative angle means toward upper screen
        # position angle means toward lower screen
        self.trajectory = 0

        self.angle_to_chkpt = angle_to_chkpt

        self.dist_to_chkpt = dist_to_chkpt

    def update_speed(self):
        self.prev_speed = self.speed
        if self.prev_x == None or self.prev_y == None:
            self.speed = 0
        else:
            self.speed = Tools.calc_dist(x1=self.prev_x, y1=self.prev_y, x2=self.x, y2=self.y)

    def update_trajectory(self):
        if self.prev_x == None or self.prev_y == None:
            self.trajectory = 0
        else:
            delta_x = self.x - self.prev_x
            delta_y = self.y - self.prev_y

            if delta_x > 0:
                self.trajectory = Tools.conv_rad_to_deg(math.atan(delta_y / delta_x))
            elif delta_x < 0:
                self.trajectory = -(180 - Tools.conv_rad_to_deg(math.atan(delta_y / delta_x)))
            elif delta_y > 0:
                self.trajectory = 90
            elif delta_y < 0:
                self.trajectory = -90
            else:
                self.trajectory = 0

            if self.trajectory < -180:
                self.trajectory = 360 + self.trajectory


    def update(self, x, y, chkpt_x, chkpt_y, angle_to_chkpt=None):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = x        
        self.y = y



        if self.prev_speed == None:
            self.acceleration = 0
        else:
            self.acceleration = self.speed - self.prev_speed

        self.angle_to_chkpt = angle_to_chkpt

        self.dist_to_chkpt = Tools.calc_dist(x1=x, y1=y, x2=chkpt_x, y2=chkpt_y)

player = Pod()
opponent = Pod()    

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod angle_to_chkpt and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    player.update(x=x, y=y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y, angle_to_chkpt=next_checkpoint_angle)
    opponent.update(x=opponent_x, y=opponent_y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y)
    
    debug(f"game dist {next_checkpoint_dist} calc {player.dist_to_chkpt}")

    # You have to output the target position
    # followed by the engine_power (0 <= engine_power <= 100)
    # i.e.: "x y engine_power"
    engine_power = 50
    print(f"{str(next_checkpoint_x)} {str(next_checkpoint_y)} {engine_power}")
