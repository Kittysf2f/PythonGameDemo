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
        
        # 游戏状态管理
        self.game_state = "selection"  # "selection" 或 "playing"
        self.selected_region = None
        self.selected_coords = None
        
        # UI设置
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 24)
        
        # 按钮设置
        self.button_width = 150
        self.button_height = 40
        self.button_x = SCREEN_WIDTH - self.button_width - 20
        self.button_y = 20
        
        # 按钮状态管理
        self.button_hovered = False
        self.button_pressed = False

    def handle_input(self):
        # 处理键盘输入
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.angle_x -= ROTATION_SPEED
        if keys[pygame.K_s]: self.angle_x += ROTATION_SPEED
        if keys[pygame.K_a]: self.angle_y -= ROTATION_SPEED
        if keys[pygame.K_d]: self.angle_y += ROTATION_SPEED
        # 钳制旋转角度
        self.angle_x = np.clip(self.angle_x, math.pi/3, math.pi*2/3)
        
        # 按ESC键返回选择模式
        if keys[pygame.K_ESCAPE] and self.game_state == "playing":
            self.game_state = "selection"
            print("返回区域选择模式")
        
        # 处理鼠标移动（实时更新悬停状态）
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self._handle_mouse_motion(mouse_x, mouse_y)
    
    def handle_event(self, event):
        """处理单个事件"""
        if event.type == pygame.MOUSEMOTION:
            # 处理鼠标移动
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self._handle_mouse_motion(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # 检查是否点击了开始游戏按钮
                if self._is_button_clicked(mouse_x, mouse_y):
                    self.button_pressed = True
                    if self.selected_region is not None:
                        self._start_game()
                else:
                    # 检查是否点击了星球上的区域
                    if self.game_state == "selection":
                        self._handle_planet_click(mouse_x, mouse_y)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.button_pressed = False
    
    def _handle_mouse_motion(self, mouse_x, mouse_y):
        """处理鼠标移动事件"""
        # 检查鼠标是否悬停在按钮上
        self.button_hovered = self._is_button_clicked(mouse_x, mouse_y)
    
    def _is_button_clicked(self, mouse_x, mouse_y):
        """检查鼠标是否点击了开始游戏按钮"""
        return (self.button_x <= mouse_x <= self.button_x + self.button_width and
                self.button_y <= mouse_y <= self.button_y + self.button_height)
    
    def _handle_planet_click(self, mouse_x, mouse_y):
        """处理点击星球选择区域"""
        # 计算点击位置相对于星球中心的位置
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = SCREEN_WIDTH * 0.4
        
        # 将屏幕坐标转换为球面坐标
        click_x = (mouse_x - center_x) / radius
        click_y = (mouse_y - center_y) / radius
        
        # 检查点击是否在星球范围内
        distance_from_center = math.sqrt(click_x**2 + click_y**2)
        if distance_from_center <= 1.0:
            # 找到最接近的星球点
            closest_point = self._find_closest_planet_point(click_x, click_y)
            if closest_point is not None:
                self.selected_coords = closest_point
                self.selected_region = self.planet.colors[closest_point[0], closest_point[1]]
                # 找到对应的生物群系名称
                biome_name = self._get_biome_name(self.selected_region)
                print(f"选择了区域: 坐标({closest_point[0]}, {closest_point[1]}), 生物群系: {biome_name}")
    
    def _find_closest_planet_point(self, click_x, click_y):
        """找到最接近点击位置的星球点"""
        # 计算旋转矩阵
        rot_x = np.array([[1,0,0],[0,math.cos(self.angle_x),-math.sin(self.angle_x)],[0,math.sin(self.angle_x),math.cos(self.angle_x)]])
        rot_y = np.array([[math.cos(self.angle_y),0,math.sin(self.angle_y)],[0,1,0],[-math.sin(self.angle_y),0,math.cos(self.angle_y)]])
        rotation_matrix = rot_y @ rot_x
        
        # 旋转所有点
        rotated_points = self.planet.points.reshape(-1, 3) @ rotation_matrix.T
        
        # 找到朝向我们的点
        front_face_indices = np.where(rotated_points[:, 2] > 0)[0]
        
        if len(front_face_indices) == 0:
            return None
        
        # 计算投影坐标
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = SCREEN_WIDTH * 0.4
        
        min_distance = float('inf')
        closest_point = None
        
        for i in front_face_indices:
            point = rotated_points[i]
            x_proj = point[0] * radius + center_x
            y_proj = point[1] * radius + center_y
            
            # 计算距离
            distance = math.sqrt((x_proj - (click_x * radius + center_x))**2 + 
                               (y_proj - (click_y * radius + center_y))**2)
            
            if distance < min_distance:
                min_distance = distance
                # 将一维索引转换回二维坐标
                row = i // self.planet.resolution
                col = i % self.planet.resolution
                closest_point = (row, col)
        
        return closest_point
    
    def _get_biome_name(self, color):
        """根据颜色获取生物群系名称"""
        for biome, biome_color in BIOME_COLORS.items():
            if np.array_equal(color, biome_color):
                return BIOME_NAMES.get(biome, "Unknown")
        return "Unknown"
    
    def _start_game(self):
        """开始游戏"""
        if hasattr(self, 'scene_manager'):
            # 获取生物群系名称
            biome_name = self._get_biome_name(self.selected_region)
            # 启动2D地图场景
            self.scene_manager.start_2d_map(biome_name, self.selected_coords)
        else:
            # 如果没有场景管理器，使用原来的逻辑
            self.game_state = "playing"
            biome_name = self._get_biome_name(self.selected_region)
            print(f"游戏开始！初始区域: 坐标{self.selected_coords}, 生物群系: {biome_name}")
    
    def set_scene_manager(self, scene_manager):
        """设置场景管理器"""
        self.scene_manager = scene_manager

    def draw(self, screen=None):
        if screen is None:
            screen = self.screen
        screen.fill((10, 10, 20))

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
            
            # 检查是否是选中的区域
            row = i // self.planet.resolution
            col = i % self.planet.resolution
            is_selected = (self.selected_coords is not None and 
                          row == self.selected_coords[0] and 
                          col == self.selected_coords[1])
            
            if is_selected:
                # 选中区域用更亮的高亮显示
                # 增加亮度
                bright_color = (
                    min(255, int(lit_color[0] * 1.3)),
                    min(255, int(lit_color[1] * 1.3)),
                    min(255, int(lit_color[2] * 1.3))
                )
                # 绘制更大的圆作为高亮背景
                pygame.draw.circle(screen, bright_color, (x_proj, y_proj), point_radius + 3)
                # 绘制原始颜色的圆
                pygame.draw.circle(screen, lit_color, (x_proj, y_proj), point_radius)
                # 绘制白色边框
                pygame.draw.circle(screen, (255, 255, 255), (x_proj, y_proj), point_radius + 2, 3)
                # 绘制内层金色边框
                pygame.draw.circle(screen, (255, 215, 0), (x_proj, y_proj), point_radius - 1, 2)
            else:
                pygame.draw.circle(screen, lit_color, (x_proj, y_proj), point_radius)

        # 绘制UI元素
        self._draw_ui(screen)

        pygame.display.flip()
    
    def _draw_ui(self, screen):
        """绘制用户界面元素"""
        if self.game_state == "selection":
            # 绘制开始游戏按钮
            # 基础颜色
            if self.selected_region is not None:
                base_color = (50, 150, 50)  # 绿色
            else:
                base_color = (100, 100, 100)  # 灰色
            
            # 根据状态调整颜色
            if self.button_pressed:
                # 点击时变暗
                button_color = tuple(max(0, c - 30) for c in base_color)
            elif self.button_hovered:
                # 悬停时稍微变亮
                button_color = tuple(min(255, c + 20) for c in base_color)
            else:
                button_color = base_color
            
            pygame.draw.rect(screen, button_color, 
                           (self.button_x, self.button_y, self.button_width, self.button_height))
            pygame.draw.rect(screen, (200, 200, 200), 
                           (self.button_x, self.button_y, self.button_width, self.button_height), 2)
            
            # 按钮文字
            button_text = "Start Game" if self.selected_region is not None else "Select Region"
            text_surface = self.button_font.render(button_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.button_x + self.button_width//2, 
                                                    self.button_y + self.button_height//2))
            screen.blit(text_surface, text_rect)
            
            # 绘制选择提示
            if self.selected_region is None:
                hint_text = "Click on planet to select starting region"
                hint_surface = self.button_font.render(hint_text, True, (200, 200, 200))
                screen.blit(hint_surface, (20, SCREEN_HEIGHT - 30))
            else:
                biome_name = self._get_biome_name(self.selected_region)
                hint_text = f"Selected: {self.selected_coords} ({biome_name})"
                hint_surface = self.button_font.render(hint_text, True, (100, 255, 100))
                screen.blit(hint_surface, (20, SCREEN_HEIGHT - 30))
        
        elif self.game_state == "playing":
            # 游戏进行中的UI
            game_text = "Game Running..."
            game_surface = self.font.render(game_text, True, (255, 255, 255))
            screen.blit(game_surface, (20, 20))
            
            biome_name = self._get_biome_name(self.selected_region)
            region_text = f"Current Location: {self.selected_coords} ({biome_name})"
            region_surface = self.button_font.render(region_text, True, (200, 200, 200))
            screen.blit(region_surface, (20, 60))
            
            # 返回选择模式提示
            hint_text = "Press ESC to return to region selection"
            hint_surface = self.button_font.render(hint_text, True, (150, 150, 150))
            screen.blit(hint_surface, (20, SCREEN_HEIGHT - 30))