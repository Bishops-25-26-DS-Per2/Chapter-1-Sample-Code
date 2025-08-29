from cmu_graphics import *

def setup():
    # Make a list of Circles that are left behind each time you click.
    app.clicked_dots = []
    app.cursor = Star(0, 0, 20, 5, fill='red')
    app.my_colors = ['white', 'red', 'blue', 'green', 'black', 'gray',  
            'yellow', 'cyan', 'magenta', 'orange', ]
    app.my_color_index = 0

def onMousePress(mouseX: int, mouseY: int) -> None:
    """This function automatically detects mouse presses.

    It will run once each time the mouse is pressed."""
    # Create a new Circle each time the user clicks.
    app.clicked_dots.append(Circle(mouseX, mouseY, 10, fill='green'))

def onMouseMove(mouseX: int, mouseY: int) -> None:
    """This function automatically updates any time the mouse moves.

    It will run continuously as the mouse moves."""
    app.cursor.centerX = mouseX
    app.cursor.centerY = mouseY

def onKeyPress(key: str) -> None:
    """This function automatically detects if a key on the keyboard was pressed.

    The variable key tells you which was pressed."""
    if key:
        if app.my_color_index < len(app.my_colors) - 1:
            app.my_color_index += 1
        else:
            app.my_color_index = 0
        app.background = app.my_colors[app.my_color_index]



setup()
cmu_graphics.run()