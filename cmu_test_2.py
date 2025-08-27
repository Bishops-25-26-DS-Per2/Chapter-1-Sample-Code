from random import randrange
import math
import cmu_graphics

class MyRect:
    """Rectangles that move across the graphics window and bounce at edges."""
    def __init__(self):
        # Start at (0, 0).  Width & height both 20 pixels.
        self.rect = cmu_graphics.Rect(0, 0, 20, 20)
        self.x_speed = randrange(1, 10)
        self.y_speed = randrange(1, 10)
    
    def move_step(self) -> None:
        """Take one step, intended to be for one frame."""
        self.rect.left += self.x_speed
        self.rect.top += self.y_speed

    def check_edges(self) -> None:
        """Bounce when the rectangle hits the edge of the screen."""
        # Bounce when the rectangle hit the left or right wall
        if self.rect.left > 380 or self.rect.left < 0:
            self.x_speed *= -1
            self.x_speed = int(math.copysign(randrange(1, 10), self.x_speed))
            if self.rect.left > 380: self.rect.left = 380
            else: self.rect.left = 0
            print(self.x_speed, self.y_speed, self.rect.left, self.rect.top)
        # Bounce when the rectangle hits the top and bottom wall
        if self.rect.top > 380 or self.rect.top < 0:
            self.y_speed *= -1
            self.y_speed = int(math.copysign(randrange(1,10), self.y_speed))
            if self.rect.top > 380: self.rect.top = 380
            else: self.rect.top = 0
            print(self.x_speed, self.y_speed, self.rect.left, self.rect.top)

def setup():
    cmu_graphics.app.rects = []
    cmu_graphics.app.frames = 0
    for i in range(4):
        cmu_graphics.app.rects.append(MyRect())
    cmu_graphics.app.label = cmu_graphics.Label("1", 100, 100)

def onStep():
    cmu_graphics.app.frames += 1
    for rect in cmu_graphics.app.rects:
        rect.move_step()
        rect.check_edges()
    if cmu_graphics.app.frames % 30 == 0:
        cmu_graphics.app.label.value+="1"

setup()

cmu_graphics.cmu_graphics.run()