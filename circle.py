PI = 3.14159265358979323846264338327950

class Circle:
    def __init__(self, radius):
        self.radius = radius
    
    def circumference(self):
        return 2 * self.radius * PI