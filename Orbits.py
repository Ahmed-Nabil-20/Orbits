from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin, cos, radians, sqrt
import sys
import random
import time

# Window size
width, height = 1000, 800

# Orbit constants for controlling planet distance logic
MIN_ORBIT_RADIUS = 95
MAX_ORBIT_RADIUS = 350
RED_THRESHOLD = 120
BLUE_THRESHOLD = 280

# Time tracking for frame-independent animation
last_time = time.time()

# Star positions for background
NUM_STARS = 100
stars = [(random.randint(0, width), random.randint(0, height)) for _ in range(NUM_STARS)]

# Animation pause control
is_paused = False

# Main simulation class for the Earth-Moon system
class PlanetSystem:
    def __init__(self):
        self.angle = 0.0  # Earth's orbit angle around the Sun
        self.moon_angle = 0.0  # Moon's orbit angle around Earth
        self.orbit_radius = 200  # Distance from Sun
        self.planet_speed = 0.5  # Base orbital speed factor
        self.moon_speed = 2.0  # Speed of Moon's orbit (degrees/frame)
        self.moon_orbit_radius = 40  # Moon's orbit radius around Earth

    def update(self, delta_time):
        # Simulate real orbital speed based on distance (Kepler's 3rd Law approximation)
        orbital_speed = sqrt(1 / self.orbit_radius) * 150  # arbitrary scaling

        self.angle = (self.angle + orbital_speed * delta_time) % 360
        self.moon_angle = (self.moon_angle + self.moon_speed * delta_time * 60) % 360
        self.planet_speed = orbital_speed

    def draw(self):
        draw_sun(width // 2, height // 2, 40)
        draw_circle(width // 2, height // 2, RED_THRESHOLD, (1.0, 0.0, 0.0), filled=False)
        draw_circle(width // 2, height // 2, BLUE_THRESHOLD, (0.0, 0.0, 1.0), filled=False)

        earth_x = width // 2 + self.orbit_radius * cos(radians(self.angle))
        earth_y = height // 2 + self.orbit_radius * sin(radians(self.angle))

        if self.orbit_radius == 115:
            ocean_color = (0.0, 0.4, 1.0)
        elif self.orbit_radius < RED_THRESHOLD:
            t = min((RED_THRESHOLD - self.orbit_radius) / (RED_THRESHOLD - MIN_ORBIT_RADIUS), 1.0)
            ocean_color = interpolate_color((1.0, 0.2, 0.2), (0.4, 0.0, 0.0), t)
        elif self.orbit_radius > BLUE_THRESHOLD:
            t = min((self.orbit_radius - BLUE_THRESHOLD) / (MAX_ORBIT_RADIUS - BLUE_THRESHOLD), 1.0)
            ocean_color = interpolate_color((0.0, 0.4, 1.0), (1.0, 1.0, 1.0), t)
        else:
            ocean_color = (0.0, 0.4, 1.0)

        draw_circle(earth_x, earth_y, 20, ocean_color, filled=True)

        moon_x = earth_x + self.moon_orbit_radius * cos(radians(self.moon_angle))
        moon_y = earth_y + self.moon_orbit_radius * sin(radians(self.moon_angle))

        if self.orbit_radius < RED_THRESHOLD:
            t = min((RED_THRESHOLD - self.orbit_radius) / (RED_THRESHOLD - MIN_ORBIT_RADIUS), 1.0)
            moon_color = interpolate_color((0.5, 0.5, 0.5), (1.0, 0.0, 0.0), t)
        elif self.orbit_radius > BLUE_THRESHOLD:
            t = min((self.orbit_radius - BLUE_THRESHOLD) / (MAX_ORBIT_RADIUS - BLUE_THRESHOLD), 1.0)
            moon_color = interpolate_color((0.5, 0.5, 0.5), (0.9, 0.9, 0.9), t)
        else:
            moon_color = (0.5, 0.5, 0.5)

        draw_circle(moon_x, moon_y, 8, moon_color)

        if RED_THRESHOLD < self.orbit_radius < BLUE_THRESHOLD:
            land_offsets = [(-5, 5), (6, 4), (-3, -6)]
            for dx, dy in land_offsets:
                draw_circle(earth_x + dx, earth_y + dy, 5, (0.0, 0.8, 0.0), filled=True)

        draw_text(10, height - 20, f"Distance from Sun: {self.orbit_radius * 1000:.0f} km")
        draw_text(10, height - 40, f"Orbit Radius: {self.orbit_radius:.0f}")
        draw_text(10, height - 60, f"Earth Angle: {self.angle:.1f}")
        draw_text(10, height - 80, f"Moon Angle: {self.moon_angle:.1f}")
        draw_text(10, height - 100, f"Orbital Speed: {self.planet_speed:.2f} units/s")
        draw_text(10, height - 120, f"Planet State: {'Burning' if self.orbit_radius < RED_THRESHOLD else 'Frozen' if self.orbit_radius > BLUE_THRESHOLD else 'Normal'}")
        draw_text(10, height - 140, "Sun’s Gravitational Influence on the Earth:")
        draw_text(10, height - 160, f"{9.8 * (200 / self.orbit_radius):.2f} m/s²")
        draw_text(10, height - 180, "[A]/[D] to move Earth | [P]ause")


def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_stars():
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y in stars:
        glVertex2f(x, y)
    glEnd()

def draw_circle(x, y, radius, color, filled=True):
    glColor3f(*color)
    mode = GL_TRIANGLE_FAN if filled else GL_LINE_LOOP
    glBegin(mode)
    if filled:
        glVertex2f(x, y)
    for deg in range(0, 361, 5):
        rad = radians(deg)
        glVertex2f(x + cos(rad) * radius, y + sin(rad) * radius)
    glEnd()

def interpolate_color(c1, c2, t):
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))

def draw_sun(x, y, radius):
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(1.0, 1.0, 0.0)
    glVertex2f(x, y)
    for deg in range(0, 361, 5):
        rad = radians(deg)
        glColor3f(1.0, 0.5, 0.0)
        glVertex2f(x + cos(rad) * radius, y + sin(rad) * radius)
    glEnd()

    glColor4f(1.0, 0.8, 0.0, 0.3)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for deg in range(0, 361, 5):
        rad = radians(deg)
        glVertex2f(x + cos(rad) * (radius + 15), y + sin(rad) * (radius + 15))
    glEnd()

system = PlanetSystem()

def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_stars()
    system.draw()
    glutSwapBuffers()

def update(value):
    global last_time
    if not is_paused:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        system.update(delta_time)
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    global is_paused
    if key == b'a':
        system.orbit_radius = max(MIN_ORBIT_RADIUS, system.orbit_radius - 10)
    elif key == b'd':
        system.orbit_radius = min(MAX_ORBIT_RADIUS, system.orbit_radius + 10)
    elif key == b'p':
        is_paused = not is_paused

def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    screen_width = glutGet(GLUT_SCREEN_WIDTH)
    screen_height = glutGet(GLUT_SCREEN_HEIGHT)
    glutInitWindowPosition((screen_width - width) // 2, (screen_height - height) // 2)
    glutCreateWindow(b"Orbits")

    glClearColor(0.0, 0.0, 0.05, 1.0)

    glutDisplayFunc(draw_scene)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
