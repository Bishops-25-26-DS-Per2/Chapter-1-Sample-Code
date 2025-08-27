from random import randrange
import math
from cmu_graphics import *

def setup():
    """Steps to take before the animation starts."""
    # Create the Rect object in the setup()
    app.r = Rect(0, 0, 20, 20)
    # Choose initial speed randomly
    app.x_speed = randrange(1, 10)
    app.y_speed = randrange(1, 10)

def onStep():
    """Steps to take every frame."""
    # Move the rectangle
    app.r.left += app.x_speed
    app.r.top += app.y_speed
    # Deal with edges in the x direction
    if app.r.left > 380 or app.r.left < 0:
        app.x_speed *= -1
        app.x_speed = int(math.copysign(randrange(1, 10), app.x_speed))
        if app.r.left > 380: app.r.left = 380
        else: app.r.left = 0
        print(app.x_speed, app.y_speed, app.r.left, app.r.top)
    # Deal with edges in the y direction
    if app.r.top > 380 or app.r.top < 0:
        app.y_speed *= -1
        app.y_speed = int(math.copysign(randrange(1,10), app.y_speed))
        if app.r.top > 380: app.r.top = 380
        else: app.r.top = 0
        print(app.x_speed, app.y_speed, app.r.left, app.r.top)

setup()

cmu_graphics.run()