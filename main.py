import sys
import math

def debug(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(f"Debug: {msg}", file=sys.stderr, flush=True)

class Tools:
    @staticmethod
    def calc_dist(x1=None, y1=None, x2=None, y2=None, point1=None, point2=None, vector=None):
        delta_x = 0
        delta_y = 0

        if x1 and y1 and x2 and y2:
            delta_x = x2 - x1
            delta_y = y2 - y1
        elif pointA and pointB:
            delta_x = point2.x - point1.x
            delta_y = point2.y = point1.y
        elif vector:
            delta_x = vector.x
            delta_y = vector.y

        return math.sqrt(delta_x**2 + delta_y**2)
    
    @staticmethod
    def conv_rad_to_deg(angle_rad):
        return angle_rad / math.pi * 180

    @staticmethod
    def conv_deg_to_rad(angle_deg):
        return angle_deg / 180 * math.pi

    @staticmethod
    def calc_vector_angle(x, y):
        output = 0

        if x > 0:
            output = Tools.conv_rad_to_deg(math.atan(y / x))
        elif x < 0:
            output = 180 + Tools.conv_rad_to_deg(math.atan(y / x)))
        elif y > 0:
            output = 90
        elif y < 0:
            output = -90

        if output > 180:
            output = output - 360
        elif output < -180:
            output = output + 360

        return output                
class Vector:
    def __init__(self, x=None, y=None, angle=None, length=None):
        self.x = None
        self.y = None
        self.angle = None
        self.length = None
        self.update(x=x, y=y, angle=angle, length=length)

    def update(self, x=None, y=None, angle=None, length=None):
        if x and y:
            self.x = x
            self.y = y
            self.angle = Tools.calc_vector_angle(x=self.x, y=self.y)
            self.length = Tools.calc_dist(x1=0, y1=0, x2=self.x, y2=self.y)
        elif angle and length:
            self.angle = angle
            self.length = length
            angle_rad = Tools.conv_deg_to_rad(self.angle)
            self.x = math.cos(angle_rad) * self.length
            self.y = math.sin(angle_rad) * self.length

    def copy(self, new_vector):
        self.x = new_vector.x
        self.y = new_vector.y

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
