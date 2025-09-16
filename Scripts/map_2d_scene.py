import pygame
import numpy as np
from config import *

class Map2DScene:
    def __init__(self, map_data, biome_name, coords):
        # 区块管理：以球面格点为key，存储已加载区块
        self.chunks = {}  # {(row, col): map_data}
        self.chunk_size = map_data['tiles'].shape[0]
        self.center_chunk_coords = coords  # 球面格点(row, col)
        self.current_chunk = coords
        self.chunks[coords] = map_data
        self.scene_manager = None

        # 地图显示设置
        self.tile_size = 16
        self.min_tile_size = 8
        self.max_tile_size = 64
        self.map_size = self.chunk_size  # 当前只显示一个区块，后续支持多区块拼接
        self.camera_x = 0
        self.camera_y = 0

        # 当前显示的区块左上角在世界中的区块坐标（row, col）
        self.display_origin_chunk = coords

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
        """处理事件，M键切换交由SceneManager统一处理，支持缩放"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.scene_manager:
                    self.scene_manager.switch_scene('planet')
            elif event.key == pygame.K_r:
                self._regenerate_map()
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self._zoom(1.1)
            elif event.y < 0:
                self._zoom(0.9)

    def _zoom(self, scale):
        """缩放地图，scale>1放大，<1缩小，保持中心不跳变"""
        old_tile_size = self.tile_size
        new_tile_size = int(self.tile_size * scale)
        new_tile_size = max(self.min_tile_size, min(self.max_tile_size, new_tile_size))
        if new_tile_size == old_tile_size:
            return
        # 计算缩放前中心点在地图中的像素坐标
        center_screen_x = SCREEN_WIDTH // 2
        center_screen_y = SCREEN_HEIGHT // 2
        center_map_x = self.camera_x + center_screen_x
        center_map_y = self.camera_y + center_screen_y
        # 缩放
        self.tile_size = new_tile_size
        # 缩放后调整camera_x, camera_y，保持视野中心不变
        new_center_map_x = int(center_map_x * self.tile_size / old_tile_size)
        new_center_map_y = int(center_map_y * self.tile_size / old_tile_size)
        self.camera_x = new_center_map_x - center_screen_x
        self.camera_y = new_center_map_y - center_screen_y
        # 限制相机范围
        max_x = max(0, self.map_size * self.tile_size - SCREEN_WIDTH)
        max_y = max(0, self.map_size * self.tile_size - SCREEN_HEIGHT)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))
    
    def handle_input(self):
        """处理键盘输入，并检测是否需要加载新块"""
        keys = pygame.key.get_pressed()
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

        # 检查是否需要加载相邻区块
        self._check_and_load_adjacent_chunk()

    def _check_and_load_adjacent_chunk(self):
        """检测视野是否越界，只有越界才切换区块"""
        # 只实现单区块切换，后续可扩展为多区块拼接
        # 如果相机超出当前区块边界，则切换到相邻区块
        # 上
        if self.camera_y < 0:
            self.camera_y = 0  # 确保相机位置不会再次触发
            self._load_chunk_in_direction(-1, 0)
            return
        # 下
        if self.camera_y > self.map_size * self.tile_size - SCREEN_HEIGHT:
            self.camera_y = self.map_size * self.tile_size - SCREEN_HEIGHT  # 确保相机位置不会再次触发
            self._load_chunk_in_direction(1, 0)
            return
        # 左
        if self.camera_x < 0:
            self.camera_x = 0  # 确保相机位置不会再次触发
            self._load_chunk_in_direction(0, -1)
            return
        # 右
        if self.camera_x > self.map_size * self.tile_size - SCREEN_WIDTH:
            self.camera_x = self.map_size * self.tile_size - SCREEN_WIDTH  # 确保相机位置不会再次触发
            self._load_chunk_in_direction(0, 1)
            return

    def _load_chunk_in_direction(self, d_row, d_col):
        """加载指定方向的新区块，并切换显示（后续可拼接）"""
        cur_row, cur_col = self.current_chunk
        new_row = (cur_row + d_row) % self.scene_manager.map_generator.planet.resolution
        new_col = (cur_col + d_col) % self.scene_manager.map_generator.planet.resolution
        new_chunk_coords = (new_row, new_col)
        if new_chunk_coords not in self.chunks:
            # 获取新块的生物群系
            color = self.scene_manager.map_generator.planet.colors[new_row, new_col]
            biome = self.scene_manager.map_generator._get_biome_from_color(color)
            # 生成新块
            map_data = self.scene_manager.map_generator.generate_2d_map(new_chunk_coords, biome)
            self.chunks[new_chunk_coords] = map_data
        else:
            # 已有区块，需获取biome
            color = self.scene_manager.map_generator.planet.colors[new_row, new_col]
            biome = self.scene_manager.map_generator._get_biome_from_color(color)

        # 切换显示新块（后续可扩展为多块拼接）
        self.current_chunk = new_chunk_coords
        self.map_data = self.chunks[new_chunk_coords]
        # 同步biome_name和coords为新块的生物群系和球面坐标
        self.biome_name = biome
        self.coords = new_chunk_coords
        # 根据切换方向重置相机到新块对边，避免无限切换
        if d_row == -1:  # 上
            self.camera_y = self.map_size * self.tile_size - SCREEN_HEIGHT
            self.camera_x = min(max(self.camera_x, 0), max(0, self.map_size * self.tile_size - SCREEN_WIDTH))
        elif d_row == 1:  # 下
            self.camera_y = 0
            self.camera_x = min(max(self.camera_x, 0), max(0, self.map_size * self.tile_size - SCREEN_WIDTH))
        elif d_col == -1:  # 左
            self.camera_x = self.map_size * self.tile_size - SCREEN_WIDTH
            self.camera_y = min(max(self.camera_y, 0), max(0, self.map_size * self.tile_size - SCREEN_HEIGHT))
        elif d_col == 1:  # 右
            self.camera_x = 0
            self.camera_y = min(max(self.camera_y, 0), max(0, self.map_size * self.tile_size - SCREEN_HEIGHT))
    
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
