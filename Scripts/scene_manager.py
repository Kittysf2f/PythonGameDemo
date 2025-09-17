import pygame
from config import *
from visualizer import Visualizer
from map_2d_scene import Map2DScene
from map_2d_generator import Map2DGenerator

class SceneManager:
    def __init__(self, planet):
        self.planet = planet
        self.current_scene = SCENE_A
        self.scene_a = None
        self.scene_b = None
        
        # 初始化场景A（球面地图场景）
        self._init_scene_a()
    
    def _init_scene_a(self):
        """初始化场景A（球面地图场景）"""
        self.scene_a = Visualizer(self.planet)
        self.scene_a.set_scene_manager(self)
    
    def _init_scene_b(self, biome_name, selected_tile):
        """初始化场景B（2D地图场景）"""
        if self.scene_b is None:
            # 创建2D地图生成器
            map_generator = Map2DGenerator(self.planet)
            # 创建2D地图场景
            self.scene_b = Map2DScene(map_generator)
            self.scene_b.set_scene_manager(self)
        
        # 启动2D地图场景
        self.scene_b.start_new_map(biome_name, selected_tile)
    
    def start_2d_map(self, biome_name, selected_tile):
        """从场景A切换到场景B"""
        print(f"切换到2D地图场景，生物群系: {biome_name}, 瓦片坐标: {selected_tile}")
        self.current_scene = SCENE_B
        self._init_scene_b(biome_name, selected_tile)
    
    def return_to_scene_a(self):
        """从场景B返回到场景A"""
        print("返回到球面地图场景")
        self.current_scene = SCENE_A
    
    def handle_event(self, event):
        """处理事件"""
        # 处理M键切换场景
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            if self.current_scene == SCENE_A and self.scene_b is not None:
                print("M键切换：从场景A切换到场景B")
                self.current_scene = SCENE_B
            elif self.current_scene == SCENE_B:
                print("M键切换：从场景B切换到场景A")
                self.current_scene = SCENE_A
        
        # 将事件传递给当前场景
        if self.current_scene == SCENE_A:
            if self.scene_a:
                self.scene_a.handle_event(event)
        elif self.current_scene == SCENE_B:
            if self.scene_b:
                self.scene_b.handle_event(event)
    
    def handle_input(self):
        """处理输入"""
        if self.current_scene == SCENE_A:
            if self.scene_a:
                self.scene_a.handle_input()
        elif self.current_scene == SCENE_B:
            if self.scene_b:
                self.scene_b.handle_input()
    
    def draw(self):
        """绘制当前场景"""
        if self.current_scene == SCENE_A:
            if self.scene_a:
                self.scene_a.draw()
        elif self.current_scene == SCENE_B:
            if self.scene_b:
                self.scene_b.draw()
    
    @property
    def clock(self):
        """获取时钟对象"""
        if self.current_scene == SCENE_A:
            return self.scene_a.clock if self.scene_a else None
        elif self.current_scene == SCENE_B:
            return self.scene_b.clock if self.scene_b else None
        return None
