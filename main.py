import sys
import math
import random
import copy
import timeit

GameTurn = 0
StartTime = 0

class Config:
    Unit_Length = 1000

class GameEnv:
    Max_Yaw_Angle = 18
    Max_Engine_Power = 100
    Map_Width = 16000
    Map_Height = 9000
    Max_Computing_Time = 0.065 # seconds
    Chkpt_Radius = 600
    List_Chkpts = []

    @staticmethod
    def add_chkpt(x, y):
        for item in GameEnv.List_Chkpts:
            if item[0] == x or item[1] == y:
                return
        GameEnv.List_Chkpts.append([x, y])

    @staticmethod
    def find_chkpt(x, y):
        chkpts = GameEnv.List_Chkpts
        for i in range(0, len(chkpts)):
            if chkpts[i][0] == x and chkpts[i][1] == y:
                return i
        return IndexError

    @staticmethod
    def next_chkpt(index):
        n = len(GameEnv.List_Chkpts)
        return (index + 1) % n

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
            return int(out_x), int(out_y)
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
        return f"{int(self.x)} {int(self.y)}"

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
                self.x = int(self.x * scaler)
                self.y = int(self.y * scaler)
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

        self.next_chkpt = Vector()

        # chkpt is the vector from pod to check point
        # chkpt.angle is the absolute angle (ref to horizon)
        # negative angle means the vector points toward upper screen
        # positive angle means the vector points toward lower screen
        self.chkpt_dir: Vector = Vector()        

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
            self.next_chkpt.update(x=x, y=y)
            self.chkpt_dir.update(pos1=self.position, pos2=Vector(x, y))        

    def update_orientation(self, chkpt_angle=None):
        self.orient_prev.copy(self.orient)
        if chkpt_angle != None:                 
            self.orient.update(angle=self.chkpt_dir.angle + chkpt_angle, length=Config.Unit_Length)
        else:
            self.orient.copy(self.acc_prev)
            self.orient.update(length=Config.Unit_Length)

    def update_engine_power(self):
        if self.engine_power == None:
            self.engine_power_prev = GameEnv.calc_engine_power(acceleration=self.acc_prev.length, speed=self.vel_prev.length)
        else:
            self.engine_power_prev = self.engine_power

    def update(self, x, y, chkpt_x=None, chkpt_y=None, chkpt_angle=None):        
        self.update_position(x=x, y=y)
        self.update_checkpoint(x=chkpt_x, y=chkpt_y)
        self.update_velocity()
        self.update_acceleration()
        self.update_orientation(chkpt_angle=chkpt_angle)
        self.update_engine_power()

class Simulation:
    @staticmethod
    def next_pos(pod: Pod, yaw_angle: float, engine_power: int):
        # angle = (0: forward, < 0: turn left, > 0: turn right)
        if yaw_angle > GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle
        elif yaw_angle < -GameEnv.Max_Yaw_Angle:
            yaw_angle = GameEnv.Max_Yaw_Angle

        acc_angle = pod.orient.angle + yaw_angle        
        acc_length = GameEnv.calc_acceleration(speed=pod.velocity.length, engine_power=engine_power)
        thrust_dir = Vector(angle=acc_angle, length=acc_length)        
        prediction = (pod.velocity + thrust_dir) + pod.position
        return [prediction.x, prediction.y]

    @staticmethod
    def predict_pos(pod: Pod, actions: list):
        dummy = copy.deepcopy(pod)
        prediction = []
        for action in actions:
            yaw_angle = action[0]
            engine_power = action[1]
            new_pos = Simulation.next_pos(pod=dummy, yaw_angle=yaw_angle, engine_power=engine_power)
            dummy.update(x=new_pos[0], y=new_pos[1])
            prediction.append(new_pos)
        return prediction

class GA_Controller:
    N_Genes = 5
    Population = 10
    Death_Rate = 0.5
    Mutation_Rate = 0.01
    Reward_Chkpt_Reached = 20000
    Death_Score = -1000000
    
    def __init__(self):        
        random.seed()  
        self.alpha = None
        self.alpha_score = None     

    def init_genome(self):
        return [[random.random(), random.random()] for i in range(0, self.N_Genes)]

    def init_population(self):
        return [self.init_genome() for i in range(0, self.Population)]

    def calc_score(self, list_pos, chkpt_index):
        score = 0
        (chkpt_x, chkpt_y) = GameEnv.List_Chkpts[chkpt_index]
        for pos in list_pos:            
            if pos[0] < 0 or pos[0] > GameEnv.Map_Width or pos[1] < 0 or pos[1] > GameEnv.Map_Height:
                return self.Death_Score
            if Tools.calc_dist(x1=pos[0], y1=pos[1], x2=chkpt_x, y2=chkpt_y) < GameEnv.Chkpt_Radius:
                score = score + self.Reward_Chkpt_Reached
                (last_pos_x, last_pos_y) = list_pos[-1]
                next_chkpt = GameEnv.next_chkpt(chkpt_index)
                (next_chkpt_x, next_chkpt_y) = GameEnv.List_Chkpts[next_chkpt]
                score = score - Tools.calc_dist(x1=last_pos_x, y1=last_pos_y, x2=next_chkpt_x, y2=next_chkpt_y)
                return score
        last_pos_x, last_pos_y = list_pos[-1][0], list_pos[-1][1]        
        score = score - Tools.calc_dist(x1=last_pos_x, y1=last_pos_y, x2=chkpt_x, y2=chkpt_y)
        return score

    def calc_fitness(self, population, pod):
        fitness = []
        index = 0
        for genome in population:
            list_pos = Simulation.predict_pos(pod=pod, actions=self.conv_genome_to_actions(genome=genome))            
            score = self.calc_score(list_pos=list_pos, chkpt_index=GameEnv.find_chkpt(x=pod.next_chkpt.x, y=pod.next_chkpt.y))            
            fitness.append([index, score])
            index += 1
        return fitness

    def survivor_selection(self, population, fitness):
        def get_score(item):
            return item[1]
        
        fitness.sort(key=get_score, reverse=True)

        (index, score) = fitness[0]
        if score > self.alpha_score:
            self.alpha = population[index]
            self.alpha_score = score

        n_survivors = self.Population - int(self.Death_Rate * self.Population)
        new_pop = []
        for i in range(0, n_survivors):
            new_pop.append(population[fitness[i][0]])
        return new_pop

    def crossover(self, population):
        n_pop = len(population)
        n_offsprings = int(self.Death_Rate * self.Population)
        
        for i in range(0, n_offsprings):
            male = random.randint(0, n_pop-1)
            while True:
                female = random.randint(0, n_pop-1)
                if female != male:
                    break
            
            male = population[male]
            female = population[female]
            offspring = []
            for gene_index in range(0, self.N_Genes):
                gene0 = 0
                gene1 = 0
                if random.random() > 0.5:
                    gene0 = male[gene_index][0]
                else:
                    gene0 = female[gene_index][0]
                if random.random() > 0.5:
                    gene1 = male[gene_index][0]
                else:
                    gene1 = female[gene_index][0]
                if random.random() < self.Mutation_Rate:
                    gene0 = random.random()
                    gene1 = random.random()
                
                offspring.append([gene0, gene1])

            population.append(offspring)
        return population
    
    def main(self, pod: Pod):
        global StartTime
        population = self.init_population()
        self.alpha_score = self.Death_Score
        
        while timeit.default_timer() - StartTime <= GameEnv.Max_Computing_Time:
            fitness = self.calc_fitness(population=population, pod=pod)
            population = self.survivor_selection(population=population, fitness=fitness)            
            population = self.crossover(population=population)            
        return self.conv_genome_to_actions(genome=[self.alpha[0]])

    def conv_genome_to_actions(self, genome: list):
        actions = []
        for (yaw_angle, engine_power) in genome:
            if engine_power > GameEnv.Max_Engine_Power:
                engine_power = GameEnv.Max_Engine_Power
            elif engine_power < 0:
                engine_power = 0
            actions.append([yaw_angle, engine_power])
        return actions

def main():
    player = Pod()
    opponent = Pod()
    controller = GA_Controller()

    global GameTurn
    global StartTime   
    
    GameTurn = 0

    # game loop
    while True:
        
        GameTurn += 1
        # next_checkpoint_x: x position of the next check point
        # next_checkpoint_y: y position of the next check point
        # next_checkpoint_dist: distance to the next checkpoint
        # next_checkpoint_angle: angle between your pod angle_to_chkpt and the direction of the next checkpoint
        x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
        opponent_x, opponent_y = [int(i) for i in input().split()]
        StartTime = timeit.default_timer()

        GameEnv.add_chkpt(x=next_checkpoint_x, y=next_checkpoint_y)        

        # the game angle is opposite of our convention
        next_checkpoint_angle = -next_checkpoint_angle

        player.update(x=x, y=y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y, chkpt_angle=next_checkpoint_angle)
        opponent.update(x=opponent_x, y=opponent_y, chkpt_x=next_checkpoint_x, chkpt_y=next_checkpoint_y)
        
        [[yaw_angle, engine_power]] = controller.main(pod=player)
        player.pilot(yaw_angle=yaw_angle, engine_power=engine_power)

        # You have to output the target position
        # followed by the engine_power (0 <= engine_power <= 100)
        # i.e.: "x y engine_power"
        print(f"{player.next_direction} {player.engine_power}")

main()