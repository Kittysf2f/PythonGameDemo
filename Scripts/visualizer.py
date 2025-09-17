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

        rot_x = np.array([[1,0,0],[0,math.cos(self.angle_x),-math.sin(self.angle_x)],[0,math.sin(self.angle_x),math.cos(self.angle_x)]])
        rot_y = np.array([[math.cos(self.angle_y),0,math.sin(self.angle_y)],[0,1,0],[-math.sin(self.angle_y),0,math.cos(self.angle_y)]])
        rotation_matrix = rot_y @ rot_x
        
        light_source = np.array([0, 0, 1])

        # 批量旋转所有点，这比在循环中逐个旋转快得多
        rotated_points = self.planet.points.reshape(-1, 3) @ rotation_matrix.T
        flat_colors = self.planet.colors.reshape(-1, 3)

        # 找到所有朝向我们的点
        front_face_indices = np.where(rotated_points[:, 2] > 0)[0]
        
        # 动态计算点的半径
        # 经验值：屏幕宽度除以分辨率得到的格子大小的一半，再稍微放大一点
        point_radius = int((SCREEN_WIDTH / self.planet.resolution) * 0.75)
        # 确保半径至少为1
        point_radius = max(1, point_radius) 

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = SCREEN_WIDTH * 0.4

        for i in front_face_indices:
            point = rotated_points[i]
            
            # 应用简单的光照
            # 我们用点的原始法向量（就是它的坐标）来计算光照
            original_normal = self.planet.points.reshape(-1, 3)[i]
            rotated_normal = original_normal @ rotation_matrix.T
            intensity = np.dot(rotated_normal, light_source)
            intensity = max(0.15, min(1.0, intensity))

            base_color = flat_colors[i]
            lit_color = (
                min(255, int(base_color[0] * intensity)),
                min(255, int(base_color[1] * intensity)),
                min(255, int(base_color[2] * intensity))
            )

            # 投影并绘制一个更大的圆
            x_proj = int(point[0] * radius + center_x)
            y_proj = int(point[1] * radius + center_y)
            pygame.draw.circle(self.screen, lit_color, (x_proj, y_proj), point_radius)

        pygame.display.flip()