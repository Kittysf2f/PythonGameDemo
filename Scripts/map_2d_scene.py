import pygame
import numpy as np
from config import *

class Map2DScene:
    def __init__(self, map_generator):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Map Scene")
        self.clock = pygame.time.Clock()
        
        self.map_generator = map_generator
        
        # 摄像机状态
        self.camera_x = 0
        self.camera_y = 0
        self.tiles_on_screen = INITIAL_TILES_ON_SCREEN  # 屏幕显示的瓦片数量
        
        # 当前区块位置
        self.current_chunk_x = 0
        self.current_chunk_y = 0
        self.last_chunk_x = None
        self.last_chunk_y = None
        
        # 已加载的区块
        self.loaded_chunks = {}
        
        # 瓦片类型到颜色的映射
        self.tile_colors = {
            0: TILE_TYPES["WATER"],
            1: TILE_TYPES["GRASS"],
            2: TILE_TYPES["SAND"],
            3: TILE_TYPES["ROCK"],
            4: TILE_TYPES["SNOW"],
            5: TILE_TYPES["FOREST"],
            6: TILE_TYPES["DESERT"],
        }
        
        # 字体
        self.font = pygame.font.Font(None, 24)
    
    def start_new_map(self, biome_name, selected_tile):
        """开始新的2D地图，基于选择的球面瓦片"""
        print(f"开始2D地图，生物群系: {biome_name}, 瓦片坐标: {selected_tile}")
        
        # 重置摄像机位置到初始区块中心
        self.camera_x = CHUNK_SIZE // 2  # 区块中心X坐标
        self.camera_y = CHUNK_SIZE // 2  # 区块中心Y坐标
        self.tiles_on_screen = INITIAL_TILES_ON_SCREEN
        
        # 计算当前区块位置（初始区块为(0,0)）
        self.current_chunk_x = 0
        self.current_chunk_y = 0
        self.last_chunk_x = None
        self.last_chunk_y = None
        
        # 清空已加载的区块
        self.loaded_chunks = {}
        
        # 加载初始区块
        self._load_chunks_around_current()
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回场景A
                if hasattr(self, 'scene_manager'):
                    self.scene_manager.return_to_scene_a()
                else:
                    print("返回场景A")
        elif event.type == pygame.MOUSEWHEEL:
            # 处理鼠标滚轮缩放
            self._handle_mouse_wheel(event.y)
    
    def handle_input(self):
        """处理输入"""
        keys = pygame.key.get_pressed()
        
        # 计算当前缩放级别（基于瓦片大小）
        tile_size = SCREEN_WIDTH / self.tiles_on_screen
        move_speed = CAMERA_SPEED * tile_size / TILE_SIZE
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera_y -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_y += move_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera_x -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_x += move_speed
        
        # 检查是否需要加载新区块
        self._update_current_chunk()
    
    def _handle_mouse_wheel(self, wheel_direction):
        """处理鼠标滚轮缩放"""
        if wheel_direction > 0:  # 向上滚动，放大
            self.tiles_on_screen = max(MIN_TILES_ON_SCREEN, self.tiles_on_screen - ZOOM_SPEED * 10)
        else:  # 向下滚动，缩小
            self.tiles_on_screen = min(MAX_TILES_ON_SCREEN, self.tiles_on_screen + ZOOM_SPEED * 10)
    
    def _update_current_chunk(self):
        """更新当前区块位置"""
        # 计算当前摄像机位置对应的区块坐标（基于瓦片坐标）
        new_chunk_x = int(self.camera_x // CHUNK_SIZE)
        new_chunk_y = int(self.camera_y // CHUNK_SIZE)
        
        # 如果区块位置发生变化，重新加载区块
        if new_chunk_x != self.current_chunk_x or new_chunk_y != self.current_chunk_y:
            print(f"区块位置变化: ({self.current_chunk_x}, {self.current_chunk_y}) -> ({new_chunk_x}, {new_chunk_y})")
            self.current_chunk_x = new_chunk_x
            self.current_chunk_y = new_chunk_y
            self._load_chunks_around_current()
    
    def _load_chunks_around_current(self):
        """加载当前区块周围的区块"""
        # 清空已加载的区块
        self.loaded_chunks = {}
        
        # 加载周围区块
        for dx in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
            for dy in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
                chunk_x = self.current_chunk_x + dx
                chunk_y = self.current_chunk_y + dy
                chunk_key = (chunk_x, chunk_y)
                
                # 获取区块数据
                chunk_data = self.map_generator.get_chunk(chunk_x, chunk_y)
                self.loaded_chunks[chunk_key] = chunk_data
        
        print(f"加载了 {len(self.loaded_chunks)} 个区块，中心位置: ({self.current_chunk_x}, {self.current_chunk_y})")
    
    def draw(self):
        """绘制2D地图"""
        self.screen.fill((50, 50, 50))  # 深灰色背景
        
        # 计算当前瓦片大小
        tile_size = SCREEN_WIDTH / self.tiles_on_screen
        
        # 计算可见区域（基于瓦片坐标）
        visible_left = int(self.camera_x - SCREEN_WIDTH // 2 / tile_size)
        visible_top = int(self.camera_y - SCREEN_HEIGHT // 2 / tile_size)
        visible_right = int(self.camera_x + SCREEN_WIDTH // 2 / tile_size)
        visible_bottom = int(self.camera_y + SCREEN_HEIGHT // 2 / tile_size)
        
        # 绘制可见的区块
        for chunk_key, chunk_data in self.loaded_chunks.items():
            chunk_x, chunk_y = chunk_key
            
            # 计算区块在屏幕上的位置（基于瓦片坐标）
            chunk_screen_x = (chunk_x * CHUNK_SIZE - self.camera_x) * tile_size + SCREEN_WIDTH // 2
            chunk_screen_y = (chunk_y * CHUNK_SIZE - self.camera_y) * tile_size + SCREEN_HEIGHT // 2
            
            # 计算区块在屏幕上的大小
            chunk_screen_width = CHUNK_SIZE * tile_size
            chunk_screen_height = CHUNK_SIZE * tile_size
            
            # 检查区块是否在可见区域内
            if (chunk_screen_x + chunk_screen_width > 0 and chunk_screen_x < SCREEN_WIDTH and
                chunk_screen_y + chunk_screen_height > 0 and chunk_screen_y < SCREEN_HEIGHT):
                
                self._draw_chunk(chunk_data, chunk_screen_x, chunk_screen_y, tile_size)
        
        # 绘制区块边界（如果启用）
        if SHOW_CHUNK_BORDERS:
            self._draw_chunk_borders(tile_size)
        
        # 绘制UI信息
        self._draw_ui()
        
        pygame.display.flip()
    
    def _draw_chunk(self, chunk_data, screen_x, screen_y, tile_size):
        """绘制单个区块"""
        # 如果瓦片太小，只绘制一个代表色
        if tile_size < 2:
            # 计算区块的主要颜色
            unique_types, counts = np.unique(chunk_data, return_counts=True)
            main_type = unique_types[np.argmax(counts)]
            tile_color = self.tile_colors.get(main_type, (100, 100, 100))
            pygame.draw.rect(self.screen, tile_color, (screen_x, screen_y, CHUNK_SIZE * tile_size, CHUNK_SIZE * tile_size))
        else:
            # 绘制区块中的每个瓦片
            step = max(1, int(tile_size // 4))  # 根据瓦片大小调整绘制步长
            for x in range(0, CHUNK_SIZE, step):
                for y in range(0, CHUNK_SIZE, step):
                    if x < CHUNK_SIZE and y < CHUNK_SIZE:
                        tile_type = chunk_data[x, y]
                        tile_color = self.tile_colors.get(tile_type, (100, 100, 100))
                        
                        # 计算瓦片在屏幕上的位置
                        tile_screen_x = screen_x + x * tile_size
                        tile_screen_y = screen_y + y * tile_size
                        
                        # 绘制瓦片
                        pygame.draw.rect(self.screen, tile_color, 
                                       (tile_screen_x, tile_screen_y, tile_size * step, tile_size * step))
    
    def _draw_chunk_borders(self, tile_size):
        """绘制区块边界"""
        # 计算可见区块范围
        visible_left_chunk = int((self.camera_x - SCREEN_WIDTH // 2 / tile_size) // CHUNK_SIZE)
        visible_right_chunk = int((self.camera_x + SCREEN_WIDTH // 2 / tile_size) // CHUNK_SIZE)
        visible_top_chunk = int((self.camera_y - SCREEN_HEIGHT // 2 / tile_size) // CHUNK_SIZE)
        visible_bottom_chunk = int((self.camera_y + SCREEN_HEIGHT // 2 / tile_size) // CHUNK_SIZE)
        
        # 绘制垂直边界线
        for chunk_x in range(visible_left_chunk - 1, visible_right_chunk + 2):
            chunk_screen_x = (chunk_x * CHUNK_SIZE - self.camera_x) * tile_size + SCREEN_WIDTH // 2
            
            # 检查边界线是否在可见区域内
            if -2 < chunk_screen_x < SCREEN_WIDTH + 2:
                pygame.draw.line(self.screen, (255, 0, 0), 
                               (chunk_screen_x, 0), (chunk_screen_x, SCREEN_HEIGHT), 2)
        
        # 绘制水平边界线
        for chunk_y in range(visible_top_chunk - 1, visible_bottom_chunk + 2):
            chunk_screen_y = (chunk_y * CHUNK_SIZE - self.camera_y) * tile_size + SCREEN_HEIGHT // 2
            
            # 检查边界线是否在可见区域内
            if -2 < chunk_screen_y < SCREEN_HEIGHT + 2:
                pygame.draw.line(self.screen, (255, 0, 0), 
                               (0, chunk_screen_y), (SCREEN_WIDTH, chunk_screen_y), 2)
    
    def _draw_ui(self):
        """绘制UI信息"""
        # 显示摄像机位置
        camera_text = f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})"
        camera_surface = self.font.render(camera_text, True, (255, 255, 255))
        self.screen.blit(camera_surface, (10, 10))
        
        # 显示缩放级别（瓦片数量）
        zoom_text = f"Tiles on Screen: {self.tiles_on_screen:.0f}x{self.tiles_on_screen:.0f}"
        zoom_surface = self.font.render(zoom_text, True, (255, 255, 255))
        self.screen.blit(zoom_surface, (10, 35))
        
        # 显示当前区块位置
        chunk_text = f"Chunk: ({self.current_chunk_x}, {self.current_chunk_y})"
        chunk_surface = self.font.render(chunk_text, True, (255, 255, 255))
        self.screen.blit(chunk_surface, (10, 60))
        
        # 显示已加载区块数量
        loaded_text = f"Loaded Chunks: {len(self.loaded_chunks)}"
        loaded_surface = self.font.render(loaded_text, True, (255, 255, 255))
        self.screen.blit(loaded_surface, (10, 85))
        
        # 显示控制提示
        controls_text = "WASD/Arrows: Move | Mouse Wheel: Zoom | M: Switch Scene | ESC: Back to Planet"
        controls_surface = self.font.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (10, SCREEN_HEIGHT - 25))
    
    def set_scene_manager(self, scene_manager):
        """设置场景管理器"""
        self.scene_manager = scene_manager
