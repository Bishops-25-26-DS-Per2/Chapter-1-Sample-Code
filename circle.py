PI = 3.14159265358979323846264338327950

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    
    def __str__(self) -> str:
        return f"Circle object with radius {self.radius}"

    def circumference(self) -> float:
        """Calculate the circumference based on the radius attribute."""
        return 2 * self.radius * PI

def main():
    circle = Circle(3)
    print(circle)
    help(circle)

if __name__ == "__main__":
    main()