import pygame as pg
from pygame import gfxdraw
from math import degrees

controlsText = [
    "G - Toggle gravity and friction(damping) ",
    "Scroll - Particle radius ",
    "V/B - Particle velocity multiplier ",
    "K/L - Particle angle ",
    "Click - Add particle ",
    "N - New generation ",
    "A/S - Amount of particles for next generation ",
    "E/R - Lower radius range next generation ",
    "D/F - Upper radius range next generation "
]
new_particle_radius = 30
new_particle_angle = 0
new_particle_vel_mult = 0


def draw(surface, font):
    x, y = pg.mouse.get_pos()
    gfxdraw.aacircle(surface, x, y, int(new_particle_radius), [63, 64, 65]) # Cursor

    for i, controlText in enumerate(controlsText):
        pos = (10, 10 + (i * 30))
        surface.blit(font.render(controlText + extra_info(i), True, [63, 64, 65], [180, 190, 200]), pos)


def extra_info(i):
    # Provide the text in parenthesis
    info = ''
    if i == 1:
        info += ('(' + str(int(new_particle_radius)) + ') ')
    if i == 2:
        info += ('(' + str(int(new_particle_vel_mult * 10) / 10) + ') ')
    if i == 3:
        info += ('(' + str(int(degrees(new_particle_angle))) + '°) ')

    if i == 6:
        from parameters import NEW_GENERATION_NUM_PARTICLES
        info += ('(' + str(int(NEW_GENERATION_NUM_PARTICLES)) + ') ')
    if i == 7:
        from parameters import NEW_GENERATION_RADIUS_RANGE
        info += ('(' + str(int(NEW_GENERATION_RADIUS_RANGE[0])) + ') ')
    if i == 8:
        from parameters import NEW_GENERATION_RADIUS_RANGE
        info += ('(' + str(int(NEW_GENERATION_RADIUS_RANGE[1])) + ') ')
    return info


def process_event(event):
    import parameters
    global new_particle_radius
    if event.type == pg.KEYDOWN:
        keys = pg.key.get_pressed()
        if keys[pg.K_g]:
            parameters.GRAVITY = 0.025 if parameters.GRAVITY == 0 else 0
            parameters.DO_DAMPING = parameters.GRAVITY != 0
        elif keys[pg.K_n]:
            from main import new_generation
            new_generation()

    elif event.type == pg.MOUSEBUTTONDOWN:
        if event.button == 1:  # LMB
            x, y, = pg.mouse.get_pos()
            from main import add_particle
            add_particle(angle=new_particle_angle, vel_mult=new_particle_vel_mult, x=x, y=y, r=int(new_particle_radius))
        elif event.button == 4:  # Scroll up
            new_particle_radius *= 1.07
        elif event.button == 5:  # Scroll down
            new_particle_radius *= 0.9


def update():
    # Used to process held down buttons
    global new_particle_angle, new_particle_vel_mult
    import parameters as params
    keys = pg.key.get_pressed()
    if keys[pg.K_a]:
        params.NEW_GENERATION_NUM_PARTICLES -= 0.06
    if keys[pg.K_s]:
        params.NEW_GENERATION_NUM_PARTICLES += 0.06
    if keys[pg.K_e]:
        params.NEW_GENERATION_RADIUS_RANGE[0] -= 0.03
    if keys[pg.K_r]:
        params.NEW_GENERATION_RADIUS_RANGE[0] += 0.03
    if keys[pg.K_d]:
        params.NEW_GENERATION_RADIUS_RANGE[1] -= 0.03
    if keys[pg.K_f]:
        params.NEW_GENERATION_RADIUS_RANGE[1] += 0.03

    if keys[pg.K_k]:
        new_particle_angle -= 0.01
    if keys[pg.K_l]:
        new_particle_angle += 0.01
    if keys[pg.K_v]:
        new_particle_vel_mult -= 0.02
    if keys[pg.K_b]:
        new_particle_vel_mult += 0.02


import main
