import pygame
from config import *
from planet_generator import PlanetGenerator
from scene_manager import SceneManager

def main():
    # 生成行星蓝图数据
    planet_blueprint = PlanetGenerator(resolution=RESOLUTION, seed=SEED)
    planet_blueprint.generate()
    
    # 创建场景管理器
    scene_manager = SceneManager(planet=planet_blueprint)
    
    # 主游戏循环
    running = True
    while running:
        # 处理所有事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # 将其他事件传递给场景管理器处理
                scene_manager.handle_event(event)
        
        # 处理输入
        scene_manager.handle_input()
        
        # 绘制画面
        scene_manager.draw()
        
        # 控制帧率
        scene_manager.clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()