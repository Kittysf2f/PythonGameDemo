import pygame
import numpy as np
from config import *

class Map2DScene:
    def __init__(self, map_data, biome_name, coords):
        self.map_data = map_data
        self.biome_name = biome_name
        self.coords = coords
        self.scene_manager = None
        
        # 地图显示设置
        self.tile_size = 16
        self.map_size = map_data['tiles'].shape[0]
        self.camera_x = 0
        self.camera_y = 0
        
        # UI设置
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        # 区块颜色定义
        self.tile_colors = {
            0: (22, 80, 158),    # 水 - 蓝色
            1: (230, 214, 153),  # 沙子 - 米色
            2: (88, 161, 48),    # 草地 - 绿色
            3: (38, 112, 21),    # 树木 - 深绿色
            4: (219, 186, 112),  # 沙漠 - 黄色
            5: (240, 240, 240),  # 雪 - 白色
            6: (110, 110, 110),  # 石头 - 灰色
        }
        
        # 生物群系颜色
        self.biome_colors = {
            "Deep Ocean": (5, 22, 64),
            "Ocean": (22, 80, 158),
            "Beach": (230, 214, 153),
            "Grassland": (88, 161, 48),
            "Forest": (38, 112, 21),
            "Desert": (219, 186, 112),
            "Snow": (240, 240, 240),
            "Mountain": (110, 110, 110),
        }
    
    def set_scene_manager(self, scene_manager):
        """设置场景管理器"""
        self.scene_manager = scene_manager
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回星球场景
                if self.scene_manager:
                    self.scene_manager.switch_scene('planet')
            elif event.key == pygame.K_r:
                # 重新生成地图
                self._regenerate_map()
    
    def handle_input(self):
        """处理键盘输入"""
        keys = pygame.key.get_pressed()
        
        # 相机移动
        move_speed = 5
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera_y -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_y += move_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera_x -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_x += move_speed
        
        # 限制相机范围
        max_x = max(0, self.map_size * self.tile_size - SCREEN_WIDTH)
        max_y = max(0, self.map_size * self.tile_size - SCREEN_HEIGHT)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))
    
    def draw(self, screen):
        """绘制2D地图场景"""
        screen.fill((20, 20, 40))  # 深蓝色背景
        
        # 绘制地图
        self._draw_map(screen)
        
        # 绘制UI
        self._draw_ui(screen)
    
    def _draw_map(self, screen):
        """绘制地图区块"""
        # 计算可见区域
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_size, (self.camera_x + SCREEN_WIDTH) // self.tile_size + 1)
        end_y = min(self.map_size, (self.camera_y + SCREEN_HEIGHT) // self.tile_size + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.map_data['tiles'][y, x]
                color = self.tile_colors.get(tile_type, (100, 100, 100))
                
                # 计算屏幕坐标
                screen_x = x * self.tile_size - self.camera_x
                screen_y = y * self.tile_size - self.camera_y
                
                # 绘制区块
                pygame.draw.rect(screen, color, 
                               (screen_x, screen_y, self.tile_size, self.tile_size))
                
                # 绘制区块边框
                pygame.draw.rect(screen, (50, 50, 50), 
                               (screen_x, screen_y, self.tile_size, self.tile_size), 1)
        
        # 绘制中心点标记
        center_x = self.map_size // 2 * self.tile_size - self.camera_x
        center_y = self.map_size // 2 * self.tile_size - self.camera_y
        if 0 <= center_x <= SCREEN_WIDTH and 0 <= center_y <= SCREEN_HEIGHT:
            pygame.draw.circle(screen, (255, 0, 0), (center_x + self.tile_size//2, center_y + self.tile_size//2), 8)
            pygame.draw.circle(screen, (255, 255, 255), (center_x + self.tile_size//2, center_y + self.tile_size//2), 8, 2)
    
    def _draw_ui(self, screen):
        """绘制用户界面"""
        # 标题
        title_text = f"2D Map - {self.biome_name}"
        title_surface = self.title_font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (20, 20))
        
        # 坐标信息
        coord_text = f"Planet Coordinates: {self.coords}"
        coord_surface = self.font.render(coord_text, True, (200, 200, 200))
        screen.blit(coord_surface, (20, 60))
        
        # 地图信息
        map_info = f"Map Size: {self.map_size}x{self.map_size}"
        map_surface = self.font.render(map_info, True, (200, 200, 200))
        screen.blit(map_surface, (20, 80))
        
        # 控制提示
        controls = [
            "Controls:",
            "WASD/Arrow Keys - Move camera",
            "ESC - Return to planet view",
            "R - Regenerate map"
        ]
        
        for i, control in enumerate(controls):
            color = (255, 255, 255) if i == 0 else (150, 150, 150)
            control_surface = self.font.render(control, True, color)
            screen.blit(control_surface, (20, SCREEN_HEIGHT - 100 + i * 20))
        
        # 图例
        legend_x = SCREEN_WIDTH - 200
        legend_y = 20
        pygame.draw.rect(screen, (40, 40, 40), (legend_x - 10, legend_y - 10, 190, 200))
        
        legend_title = self.font.render("Legend:", True, (255, 255, 255))
        screen.blit(legend_title, (legend_x, legend_y))
        
        legend_items = [
            (0, "Water"),
            (1, "Sand"),
            (2, "Grass"),
            (3, "Forest"),
            (4, "Desert"),
            (5, "Snow"),
            (6, "Stone")
        ]
        
        for i, (tile_id, name) in enumerate(legend_items):
            color = self.tile_colors.get(tile_id, (100, 100, 100))
            pygame.draw.rect(screen, color, (legend_x, legend_y + 30 + i * 20, 12, 12))
            name_surface = self.font.render(name, True, (200, 200, 200))
            screen.blit(name_surface, (legend_x + 20, legend_y + 30 + i * 20))
    
    def _regenerate_map(self):
        """重新生成地图"""
        if self.scene_manager:
            # 重新生成2D地图
            map_data = self.scene_manager.map_generator.generate_2d_map(self.coords, self.biome_name)
            self.map_data = map_data
            print(f"重新生成地图: {self.biome_name}")
