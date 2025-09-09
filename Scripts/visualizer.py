import pygame
import numpy as np
import math
from config import *

class Visualizer:
    def __init__(self, planet):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Procedural Planet Generator")
        self.clock = pygame.time.Clock()
        self.planet = planet
        self.angle_x, self.angle_y = math.pi/2, 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.angle_x -= ROTATION_SPEED
        if keys[pygame.K_s]: self.angle_x += ROTATION_SPEED
        if keys[pygame.K_a]: self.angle_y -= ROTATION_SPEED
        if keys[pygame.K_d]: self.angle_y += ROTATION_SPEED
        # 钳制旋转角度
        self.angle_x = np.clip(self.angle_x, math.pi/3, math.pi*2/3)

    def draw(self):
        self.screen.fill((10, 10, 20))
        rot_x = np.array([[1, 0, 0], [0, math.cos(self.angle_x), -math.sin(self.angle_x)], [0, math.sin(self.angle_x), math.cos(self.angle_x)]])
        rot_y = np.array([[math.cos(self.angle_y), 0, math.sin(self.angle_y)], [0, 1, 0], [-math.sin(self.angle_y), 0, math.cos(self.angle_y)]])
        rotation_matrix = rot_y @ rot_x
        rotated_points = self.planet.points.reshape(-1, 3) @ rotation_matrix.T
        radius = SCREEN_WIDTH * 0.4
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        flat_colors = self.planet.colors.reshape(-1, 3)
        front_face_indices = np.where(rotated_points[:, 2] > 0)[0]
        
        for i in front_face_indices:
            point = rotated_points[i]
            color = flat_colors[i]
            x_proj = int(point[0] * radius + center_x)
            y_proj = int(point[1] * radius + center_y)
            pygame.draw.circle(self.screen, color, (x_proj, y_proj), 2)

        pygame.display.flip()