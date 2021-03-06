import pygame
import colors
from field import Field
from chart import Chart
from shapes import *

class Game:
    def __init__(self, obstacle_pos=None, auto_mode=False, screen_width=640, screen_height=400):
        self._done = False
        self.auto_mode = auto_mode
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        # init pygame
        pygame.init()
        pygame.display.set_caption("Game")
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        self.FRAME_RATE = 60
        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.default_font = pygame.font.SysFont(pygame.font.get_default_font(), 23)
        self.info_font = self.default_font

        self.enable_display = True

        # position for displaying history chart
        self.CHART_POS = (30, 220)

        # field and player objects for each game
        self.obstacle_pos = obstacle_pos
        self.field = None
        self.info = None
        self.history_chart = None

        self.setup_game()

    def _draw_field(self):
        shapes = self.field.get_shapes()
        for shape in shapes:
            self._draw_shape(shape)

    def _draw_info_panel(self):
        x, y = 30, 30
        font_height = self.default_font.get_height()

        # By default, display scores only
        score = self.field.get_score()
        text = self.info_font.render("Score: {:.1f}".format(score), True, colors.WHITE)
        self.screen.blit(text, (x, y))

        # display information
        if self.info:
            for key, val in self.info:
                y += font_height
                info_text = self.info_font.render("{}: {}".format(key, val), True, colors.WHITE)
                self.screen.blit(info_text, (x, y))

    def _draw_history_panel(self):
        if self.history_chart:
            shapes = self.history_chart.get_shapes()
            for shape in shapes:
                self._draw_shape(shape)

    def _draw_shape(self, shape):
        if isinstance(shape, Line):
            pygame.draw.aaline(self.screen, shape.color, shape.start_pos, shape.end_pos, shape.width)
        elif isinstance(shape, Rectangle):
            pygame.draw.rect(self.screen, shape.color, (shape.x, shape.y, shape.width, shape.height))
        elif isinstance(shape, Circle):
            pygame.draw.circle(self.screen, shape.color, shape.pos, shape.radius, shape.width)
        elif isinstance(shape, DashLine):
            for line in shape.lines:
                self._draw_shape(line)
        elif isinstance(shape, Text):
            self.screen.blit(shape.text_surface, shape.pos)
        else:
            print "[ERROR] Unknown shape type {}!".format(shape.__class__.__name__)

    def setup_game(self):
        self.field = Field(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, obstacle_pos=self.obstacle_pos)

    def is_over(self):
        return self.field.check_is_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    # toggle display
                    self.enable_display = not self.enable_display
                    print "Display Mode: {}".format(self.enable_display)
                if event.key == pygame.K_r and self.is_over():
                    # restart game
                    self.setup_game()

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_q] or pressed[pygame.K_ESCAPE]:
            # quit game
            self._done = True
        if not self.auto_mode:
            if pressed[pygame.K_SPACE] or pressed[pygame.K_UP]:
                # jump
                self.field.jump()
            if pressed[pygame.K_LEFT]:
                # move left
                self.field.move("left")
            if pressed[pygame.K_RIGHT]:
                # move right
                self.field.move("right")

    def update_screen(self):
        self.screen.fill(colors.BLACK)

        self._draw_field()
        self._draw_info_panel()
        if self.history_chart:
            self._draw_history_panel()

        pygame.display.flip()
        self.clock.tick(self.FRAME_RATE)

    def on_update(self):
        """Things to do when frame get updated"""
        self.field.update()

    def start(self):
        while not self._done:
            self.handle_events()

            if not self.is_over():
                self.update_screen()
                self.on_update()

    def show(self, actions, info=None, history=None):
        self.field = Field(self.SCREEN_WIDTH, self.SCREEN_HEIGHT,
                           obstacle_pos=self.obstacle_pos, player_actions=actions)
        self.info = info

        if history:
            x_values = [float(gen_info['Generation']) for gen_info in history]
            y_values = [float(gen_info['Highest Fitness']) for gen_info in history]
            highest_fitness = y_values[-1]
            avg_values = [float(gen_info['Average Fitness']) for gen_info in history]
            avg_fitness = avg_values[-1]
            self.history_chart = Chart(caption="Generation History",
                                       width=280, height=180, margin=20,
                                       pos=self.CHART_POS, x_label="Generation", y_label="Fitness")
            self.history_chart.add_curve(x_values, y_values)
            self.history_chart.add_curve(x_values, avg_values, color=colors.BLUE)
            self.history_chart.add_constant(highest_fitness, label="Highest Fitness {}".format(highest_fitness),
                                            color=colors.WHITE)
            self.history_chart.add_constant(avg_fitness, label="Average Fitness {}".format(avg_fitness),
                                            color=colors.BLUE)

        while not self.is_over():
            self.handle_events()

            if self.enable_display:
                self.update_screen()

            self.on_update()


if __name__ == '__main__':
    game = Game()
    game.start()
