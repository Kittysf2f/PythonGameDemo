import pygame
import numpy as np
import threading
from visualizer import Visualizer
from map_2d_generator import Map2DGenerator
from map_2d_scene import Map2DScene
from config import *

class SceneManager:
    def __init__(self, planet):
        # pygame已在main.py初始化
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Procedural Planet Generator")
        self.clock = pygame.time.Clock()

        # 记录当前2D地图场景名
        self.last_map_scene_name = None

        # 加载状态
        self.loading_active = False
        self.loading_progress = 0.0
        self.loading_text = "Loading..."
        self._loading_thread = None
        self._pending_map_scene_name = None

        # 场景管理
        self.current_scene = None
        self.scenes = {}

        # 初始化3D星球场景
        self.planet_scene = Visualizer(planet=planet)
        self.planet_scene.set_scene_manager(self)
        self.scenes['planet'] = self.planet_scene

        # 2D地图生成器
        self.map_generator = Map2DGenerator(planet)

        # 设置初始场景
        self.switch_scene('planet')
    
    def switch_scene(self, scene_name):
        """切换场景"""
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            print(f"切换到场景: {scene_name}")
            # 记录2D地图场景名
            if scene_name.startswith("map_"):
                self.last_map_scene_name = scene_name
        else:
            print(f"场景不存在: {scene_name}")
    
    def start_2d_map(self, biome_name, coords):
        """启动2D地图场景"""
        # 启动异步加载
        if self.loading_active:
            return
        self.loading_active = True
        self.loading_progress = 0.0
        self.loading_text = f"Generating 2D map at {coords} ({biome_name})"
        self._pending_map_scene_name = f"map_{int(coords[0])}_{int(coords[1])}"

        # 记录2D地图场景名
        self.last_map_scene_name = self._pending_map_scene_name

        def _progress_cb(phase, progress):
            # phase: str, progress: 0..1
            self.loading_progress = max(0.0, min(1.0, float(progress)))
            self.loading_text = phase

        def _worker():
            try:
                map_data = self.map_generator.generate_2d_map(coords, biome_name, progress_callback=_progress_cb)
                if self._pending_map_scene_name not in self.scenes:
                    map_scene = Map2DScene(map_data, biome_name, coords)
                    map_scene.set_scene_manager(self)
                    self.scenes[self._pending_map_scene_name] = map_scene
                # 加载完成
                self.loading_progress = 1.0
                self.loading_text = "Completed"
            except Exception as e:
                import traceback
                print("[SceneManager] Error while generating 2D map:", e)
                traceback.print_exc()
            finally:
                # 切换到2D地图场景
                self.loading_active = False
                if self._pending_map_scene_name:
                    self.switch_scene(self._pending_map_scene_name)
                    self._pending_map_scene_name = None

        self._loading_thread = threading.Thread(target=_worker, daemon=True)
        self._loading_thread.start()
    
    def handle_event(self, event):
        """处理事件，包括M键切换场景"""
        # 处理M键切换
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            # 当前为球面场景且有2D地图，切到2D地图
            if self.current_scene == self.planet_scene and self.last_map_scene_name:
                self.switch_scene(self.last_map_scene_name)
                return
            # 当前为2D地图场景，切回球面
            elif self.current_scene != self.planet_scene:
                self.switch_scene('planet')
                return
        # 其他事件交给当前场景
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def handle_input(self):
        """处理输入"""
        if self.current_scene:
            self.current_scene.handle_input()
    
    def draw(self):
        """绘制当前场景"""
        if self.loading_active:
            # 绘制加载界面
            self._draw_loading_screen()
        else:
            if self.current_scene:
                self.current_scene.draw(self.screen)
            # 确保每帧刷新
            pygame.display.flip()

    def _draw_loading_screen(self):
        self.screen.fill((15, 15, 25))
        # 文本
        font = pygame.font.Font(None, 36)
        sub_font = pygame.font.Font(None, 24)
        title_surface = font.render("Loading...", True, (255, 255, 255))
        text_surface = sub_font.render(self.loading_text, True, (200, 200, 200))
        self.screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(text_surface, (SCREEN_WIDTH//2 - text_surface.get_width()//2, SCREEN_HEIGHT//2 - 30))
        
        # 进度条
        bar_w, bar_h = SCREEN_WIDTH * 0.6, 20
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = SCREEN_HEIGHT // 2 + 10
        pygame.draw.rect(self.screen, (60, 60, 80), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * self.loading_progress)
        pygame.draw.rect(self.screen, (80, 180, 80), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2)
        
        pygame.display.flip()
    
    def get_planet_scene(self):
        """获取星球场景"""
        return self.planet_scene
