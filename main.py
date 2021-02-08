import sys
import math

class Config:
    Unit_Length = 100

class GameEnv:
    Max_Yaw_Angle = 18
    Max_Engine_Power = 100
    Map_Width = 16000
    Map_Height = 9000

    @staticmethod
    def calc_acceleration(engine_power: int, speed: float)->float:
        acceleration = -0.15 * speed + engine_power
        if acceleration < 0:
            acceleration = 0

        return acceleration    

    @staticmethod
    def calc_engine_power(acceleration: float, speed: float)->int:
        return int(acceleration + 0.15 * (speed - acceleration))

class Tools:

    @staticmethod
    def debug(msg):
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        print(f"Debug: {msg}", file=sys.stderr, flush=True)

    @staticmethod
    def limit_angle(angle_deg=None, angle_rad=None)->float:
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
    def conv_cartesian_polar(x=None, y=None, angle=None, length=None):    
        if x != None and y != None:
            out_angle = Tools.calc_vector_angle(x=x, y=y)
            out_angle = Tools.limit_angle(angle_deg=out_angle)    
            out_length = Tools.calc_dist(x1=x, y1=y)
            return out_angle, out_length
        elif angle !=None and length != None:
            angle_rad = Tools.conv_deg_to_rad(angle)
            out_x = math.cos(angle_rad) * length
            out_y = math.sin(angle_rad) * length
            return out_x, out_y
        return NotImplemented

    @staticmethod
    def calc_dist(x1=None, y1=None, x2=None, y2=None, pos1=None, pos2=None, vector=None)->float:
        delta_x = 0
        delta_y = 0

        if x1 != None and y1 != None and x2 != None and y2 != None:
            delta_x = x2 - x1
            delta_y = y2 - y1
        elif pos1 != None and pos2 != None:
            delta_x = pos2.x - pos1.x
            delta_y = pos2.y = pos1.y
        elif vector != None:
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

        return Tools.limit_angle(angle_deg=output)

class Vector:
    def __init__(self, x=0, y=0, angle=0, length=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length

    def __str__(self):
        return f"{int(round(self.x, 0))} {int(round(self.y, 0))}"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x + other, self.y + other)
        elif isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x - other, self.y - other)
        elif isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(other * self.x, other * self.y)
        elif isinstance(other, Vector):
            return NotImplemented
        else:
            return NotImplemented
         
    def update(self, x=None, y=None, angle=None, length=None, pos1=None, pos2=None):
        if x != None and y != None:
            self.x = x
            self.y = y
            self.angle = Tools.calc_vector_angle(x=self.x, y=self.y)
            self.length = Tools.calc_dist(x1=0, y1=0, x2=self.x, y2=self.y)
        elif angle !=None and length != None:
            self.angle = angle
            self.length = length
            angle_rad = Tools.conv_deg_to_rad(self.angle)
            self.x = math.cos(angle_rad) * self.length
            self.y = math.sin(angle_rad) * self.length
        elif pos1 != None and pos2 != None:
            if pos1.x != None and pos1.y != None and pos2.x != None and pos2.y != None:
                self.x = pos2.x - pos1.x
                self.y = pos2.y - pos1.y
                self.angle = Tools.calc_vector_angle(x=self.x, y=self.y)
                self.length = Tools.calc_dist(x1=0, y1=0, x2=self.x, y2=self.y)
        else:
            return
        
        self.angle = Tools.limit_angle(angle_deg=self.angle)
        

    def copy(self, new_vector):
        self.x = new_vector.x
        self.y = new_vector.y

class CheckPoint:
    def __init__(self, x, y, radius):
        self.pos = Vector(x, y)
        self.radius = radius

class Pod:
    def __init__(self):
        self.position = Vector()
        self.pos_prev = Vector()

        # velocity is a vector
        # velocity angle is absolute (ref to horizon)
        # negative angle means toward upper screen
        # position angle means toward lower screen
        self.velocity = Vector()
        self.vel_prev = Vector()
        self.acceleration = 0

        # chkpt is the vector from pod to check point
        # chkpt.angle is the absolute angle (ref to horizon)
        # negative angle means the vector points toward upper screen
        # positive angle means the vector points toward lower screen
        self.chkpt = Vector()

        # orient is vector of the pod orientation
        # orient.angle is the absolute angle of the pod orientation  (ref to horizon)
        self.orient_prev = Vector()
        self.orient = Vector()

        self.next_direction = Vector()
        self.engine_power = 0

    def set_direction(self, angle=0, engine_power=0):
        # angle = (0: forward, < 0: turn left, > 0: turn right)
        if angle > GameEnv.Max_Yaw_Angle:
            angle = GameEnv.Max_Yaw_Angle
        elif angle < -GameEnv.Max_Yaw_Angle:
            angle = GameEnv.Max_Yaw_Angle

        self.next_direction.update(angle=self.orient.angle - angle, length=Config.Unit_Length)
        self.next_direction = self.next_direction + self.position
        self.engine_power = engine_power

    def update(self, x, y, chkpt_x, chkpt_y, chkpt_angle=None):
        self.pos_prev.copy(self.position)
        self.position.update(x=x, y=y)

        self.vel_prev.copy(self.velocity)
        self.velocity.update(pos1=self.pos_prev, pos2=self.position)
        self.engine_power = GameEnv.calc_engine_power(acceleration=self.acceleration, speed=self.velocity.length)        

        self.chkpt.update(pos1=self.position, pos2=Vector(chkpt_x, chkpt_y))

        if chkpt_angle != None:       
            self.orient_prev.copy(self.orient)     
            self.orient.update(angle=self.chkpt.angle + chkpt_angle, length=Config.Unit_Length)

def main():
    player = Pod()
    opponent = Pod()    

    player.orient.angle = 0
    # game loop
    while True:
        prev_orient = player.orient.angle
        # next_checkpoint_x: x position of the next check point
        # next_checkpoint_y: y position of the next check point
        # next_checkpoint_dist: distance to the next checkpoint
        # next_checkpoint_angle: angle between your pod angle_to_chkpt and the direction of the next checkpoint
        x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
        opponent_x, opponent_y = [int(i) for i in input().split()]

        # the game angle is opposite of our convention
        next_checkpoint_angle = -next_checkpoint_angle

        player.update(x=x, y=y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y, chkpt_angle=next_checkpoint_angle)
        opponent.update(x=opponent_x, y=opponent_y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y)

        player.set_direction(0, 100)
        
        Tools.debug(f"yaw: {abs(player.orient.angle-prev_orient):.1f} speed {player.velocity.length}")

        # You have to output the target position
        # followed by the engine_power (0 <= engine_power <= 100)
        # i.e.: "x y engine_power"
        print(f"{player.next_direction} {player.engine_power}")

main()