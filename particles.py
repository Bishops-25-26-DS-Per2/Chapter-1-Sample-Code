from random import randrange
import math
import inspect

from cmu_graphics import *

app.particles = 15
app.edge_repel = 1000 + 50*app.particles
app.frames = 0

def setup():
    """Run this before the simulation starts to get things going."""
    app.width = 840
    app.height = 840
    app.background = "black"
    app.objs = []
    app.objs.append(Edge(x = 0))
    app.objs.append(Edge(x = app.width))
    app.objs.append(Edge(y = 0))
    app.objs.append(Edge(y = app.height))
    for i in range(app.particles):
        x = randrange(1, app.width)
        y = randrange(1, app.height)
        app.objs.append(Particle(x, y))
    
def onStep():
    """Calculate new position of each particle for each frame."""
    # The first four items are non-moving walls, so don't move them.
    for particle in app.objs[4:]:
        # But all objects other than itself repel each particle
        for obj in app.objs:
            if obj != particle:
                repel = obj.repel(particle)
                particle.x += repel[0]
                particle.y += repel[1]
        # If a particle ends up off-screen, put it back on
        if particle.x < 0:
            particle.x = 2
        elif particle.x > app.width:
            particle.x = app.width - 2
        if particle.y < 0:
            particle.y = 2
        elif particle.y > app.height:
            particle.y = app.height - 2
        # Sometimes a particle gets stuck at the edge
        if (int(particle.x) == 2 or 
                int(particle.x) == app.width - 2 or
                int(particle.y) == 2 or
                int(particle.y) == app.height - 2
        ):
            particle.stuck += 1
        else:
            particle.stuck = 0
        if particle.stuck > 4:
            particle.stuck = 0
            if particle.x == 2:
                particle.x = 50
            elif particle.x == app.width - 2:
                particle.x = app.width - 50
            if particle.y == 2:
                particle.y = 50
            elif particle.y == app.height - 2:
                particle.y = app.height - 50
        particle.circle.centerX = particle.x
        particle.circle.centerY = particle.y
    app.frames += 1
    if app.frames % 30 == 0:
        for particle in app.objs[4:]:
            print(f"{particle.x:3.0f}, {particle.y:3.0f}", end="  ")
        print()

def onMousePress(mouseX: int, mouseY: int) -> None:
    """Add a new particle when we get a click."""
    app.objs.append(Particle(mouseX, mouseY))
    app.particles += 1
    print(app.particles, end="  ")

class Particle(object):
    """A particle is a freely moving object that repels all other particles"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.repel_const = (20 + app.particles) / app.particles
        self.stuck = 0
        self.circle = Circle(self.x, self.y, 25)
        self.circle.fill = "white"

    def repel(self, other: "Edge | Particle") -> (float, float):
        # Apply the repelling force of a particle, closer => stronger
        distance = dist(self, other)
        if distance > 0:
            x_repel = self.repel_const * (other.x - self.x) / distance
            y_repel = self.repel_const * (other.y - self.y) / distance
        else:
            # Really unlikely that distance == 0, but avoid a crash if so
            x_repel = randrange(1,10)
            y_repel = randrange(1,10)
        return x_repel, y_repel

class Edge(object):
    """ An Edge is literally the edge of the screen. """
    def __init__(self, x: int = None, y: int = None):
    # We expect to get x or y, but not both so we made x,y optional arguments
        # Crash the program if we got neither x,y or both
        if x is None and y is None:
            err_str = "Can't create Edge instance with no coordinate given. "
            err_str += "Provide either an x or a y coordinate."
            raise ValueError(err_str)
        if x is not None and y is not None:
            err_str = "Can't create Edge instance with both coordinate given. "
            err_str += "Provide either an x or a y coordinate."
            raise ValueError(err_str)
        # Whichever was not passed in will be None, that was the default value
        self.x = x
        self.y = y
        self.repel_const = app.edge_repel   

    def repel(self, other: Particle) -> (float, float):
        # Apply the repelling force on a particle, perpendicular to the edge
        # Force is proportional to reciprocal of distance, so closer => stronger
        if self.x is not None:
            return self.repel_const * other.repel_const / (other.x - self.x), 0
        elif self.y is not None:
            return 0, self.repel_const * other.repel_const / (other.y - self.y)

def dist(obj1: Particle, obj2: Particle) -> float:
    """Usual Pythagorean distance, assuming obj1 and obj2 have attrs .x & .y"""
    return math.sqrt((obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2)


setup()
cmu_graphics.run()