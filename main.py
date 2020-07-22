import controls
import os
import numpy as np
import pygame as pg

from itertools import combinations
from math import atan2, cos, inf, pi, sin, sqrt
from pygame import gfxdraw
from random import choice, randint, random

os.environ['SDL_VIDEO_WINDOW_POS'] = '960,30'  # Set initial position of window
pg.init()

# Colors from https://flatuicolors.com/palette/us
ALL_COLORS = [[85, 239, 196],  [129, 236, 236], [116, 185, 255], [162, 155, 254], [223, 230, 233],
              [0, 184, 148],   [0, 206, 201],   [9, 132, 227],   [108, 92, 231],  [178, 190, 195],
              [255, 234, 167], [250, 177, 160], [255, 118, 117], [253, 121, 168], [99, 110, 114],
              [253, 203, 110], [225, 112, 85],  [214, 48, 49],   [232, 67, 147],  [45, 52, 5]]
WIDTH, HEIGHT = 960, 1010

font = pg.font.Font('Roboto-Medium.ttf', 25)
w = pg.display.set_mode((WIDTH, HEIGHT))


def clamp(val, low=None, high=None):
    # Return value no lower than low and no higher than high
    minimum = -inf if low is None else low
    maximum = inf if high is None else high
    return max(min(val, maximum), minimum)


def dist(x1, y1, x2, y2, less_than=None, greater_than=None):
    # Use less_than or greater_than avoid using costly square root function
    if less_than is not None:
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) < less_than ** 2
    if greater_than is not None:
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) > greater_than ** 2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def draw_circle(surface, x, y, radius, color):
    # Draw anti-aliased circle
    gfxdraw.aacircle(surface, int(x), int(y), radius, color)
    gfxdraw.filled_circle(surface, int(x), int(y), radius, color)


def overlapping_particle(x, y, r):
    # Returns an overlapping particle from particles or None if not touching any
    for particle in particles:
        if dist(x, y, particle.x, particle.y, less_than=r + particle.r):
            return particle


def particle_bounce_velocities(p1, p2):
    # Change particle velocities to make them bounce
    # Based off github.com/xnx/collision/blob/master/collision.py lines 148-156
    from parameters import COLLISION_DAMPING, DO_DAMPING
    m1, m2 = p1.r ** 2, p2.r ** 2
    big_m = m1 + m2
    r1, r2 = np.array((p1.x, p1.y)), np.array((p2.x, p2.y))
    d = np.linalg.norm(r1 - r2) ** 2
    v1, v2 = np.array((p1.vx, p1.vy)), np.array((p2.vx, p2.vy))
    u1 = v1 - 2 * m2 / big_m * np.dot(v1 - v2, r1 - r2) / d * (r1 - r2)
    u2 = v2 - 2 * m1 / big_m * np.dot(v2 - v1, r2 - r1) / d * (r2 - r1)
    p1.vx, p1.vy = u1 * (COLLISION_DAMPING if DO_DAMPING else 1)
    p2.vx, p2.vy = u2 * (COLLISION_DAMPING if DO_DAMPING else 1)


def particle_bounce_positions(p1, p2):
    # Push particles away so they don't overlap
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    angle = atan2(dy, dx)
    center_x = p1.x + 0.5*dx
    center_y = p1.y + 0.5*dy
    radius = (p1.r + p2.r) / 2
    p1.x = center_x - (cos(angle) * radius)
    p1.y = center_y - (sin(angle) * radius)
    p2.x = center_x + (cos(angle) * radius)
    p2.y = center_y + (sin(angle) * radius)


class Particle:
    def __init__(self, r, angle=None, vel_mult=1, x=None, y=None):
        a = 2 * pi * random() if angle is None else angle  # Angles are clockwise from 3 o'clock
        self.vx, self.vy = (cos(a)*vel_mult, sin(a)*vel_mult)
        self.color = choice(ALL_COLORS)
        self.r = r  # Radius
        self.x, self.y = x, y
        if self.x is None or self.y is None:
            self.calculate_pos()

    def calculate_pos(self):
        # Find a position where we won't overlap with any other particles
        while True:
            self.x, self.y = randint(self.r, WIDTH - self.r), randint(self.r, HEIGHT - self.r)
            if overlapping_particle(self.x, self.y, self.r) is None:  # If valid spot
                break

    def damping(self, amount):
        # Slow down the particle gradually
        self.vx *= amount
        self.vy *= amount

    def gravity(self, amount):
        self.vy += amount

    def wall_collisions(self, damping_amount):
        # Velocity
        collided = False
        if not self.r < self.x < WIDTH - self.r:
            self.vx *= damping_amount
            collided = True
        if not self.r < self.y < HEIGHT - self.r:
            self.vy *= damping_amount
            collided = True

        # Position
        if collided:
            # Get out of wall
            self.x = clamp(self.x, low=self.r, high=WIDTH - self.r)
            self.y = clamp(self.y, low=self.r, high=HEIGHT - self.r)

    def move(self, speed):
        self.x += self.vx * speed
        self.y += self.vy * speed

    def draw(self):
        draw_circle(w, self.x, self.y, self.r, self.color)

    def apply_force_towards(self, x, y, strength=1):
        # May be used in later implementations with attractions
        dx = x - self.x
        dy = y - self.y
        self.vx += dx * 0.00001 * strength
        self.vy += dy * 0.00001 * strength


def add_particle(angle=None, vel_mult=1, x=None, y=None, r=None):
    global particles
    particles.append(Particle(angle=angle, vel_mult=vel_mult, x=x, y=y, r=r))


def new_generation():
    from parameters import NEW_GENERATION_NUM_PARTICLES, NEW_GENERATION_RADIUS_RANGE
    global particles
    particles = []
    for _ in range(int(NEW_GENERATION_NUM_PARTICLES)):
        particles.append(Particle(r=randint(int(NEW_GENERATION_RADIUS_RANGE[0]), int(NEW_GENERATION_RADIUS_RANGE[1]))))


def events():
    for event in pg.event.get():
        controls.process_event(event)
        if event.type == pg.QUIT:
            pg.quit()
            quit()


def update():
    from parameters import DAMPING, DO_DAMPING, GRAVITY, SPEED_MULTIPLIER, WALL_DAMPING
    for particle in particles:
        particle.damping(DAMPING if DO_DAMPING else 1)
        particle.gravity(GRAVITY)
        particle.wall_collisions(-WALL_DAMPING if DO_DAMPING else -1)
        particle.move(SPEED_MULTIPLIER)

    # Test inter-particle collisions
    pairs = combinations(range(len(particles)), 2)  # All combinations of particles
    for i, j in pairs:
        p1, p2 = particles[i], particles[j]
        if dist(p1.x, p1.y, p2.x, p2.y, less_than=p1.r + p2.r):  # If they are touching
            particle_bounce_velocities(p1, p2)
            particle_bounce_positions(p1, p2)

    controls.update()


def draw():
    w.fill([255, 255, 255])

    for particle in particles:
        particle.draw()

    controls.draw(w, font)

    pg.display.update()


particles = []
new_generation()
while True:
    events()
    update()
    draw()
