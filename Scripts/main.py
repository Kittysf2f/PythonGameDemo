import pygame
from config import *
from planet_generator import PlanetGenerator
from visualizer import Visualizer

def main():
    # 初始化pygame
    pygame.init()

    # 生成行星蓝图数据
    planet_blueprint = PlanetGenerator(resolution=RESOLUTION, seed=SEED)
    planet_blueprint.generate()
    
    # 创建可视化器实例
    viz = Visualizer(planet=planet_blueprint)
    # 主游戏循环
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 处理输入
        viz.handle_input()
        
        # 绘制画面
        viz.draw()
        
        # 控制帧率
        viz.clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()