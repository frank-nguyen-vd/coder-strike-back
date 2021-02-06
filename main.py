import sys
import math

def debug(msg):
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(f"Debug: {msg}", file=sys.stderr, flush=True)

class Tools:
    @staticmethod
    def limit_angle(angle_deg=None, angle_rad=None):
        if angle_deg != None:
            if angle_deg > 180:
                return angle_deg - 360
            if angle_deg < -180:
                return angle_deg + 360
            return angle_deg

        if angle_rad != None:
            if angle_rad > math.pi:
                return angle_rad - math.pi * 2
            if angle_rad < -math.pi:
                return angle_rad + math.pi * 2
            return angle_rad

    @staticmethod
    def calc_dist(x1=None, y1=None, x2=None, y2=None, pos1=None, pos2=None, vector=None):
        delta_x = 0
        delta_y = 0

        if x1 and y1 and x2 and y2:
            delta_x = x2 - x1
            delta_y = y2 - y1
        elif pos1 and pos2:
            delta_x = pos2.x - pos1.x
            delta_y = pos2.y = pos1.y
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
            output = 180 + Tools.conv_rad_to_deg(math.atan(y / x))
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
    def __init__(self):
        self.x = None
        self.y = None
        self.angle = None
        self.length = None

    def update(self, x=None, y=None, angle=None, length=None, pos1=None, pos2=None):
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
        elif pos1 and pos2:
            self.x = pos2.x - pos1.x
            self.y = pos2.y - pos1.y
            self.angle = Tools.calc_vector_angle(x=self.x, y=self.y)
            self.length = Tools.calc_dist(x1=0, y1=0, x2=self.x, y2=self.y)        

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
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y     

    def copy(self, new_pos):
        self.x = new_pos.x
        self.y = new_pos.y

    def update(self, x, y):
        self.x = x
        self.y = y

class CheckPoint:
    def __init__(self, x, y, radius):
        self.pos = Position(x, y)
        self.radius = radius

class Pod:
    def __init__(self):
        self.position = Position()
        self.pos_prev = Position()

        # negative angle means toward upper screen
        # position angle means toward lower screen
        self.velocity = Vector()
        self.vel_prev = Vector()
        self.acceleration = 0

        # chkpt is the vector from pod to check point
        # negative angle means the vector points toward upper screen
        # positive angle means the vector points toward lower screen
        self.chkpt = Vector()

        # orientation is the angle between pod orientation and vector chkpt
        self.orientation = 0

    def update(self, x, y, chkpt_x, chkpt_y, orientation=None):
        self.pos_prev.copy(self.position)
        self.position.update(x=x, y=y)

        self.vel_prev.copy(self.velocity)
        self.velocity.update(pos1=self.pos_prev, pos2=self.position)

        self.chkpt.update(pos1=self.position, pos2=Position(chkpt_x, chkpt_y))

        self.orientation = orientation        

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

    player.update(x=x, y=y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y, orientation=next_checkpoint_angle)
    opponent.update(x=opponent_x, y=opponent_y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y)
    
    # You have to output the target position
    # followed by the engine_power (0 <= engine_power <= 100)
    # i.e.: "x y engine_power"
    engine_power = 50
    print(f"{str(next_checkpoint_x)} {str(next_checkpoint_y)} {engine_power}")
