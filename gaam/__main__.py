# https://www.pygame.org/docs/
import pygame as pg
# http://www.pymunk.org/en/latest/pymunk.html
import pymunk as pm
import json

# i picked a low resolution so everything would be faster and sprites would be smaller
WITDH = 1280
HEIGHT = 960
# update simulation by 10 milliseconds at a time. pymunk is faster if the time step is always the same
SIM_STEP_SIZE = 10
BALL_OBJECT_TYPE = 1
WALL_OBJECT_TYPE = 2
GRAVITY_M_PER_S2 = 9.81/1000

space = pm.Space()
space.gravity = 0, GRAVITY_M_PER_S2
space.add_default_collision_handler()

pg.init()
screen = pg.display.set_mode((WITDH, HEIGHT), pg.SCALED)
clock = pg.time.Clock()
font = pg.font.SysFont("ptmonottc", 12)
n_dash = font.metrics("n")[0][4]

show_stats = True
sim_lag = 0.0
done = False


def draw_text(surface, font, start: tuple, text: str):
    for line in text.split("\n"):
        if len(line) > 0:
            line_img = font.render(line, True, pg.Color("white"))
            screen.blit(line_img, start)
        start = (start[0], start[1] + font.get_linesize())


class Thing:
    def __init__(self, body, *shapes):
        self.body = body
        self.shapes = shapes

    def addTo(self, space):
        if self.body is None:
            def set_static(shape):
                shape.body = space.static_body
                return shape
            space.add(*map(set_static, self.shapes))
        else:
            space.add(self.body, *self.shapes)


class Ball(Thing):
    def __init__(self, center, radius: float):
        self.is_static = False
        self.radius = radius
        # define the thing all the forces are applied to
        body = pm.Body()
        body.mass = 1.0
        body.moment = pm.moment_for_circle(body.mass, 0, radius)
        body.position = center
        # define hit box
        circle = pm.Circle(body, radius)
        circle.elasticity = 0.8
        circle.friction = 0.9
        circle.collision_type = BALL_OBJECT_TYPE
        super().__init__(body, circle)

    def drawTo(self, surface, sim_lag):
        center = (self.body.position + self.body.velocity * sim_lag).int_tuple
        pg.draw.circle(surface, pg.Color("red"), center, self.radius)


class Wall(Thing):
    def __init__(self, start: tuple, end: tuple):
        self.is_static = True
        end = pm.Vec2d(end)
        start = pm.Vec2d(start)
        self.start = start
        self.end = end
        self.radius = 10.0
        self.width = (end - start).perpendicular_normal() * self.radius
        segment = pm.Segment(None, self.start, self.end, self.radius)
        segment.elasticity = 0.8
        segment.friction = 0.9
        segment.collision_type = WALL_OBJECT_TYPE
        super().__init__(None, segment)

    def drawTo(self, surface, sim_lag):
        verts = [
            (self.start + self.width).int_tuple,
            (self.start - self.width).int_tuple,
            (self.end - self.width).int_tuple,
            (self.end + self.width).int_tuple
        ]
        pg.draw.polygon(surface, pg.Color("white"), verts)
        pg.draw.circle(surface, pg.Color("white"),
                       self.start.int_tuple, self.radius)
        pg.draw.circle(surface, pg.Color("white"),
                       self.end.int_tuple, self.radius)


world = [
    Ball((100.0, 100.0), 30.0),
    Wall((50.0, 392.0), (150.0, 400.0)),
]

background = pg.Surface(screen.get_size())
for thing in world:
    thing.addTo(space)
    if thing.is_static:
        thing.drawTo(background, 0)


def what_to_do_when_a_ball_hits_a_wall(arbiter, space, data):
    try:
        for contact in arbiter.contact_point_set.points:
            # where on the wall did the ball hit
            pg.draw.circle(background,
                           pg.Color("green"),
                           contact.point_b.int_tuple,
                           5 * arbiter.total_impulse.get_length())
    except Exception as e:
        print(e)


space.add_collision_handler(
    BALL_OBJECT_TYPE,
    WALL_OBJECT_TYPE).post_solve = what_to_do_when_a_ball_hits_a_wall

clock.tick()
while not done:
    # get how much time has passed
    dt = clock.tick()

    # get user input
    for evt in pg.event.get():
        if evt.type == pg.QUIT:
            done = True
        if evt.type == pg.KEYDOWN and evt.key == pg.K_F1:
            show_stats = not show_stats

    # update state
    sim_lag += dt
    iters = 0
    while sim_lag > SIM_STEP_SIZE:
        iters += 1
        space.step(SIM_STEP_SIZE)
        sim_lag -= SIM_STEP_SIZE

    # draw updated state
    screen.fill(pg.Color("black"))
    screen.blit(background, (0, 0))
    for thing in world:
        if not thing.is_static:
            thing.drawTo(screen, sim_lag)

    if show_stats:
        stats = f"fps {round(clock.get_fps(), 1)}\n"\
            f""
        draw_text(screen, font, (n_dash, 0), stats)

    pg.display.flip()

pg.quit()
