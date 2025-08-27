from random import randrange

from cmu_graphics import *

def setup():
    """Create objects and constants, set up the window for the simulation."""
    # Following distance of one car to another.  1 car length = 80 pixels
    app.NEAR_TEST = 240
    # Number of lanes in my road
    app.lanes = 3
    # Size of the window showing the road.  Height depends on # of lanes
    app.width = 1200
    app.height = 100*app.lanes + 100
    # Set background to dark gray
    app.background = 'dimGray'
    # Counting frames drawn so we can generate new traffic on a schedule
    app.frames = 0
    # List of all cars on the road, excluding me
    app.cars = []
    # List of removed cars.  This is to avoid creating new Rect() objects 
    #   when creating new Car() objects so as to avoid the maxShape limit
    #   in cmu_graphics.
    app.removed_cars = []
    # Any global variables to be modified have to be declared here
    app.me = MyCar(0)
    for i in range(randrange(2, 5*app.lanes)):
        car = generate_new_car()
        if car is not None:
            app.cars.append(car)
        else:
            pass
            # print("Could not fit a car, too many collisions.")
    # print(app.cars)
    app.road = Road()
    app.road.create_road()


def onStep():
    """This function runs once per frame. 
    
    Update positions of all objects, create new objects as needed, destroy 
    objects no longer in use.
    """
    app.frames += 1
    app.road.shift_lane_lines()
    # Draw my car, adjust as needed
    app.me.move_car()
    app.me.check_near()
    app.me.check_speeds()
    # Draw and adjust other cars
    for i, car in enumerate(app.cars):
        car.move_car()
        near = car.check_near()
        # prevent things getting static by randomly nudging speed by a bit
        if not near and car != app.me:
            adj = randrange(-5, 6)
            car.speed += 0.001 * adj
            car.previous_speed += 0.001 * adj
        car.rect.fill = car.color
        car.rect.toBack()
    # Check who's far enough off-screen that they're not coming on-screen
    purge_cars()
    # Every once in a while, add a new car
    if app.frames % 160 == 0:
        car = generate_new_car()
        if car is not None:
            app.cars.append(car)
        else:
            pass
            # print("Could not fit a car, too many collisions.\n")
        # If needed, print car stats
        my_str = str(len(app.cars))
        on_screen = 0
        for car in app.cars:
            if -80 < car.x < app.width:
                on_screen += 1
            for other_car in app.cars:
                if car != other_car:
                    if (abs(car.x - other_car.x) < 80
                            and car.lane == other_car.lane):
                        disaster_str = f"Disaster at {car.x}, {other_car.x}!\n"
                        disaster_str += f"Now: {app.frames} "
                        disaster_str += f"Car 1: {car.frame_created} "
                        disaster_str += f"Car 2: {other_car.frame_created}" 
                        print(disaster_str)
        my_str += "," + str(on_screen)
        for car in app.cars:
            my_str += "\t" + str(car.lane) + "," + str(int(car.x))
        # print(my_str)
        if app.frames % 800 == 0:
            print(app.frames)

        
class Road:
    """Object representing the road and its associated methods."""
    def __init__(self):
        self.line_color = 'white'
        self.left_edge_color = 'gold'
        
    def create_road(self) -> None:
        """Create all the lines associated with the road.
        
        All lines have a thickness of 10 pixels, lanes are 100 pixels wide,
        including one lane line.
        """
        self.create_edge_lines()
        self.create_lane_lines()
    
    def create_edge_lines(self) -> None:
        """Create the long lines on the left/right edges of the road."""
        self.right_edge = Rect(0, 50, app.width, 10)
        self.right_edge.fill = self.line_color
        self.left_edge = Rect(0, 50 + 100*app.lanes, app.width, 10)
        self.left_edge.fill = self.left_edge_color
    
    def create_lane_lines(self) -> None:
        """Create the dashed lane lines.
        
        These lines are 125 pixels long, each one starts 300 pixels from the
        previous one.  
        """
        self.lane_lines = []
        for i in range(app.lanes - 1):
            for j in range(app.width // 300):
                r = Rect(300*j, 100*i + 150, 125, 10)
                r.fill = self.line_color
                self.lane_lines.append(r)

    def shift_lane_lines(self) -> None:
        """Move the lane lines along, giving illusion of car movement."""
        # All line segments need to jump 300 pixels left if minimum left 
        #   position gets as large as 175 (= spacing - length).
        lefts = []
        for r in self.lane_lines:
            r.left += 15
            lefts.append(r.left)
        if min(lefts) >= 175:
            for r in self.lane_lines:
                r.left -= 300

    
class Car(object):
    """Superclass for cars in the simulation.
    
    Not intended to be called directly, use the classes that inherit from it."""
    def __init__(self, lane: int):
        """Intended to be called by all subclasses."""
        # Used when changing lanes
        self.changing_lanes = False
        # Which direction we're changing: left (-1) or right (+1)
        self.changing_lanes_dir = 0
        # Lane Number, between 0 & lane - 1
        self.lane = lane
        # If you have to slow down because someone is in front of you, keep
        # track of how fast you were going
        self.previous_speed = self.speed
        # Which frame number the car finished changing lanes.
        self.changed_lanes_frame = 0
        # self.x is set in the subclass
        self.y = 100 * self.lane + 80
        # Keep track on when the car was created, for error checking.
        self.frame_created = app.frames
        # Keep track of who this car is stuck behind. 
        self.stuck_behind = []
        if not app.removed_cars:
            self.rect = Rect(self.x, self.y, 80, 50)
        else:
            self.rect = app.removed_cars.pop().rect
            self.rect.left = self.x
            self.rect.top = self.y
        self.rect.fill = self.color

    def move_car(self) -> None:
        """Find new correct location, both forward/back (x), and lane (y)."""
        if self != app.me:
            self.x += rounded(self.speed * 10)
        else:
            self.check_speeds()
        if self.changing_lanes:
            self.lane += self.changing_lanes_dir * 0.05
            self.y = 100 * self.lane + 80
            if abs(self.lane - rounded(self.lane)) < 0.01:
                self.changing_lanes = False
                self.changing_lanes_dir = 0
                self.lane = int(rounded(self.lane))
                self.y = 100 * self.lane + 80
                self.changed_lanes_frame = app.frames
                # print("Done changing lanes")
        self.rect.left = self.x
        self.rect.top = self.y
        
    def change_lanes(self, dir: int) -> None:
        """To change lanes, just change attributes, move_car does the rest."""
        self.changing_lanes = True
        self.changing_lanes_dir = dir
    
    def check_near(self) -> bool:
        """See if another car is near enough to change this car's behavior."""
        near = False
        app.cars.append(app.me)
        for i, car in enumerate(app.cars):
            # Avoid checking self, you're always near yourself
            if self != car:
                if (self.lane == car.lane and 
                        self.x - car.x < app.NEAR_TEST and 
                        self.x - car.x > 0
                ):
                    near = True
                    near_car_index = i
                    if i not in self.stuck_behind:
                        self.stuck_behind.append(i)
                    for j in app.cars[i].stuck_behind:
                        if j not in self.stuck_behind:
                            self.stuck_behind.append(j)
                    
        app.cars.pop(-1)
        if not self.changing_lanes:
            # Any time a car is not in the right lane, and it can go right, it
            # should go right.
            blocked_right = False
            # Include me in cars that might need to get right
            app.cars.append(app.me)
            for car in app.cars:
                if car != self:
                    if (car.lane == self.lane - 1 and 
                            abs(car.x - self.x) < app.NEAR_TEST
                    ):
                        blocked_right = True
                    if (car.changing_lanes and 
                            abs(car.x - self.x) < app.NEAR_TEST
                    ):
                        blocked_right = True
            if not blocked_right and self.lane > 0 and not self.changing_lanes:
                if app.frames > self.changed_lanes_frame + 40:
                    self.change_lanes(-1)
            # But don't leave me in the list of cars
            app.cars.pop(-1)
        # If any car had to slow down, turn it red.
        if near:
            # self.color = 'red'
            # if self == app.me:
            #     print(f"{app.me.speed=}")
            self.adjust(near_car_index)
        # Turn back to the original color, blue or green
        elif self != app.me:
            self.color = 'blue'
            self.speed = self.previous_speed
            self.stuck_behind = []
        else:
            self.color = 'green'
            self.speed += 0.1
            self.stuck_behind = []
        self.rect.fill = self.color
        return near
    
    def adjust(self, near_car_index: int) -> None:
        """Determine if one car is overtaking another and respond. 
        
        Can move left, otherwise slow down.  Doesn't pass on the right."""
        app.cars.append(app.me)
        blocked_left = False
        for car in app.cars:
            if car != self:
                if (car.lane == self.lane + 1 and 
                        abs(car.x - self.x) < app.NEAR_TEST
                ):
                    blocked_left = True
                if (car.changing_lanes and 
                        abs(car.x - self.x) < app.NEAR_TEST
                ):
                    blocked_left = True                    
        if (not blocked_left and 
                self.lane < app.lanes - 1 and 
                not self.changing_lanes and 
                app.frames > self.changed_lanes_frame + 40
        ):
            self.change_lanes(1)
        if self != app.me:
            self.speed = app.cars[near_car_index].speed
            for i in self.stuck_behind:
                if i < len(app.cars) and self.speed < app.cars[i].speed:
                    self.speed = app.cars[i].speed
        else:
            for i in self.stuck_behind:
                if i < len(app.cars):
                    app.cars[i].speed = 0
        if self.x - app.cars[near_car_index].x < app.NEAR_TEST - 1:
            if self != app.me:
                self.x += 3
            else:
                app.cars[near_car_index].x -= 3
        app.cars.pop(-1)

class MyCar(Car):
    """This car is me, the central car in the simulation. 
    
    The speed of the simulation always matches my speed.
    Simulation expects only one instance of this class."""
    def __init__(self, lane: int):
        self.color = 'green'
        self.x = 450
        self.y = 0
        # Simulation speed is relative to MyCar.speed
        # Adding to my speed makes me go faster, this is opposite others.
        self.speed = 0
        # At the end, also run the __init__ method from the Car parent class
        super().__init__(lane)
        
    def check_speeds(self) -> None:
        """If my speed goes down, slow down the entire simulator. 
        
        Do this by speeding up all the other cars."""
        for car in app.cars:
            if car != self:
                car.speed -= self.speed
        self.speed = 0

class OtherCar(Car):
    """For all the other cars."""
    def __init__(self, lane: int, x: int, speed: int):
        self.color = 'blue'
        self.x = x
        self.y = 0
        # Notice that self.speed is relative to MyCar
        # Increase in speed value actually slows car because more right is
        #   farther behind.  This is opposite MyCar.
        self.speed = speed
        # Run the parent Car class __init__ method.
        super().__init__(lane)
        
def generate_new_car() -> OtherCar | None:
    """Algorithm for making additional cars.
    
    Notice that cmu_graphics is picky about creating new Rect objects, so 
        we recycle existing Rect objects using app.removed_cars list.  This
        happens in Car.__init__()
    We return None if a new car just won't fit.  In this case, it just fails
        and no new car is added.
    """
    speed = randrange(-6, 7) * 0.05
    # They can go anywhere if the simulation hasn't started running yet.
    if app.frames == 0:
        x = randrange(-2, int(app.width / 50) + 2) * 50
    else:
        # But if it has started running, try to generate them off-screen.  If
        #   they are faster, start them behind, if slower start them ahead.
        if speed == 0:
            adj = randrange(0,2)
            if adj == 0:
                speed = -0.05
            else:
                speed = 0.05
        if speed > 0:
            x = -100
        elif speed < 0:
            x = app.width + 100
    if speed < 0:
        # Make it more likely that slower cars are to the right
        lane_tmp = randrange(0, app.lanes * app.lanes)
        lane = app.lanes - 1
        diff = 1
        lane_tmp -= diff
        while lane_tmp >= 0:
            diff += 2
            lane_tmp -= diff
            lane -= 1
    elif speed > 0:
        # Make it more likely that faster cars are to the left
        lane_tmp = randrange(0, app.lanes * app.lanes)
        lane = 0
        diff = 1
        lane_tmp -= diff
        while lane_tmp >= 0:
            diff += 2
            lane_tmp -= diff
            lane += 1
    else:
        lane = randrange(0, app.lanes)
    # print(f"{x=}, {speed=}, {lane=}, {app.frames=}")
    # Collision is not an actual collision, but if the location where the car
    #   is about to generate is occupied, move it around until it can find an
    #   unoccupied location.
    collision = True
    collision_count = 0
    while collision:
        # Keep trying to find an open spot for this car to spawn.
        collision = False
        collision_count += 1
        app.cars.append(app.me)
        for car in app.cars:
            if lane == car.lane and abs(x - car.x) < app.NEAR_TEST:
                collision = True
                # print(lane, x, car.x)
        if collision:
            n = randrange(0,4)
            if n == 0 and lane < app.lanes - 1:
                lane += 1
            elif n == 1 and lane > 0:
                lane -= 1
            elif n == 2:
                if app.frames == 0 or x < -app.NEAR_TEST:
                    x += app.NEAR_TEST
            elif n == 3:
                if app.frames == 0 or x > app.width + app.NEAR_TEST:
                    x -= app.NEAR_TEST
        app.cars.pop(-1)
        if collision_count == 1000:
            break
    # print(f"{x=}, {speed=}, {lane=}, {app.frames=} {collision_count=}\n")
    if collision_count < 1000:
        return OtherCar(lane, x, speed)
    else:
        return None
        
def purge_cars() -> None:
    """If cars get far enough off-screen, drop them out of the list."""
    to_purge = []
    for i, car in enumerate(app.cars):
        if car.x > app.width + 1000 or car.x < -1000:
            to_purge.append(i)
    for i in to_purge:
        car = app.cars.pop(i)
        app.removed_cars.append(car)

setup()
cmu_graphics.run()