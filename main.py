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

class GameEnv:
    Max_Engine_Power = 100

    @staticmethod
    def calc_acceleration(engine_power, speed):
        max_acceleration = 1.2 * engine_power
        acceleration = -0.15 * speed + max_acceleration
        if acceleration < 0:
            acceleration = 0
    

class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y        

class CheckPoint:
    def __init__(self, x, y, radius):
        self.pos = Position(x, y)
        self.radius = radius

class Pod:
    def __init__(self, x=None, y=None, orientation=None, dist_to_chkpt=None, speed=None, acceleration=None):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y

        self.speed = speed
        self.prev_speed = speed

        self.acceleration = acceleration
        self.orientation = orientation
        self.dist_to_chkpt = dist_to_chkpt

    def update(self, x, y, orientation=None, dist_to_chkpt=None):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x = x        
        self.y = y

        self.prev_speed = self.speed
        if self.prev_x == None or self.prev_y == None:
            self.speed = 0
        else:
            self.speed = Tools.calc_dist(x1=self.prev_x, y1=self.prev_y, x2=self.x, y2=self.y)

        if self.prev_speed == None:
            self.acceleration = 0
        else:
            self.acceleration = self.speed - self.prev_speed

        self.orientation = orientation

        self.dist_to_chkpt = dist_to_chkpt

    
class Probe:
    def __init__(self):
        self.player = Pod()
        self.opponent = Pod()
        self.max_speed = 0
        self.max_acceleration = 0

    def update_game_info(self, player_x, player_y, opponent_x, opponent_y, chkpt_x, chkpt_y, player_orientation):
        self.player.update(
            x=player_x,
            y=player_y,
            orientation=player_orientation,
            dist_to_chkpt=Tools.calc_dist(x1=player_x, y1=player_y, x2=chkpt_x, y2=chkpt_y))

        self.opponent.update(
            x=opponent_x,
            y=opponent_y,            
            dist_to_chkpt=Tools.calc_dist(x1=opponent_x, y1=opponent_y, x2=chkpt_x, y2=chkpt_y))


    def probe_max_speed(self):
        if self.player.speed > self.max_speed:
            self.max_speed = self.player.speed

    def probe_max_acceleration(self):
        if abs(self.player.acceleration) > self.max_acceleration:
            self.max_acceleration = abs(self.player.acceleration)

probe = Probe()

# game loop
while True:
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    # next_checkpoint_dist: distance to the next checkpoint
    # next_checkpoint_angle: angle between your pod orientation and the direction of the next checkpoint
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    probe.update_game_info(
        player_x=x, player_y=x,
        opponent_x=opponent_x, opponent_y=opponent_y,
        chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y,
        player_orientation=next_checkpoint_angle)

    engine_power = 50
    debug(f"engine_power {engine_power} speed {probe.player.speed:.2f} acc {probe.player.acceleration:.2f}")

    # You have to output the target position
    # followed by the engine_power (0 <= engine_power <= 100)
    # i.e.: "x y engine_power"
    print(f"{str(next_checkpoint_x)} {str(next_checkpoint_y)} {engine_power}")
