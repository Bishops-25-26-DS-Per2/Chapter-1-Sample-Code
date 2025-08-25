PI = 3.14159265358979323846264338327950

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    
    def circumference(self) -> float:
        """Calculate the circumference based on the radius attribute."""
        return 2 * self.radius * PI