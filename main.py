import sys
import math

GameTurn = 0

class Config:
    Unit_Length = 1000

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
        elif x1 != None and y1 != None:
            delta_x = x1
            delta_y = y1

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
    def __init__(self, x=None, y=None, angle=None, length=None, pos1=None, pos2=None):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.length = 0
        self.update(x=x, y=y, angle=angle, length=length, pos1=pos1, pos2=pos2)

    def __str__(self):
        return f"{int(round(self.x, 0))} {int(round(self.y, 0))}"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Vector(x=self.x + other, y=self.y + other)
        elif isinstance(other, Vector):
            return Vector(x=self.x + other.x, y=self.y + other.y)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Vector(x=self.x - other, y=self.y - other)
        elif isinstance(other, Vector):
            return Vector(x=self.x - other.x, y=self.y - other.y)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(x=other * self.x, y=other * self.y)
        elif isinstance(other, Vector):
            return NotImplemented
        else:
            return NotImplemented
         
    def update(self, x=None, y=None, angle=None, length=None, pos1=None, pos2=None):
        if x != None and y != None:
            self.x = x
            self.y = y
            self.angle, self.length = Tools.conv_cartesian_polar(x=self.x, y=self.y)
        elif angle !=None and length != None:
            self.angle = angle
            self.length = length
            self.x, self.y = Tools.conv_cartesian_polar(angle=self.angle, length=self.length)
        elif pos1 != None and pos2 != None:
            if pos1.x != None and pos1.y != None and pos2.x != None and pos2.y != None:
                self.x = pos2.x - pos1.x
                self.y = pos2.y - pos1.y
                self.angle, self.length = Tools.conv_cartesian_polar(x=self.x, y=self.y)
            else:
                return NotImplemented
        elif length != None:
            if self.length != 0:
                scaler = length / self.length
                self.x *= scaler
                self.y *= scaler
                self.length = length
        elif pos1 != None:
            self.x = pos1.x
            self.y = pos1.y
            self.angle, self.length = Tools.conv_cartesian_polar(x=self.x, y=self.y)
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
        self.position: Vector = None
        self.pos_prev: Vector = None

        # velocity is a vector
        # velocity angle is absolute (ref to horizon)
        # negative angle means toward upper screen
        # positive angle means toward lower screen
        self.velocity: Vector = None
        self.vel_prev: Vector = None

        # accleration is a vector
        # acceleration angle is absolute (ref to horizon)
        # negative angle means toward upper screen
        # positive angle means toward lower screen
        self.acceleration: Vector = Vector(x=0, y=0)
        self.acc_prev: Vector = Vector(x=0, y=0)

        # chkpt is the vector from pod to check point
        # chkpt.angle is the absolute angle (ref to horizon)
        # negative angle means the vector points toward upper screen
        # positive angle means the vector points toward lower screen
        self.chkpt: Vector = Vector()

        # orient is vector of the pod orientation
        # orient.angle is the absolute angle of the pod orientation  (ref to horizon)
        self.orient_prev: Vector = Vector()
        self.orient: Vector = Vector()

        # next direction and engine power are the output param to pilot the pod
        self.next_direction: Vector = Vector()        
        self.engine_power: int = None
        self.engine_power_prev: int = None

    def pilot(self, yaw_angle=0, engine_power=0):
        # yaw angle = (0: forward, < 0: turn left, > 0: turn right)
        if yaw_angle > GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle
        elif yaw_angle < -GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle

        self.acceleration.update(
            angle=self.orient.angle + yaw_angle, 
            length=GameEnv.calc_acceleration(speed=self.velocity.length, engine_power=engine_power))
        self.next_direction = self.acceleration + self.position
        self.engine_power = engine_power

    def update_position(self, x, y):
        if self.position == None:
            self.position = Vector(x=x, y=y)
            self.pos_prev = Vector(pos1=self.position)            
        else:
            self.pos_prev.copy(self.position)
            self.position.update(x=x, y=y)

    def update_velocity(self):
        if self.velocity == None:
            self.velocity = Vector(pos1=self.pos_prev, pos2=self.position)
            self.vel_prev = Vector(pos1=self.velocity)            
        else:
            self.vel_prev.copy(self.velocity)
            self.velocity.update(pos1=self.pos_prev, pos2=self.position)
            
    def update_acceleration(self):
        self.acc_prev = self.velocity - self.vel_prev

    def update_checkpoint(self, x=None, y=None):
        if x != None and y != None:
            self.chkpt.update(pos1=self.position, pos2=Vector(x, y))        

    def update_orientation(self, chkpt_angle=None):
        self.orient_prev.copy(self.orient)
        if chkpt_angle != None:                 
            self.orient.update(angle=self.chkpt.angle + chkpt_angle, length=Config.Unit_Length)
        else:
            self.orient.copy(self.acc_prev)
            self.orient.update(length=Config.Unit_Length)

    def update_engine_power(self):
        if self.engine_power == None:
            self.engine_power_prev = GameEnv.calc_engine_power(acceleration=self.acc_prev.length, speed=self.vel_prev.length)
        else:
            self.engine_power_prev = self.engine_power

    def update(self, x, y, chkpt_x, chkpt_y, chkpt_angle=None):        
        self.update_position(x=x, y=y)
        self.update_checkpoint(x=chkpt_x, y=chkpt_y)
        self.update_velocity()
        self.update_acceleration()
        self.update_orientation(chkpt_angle=chkpt_angle)
        self.update_engine_power()

class Simulation:
    @staticmethod
    def next_pos(pod: Pod, yaw_angle: float, engine_power: int)->Vector:
        # angle = (0: forward, < 0: turn left, > 0: turn right)
        if yaw_angle > GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle
        elif yaw_angle < -GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle

        acc_angle = pod.orient.angle + yaw_angle        
        acc_length = GameEnv.calc_acceleration(speed=pod.velocity.length, engine_power=engine_power)
        thrust_dir = Vector(angle=acc_angle, length=acc_length)        
        return (pod.velocity + thrust_dir) + pod.position

    @staticmethod
    def last_pos(pod: Pod, actions: list)->Vector:
        output = copy.deepcopy(pod)
        for action in actions:
            yaw_angle = action[0]
            engine_power = action[1]
            new_pos = Simulation.next_pos(pod=output, yaw_angle=yaw_angle, engine_power=engine_power)
            output.update(x=new_pos.x, y=new_pos.y)
        return output.position


class GA_Controller:
    N_Genes = 5
    Population = 10
    Death_Rate = 0.2
    Mutation_Rate = 0.01
    
    def __init__(self):
        random.seed()       

    def init_genome(self):
        return [[random.random(), random.random()] for i in range(0, self.N_Genes)]

    def conv_genome_to_actions(self, genome: list):
        actions = []
        for (encoded_yaw_angle, encoded_engine_power) in genome:
            yaw_angle = encoded_yaw_angle * (GameEnv.Max_Yaw_Angle - (-GameEnv.Max_Yaw_Angle)) + (-GameEnv.Max_Yaw_Angle)
            engine_power = int(encoded_engine_power * GameEnv.Max_Engine_Power)
            actions.append([yaw_angle, engine_power])
        return actions

def main():
    player = Pod()
    opponent = Pod()    
    global GameTurn

    # game loop
    while True:        
        GameTurn += 1
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
        
        if GameTurn == 1:
            set_angle = 0
        else:
            set_angle=90
        set_engine_power=100
        
        player.pilot(yaw_angle=set_angle, engine_power=set_engine_power)
        
        Tools.debug(f"chkpt angle {player.chkpt.angle:.0f} yaw angle {set_angle:.0f} next angle {player.next_direction.angle:.0f}")        
        
        next_pos = Simulation.next_pos(
            curr_pos=player.position,
            curr_vel=player.velocity,
            curr_angle=player.orient.angle,
            yaw_angle=set_angle,
            engine_power=set_engine_power
        )
        Tools.debug(f"curr pos {x} {y} new pos {next_pos.x:.0f} {next_pos.y:.0f}")
        

        # You have to output the target position
        # followed by the engine_power (0 <= engine_power <= 100)
        # i.e.: "x y engine_power"
        print(f"{player.next_direction} {player.engine_power}")

main()