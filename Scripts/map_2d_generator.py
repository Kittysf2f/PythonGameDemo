import numpy as np
import math
from config import *

class Map2DGenerator:
    def __init__(self, planet):
        self.planet = planet
        self.map_size = 50  # 2D地图大小
        self.tile_size = 16  # 每个区块的像素大小
    
    def generate_2d_map(self, center_coords, center_biome, progress_callback=None):
        """根据球面坐标和生物群系生成2D地图"""
        print(f"生成2D地图: 中心坐标{center_coords}, 生物群系{center_biome}")
        if progress_callback is None:
            progress_callback = lambda phase, p: None
        
        # 创建地图数据
        map_data = {
            'tiles': np.zeros((self.map_size, self.map_size), dtype=int),
            'biomes': np.zeros((self.map_size, self.map_size), dtype=int),
            'elevation': np.zeros((self.map_size, self.map_size)),
            'center_coords': center_coords,
            'center_biome': center_biome
        }
        progress_callback("Preparing data", 0.05)
        
        # 获取中心区域的相邻区域信息
        neighbor_info = self._get_neighbor_biomes(center_coords)
        progress_callback("Analyzing neighbor regions", 0.15)
        
        # 生成地形高度图
        self._generate_elevation(map_data, neighbor_info, progress_callback)
        
        # 根据高度和相邻区域生成生物群系
        self._generate_biomes(map_data, neighbor_info, progress_callback)
        
        # 生成具体的区块类型
        self._generate_tiles(map_data, progress_callback)
        progress_callback("Finalizing", 0.95)
        
        return map_data
    
    def _get_neighbor_biomes(self, center_coords):
        """获取中心区域周围的生物群系信息"""
        row, col = center_coords
        resolution = self.planet.resolution
        
        # 定义8个方向的偏移
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        neighbor_info = {}
        
        for i, (dr, dc) in enumerate(directions):
            new_row = (row + dr) % resolution
            new_col = (col + dc) % resolution
            
            # 获取相邻区域的生物群系
            neighbor_color = self.planet.colors[new_row, new_col]
            neighbor_biome = self._get_biome_from_color(neighbor_color)
            
            neighbor_info[i] = {
                'coords': (new_row, new_col),
                'biome': neighbor_biome,
                'color': neighbor_color
            }
        
        return neighbor_info
    
    def _get_biome_from_color(self, color):
        """根据颜色获取生物群系名称"""
        for biome, biome_color in BIOME_COLORS.items():
            if np.array_equal(color, biome_color):
                return BIOME_NAMES.get(biome, "Unknown")
        return "Unknown"
    
    def _generate_elevation(self, map_data, neighbor_info, progress_callback):
        """生成地形高度图"""
        # 使用噪声生成自然的地形
        import noise
        
        # 中心区域的高度
        center_elevation = self._get_elevation_from_biome(map_data['center_biome'])
        
        for y in range(self.map_size):
            for x in range(self.map_size):
                # 计算到中心的距离
                center_x, center_y = self.map_size // 2, self.map_size // 2
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_distance = math.sqrt(center_x**2 + center_y**2)
                normalized_distance = distance / max_distance
                
                # 基础噪声
                noise_val = noise.pnoise2(x * 0.1, y * 0.1, octaves=4, persistence=0.5)
                noise_val = (noise_val + 1) / 2  # 归一化到0-1
                
                # 根据距离中心的位置调整高度
                if normalized_distance < 0.3:
                    # 中心区域，使用中心生物群系的高度
                    elevation = center_elevation + noise_val * 0.2
                elif normalized_distance < 0.7:
                    # 过渡区域，混合中心和外围的高度
                    center_weight = 1 - (normalized_distance - 0.3) / 0.4
                    elevation = center_elevation * center_weight + noise_val * 0.3
                else:
                    # 外围区域，使用噪声生成的高度
                    elevation = noise_val
                
                map_data['elevation'][y, x] = elevation
            # 进度更新（30% - 60%）
            progress_callback("Generating elevation", 0.3 + 0.3 * (y / max(1, self.map_size - 1)))
    
    def _get_elevation_from_biome(self, biome_name):
        """根据生物群系获取基础高度"""
        elevation_map = {
            "Deep Ocean": 0.1,
            "Ocean": 0.2,
            "Beach": 0.4,
            "Grassland": 0.5,
            "Forest": 0.6,
            "Desert": 0.5,
            "Snow": 0.8,
            "Mountain": 0.9
        }
        return elevation_map.get(biome_name, 0.5)
    
    def _generate_biomes(self, map_data, neighbor_info, progress_callback):
        """根据高度和相邻区域生成生物群系"""
        for y in range(self.map_size):
            for x in range(self.map_size):
                elevation = map_data['elevation'][y, x]
                
                # 根据高度确定基础生物群系
                if elevation < 0.3:
                    base_biome = "Ocean"
                elif elevation < 0.5:
                    base_biome = "Beach"
                elif elevation < 0.7:
                    base_biome = "Grassland"
                elif elevation < 0.8:
                    base_biome = "Forest"
                else:
                    base_biome = "Mountain"
                
                # 考虑相邻区域的影响
                biome = self._blend_biomes(base_biome, neighbor_info, x, y)
                map_data['biomes'][y, x] = self._biome_to_id(biome)
            # 进度更新（60% - 85%）
            progress_callback("Assigning biomes", 0.6 + 0.25 * (y / max(1, self.map_size - 1)))
    
    def _blend_biomes(self, base_biome, neighbor_info, x, y):
        """混合生物群系，创建自然过渡"""
        center_x, center_y = self.map_size // 2, self.map_size // 2
        
        # 计算当前位置相对于中心的方向
        dx = x - center_x
        dy = y - center_y
        
        # 确定主要影响方向
        if abs(dx) > abs(dy):
            direction = 1 if dx > 0 else 3  # 右或左
        else:
            direction = 2 if dy > 0 else 0  # 下或上
        
        # 获取该方向的相邻生物群系
        if direction in neighbor_info:
            neighbor_biome = neighbor_info[direction]['biome']
            
            # 计算混合权重（距离中心越远，相邻区域影响越大）
            distance = math.sqrt(dx**2 + dy**2)
            max_distance = math.sqrt(center_x**2 + center_y**2)
            blend_weight = min(0.5, distance / max_distance)
            
            # 随机决定是否应用混合
            import random
            if random.random() < blend_weight:
                return neighbor_biome
        
        return base_biome
    
    def _biome_to_id(self, biome_name):
        """将生物群系名称转换为ID"""
        biome_ids = {
            "Deep Ocean": 0,
            "Ocean": 1,
            "Beach": 2,
            "Grassland": 3,
            "Forest": 4,
            "Desert": 5,
            "Snow": 6,
            "Mountain": 7
        }
        return biome_ids.get(biome_name, 3)
    
    def _generate_tiles(self, map_data, progress_callback):
        """生成具体的区块类型"""
        for y in range(self.map_size):
            for x in range(self.map_size):
                biome_id = map_data['biomes'][y, x]
                elevation = map_data['elevation'][y, x]
                
                # 根据生物群系和高度生成区块类型
                tile_type = self._get_tile_type(biome_id, elevation)
                map_data['tiles'][y, x] = tile_type
            # 进度更新（85% - 95%）
            progress_callback("Populating tiles", 0.85 + 0.10 * (y / max(1, self.map_size - 1)))
    
    def _get_tile_type(self, biome_id, elevation):
        """根据生物群系ID和高度获取区块类型"""
        # 这里可以根据需要定义更多的区块类型
        if biome_id == 0 or biome_id == 1:  # 海洋
            return 0  # 水
        elif biome_id == 2:  # 海滩
            return 1  # 沙子
        elif biome_id == 3:  # 草原
            return 2  # 草地
        elif biome_id == 4:  # 森林
            return 3  # 树木
        elif biome_id == 5:  # 沙漠
            return 4  # 沙漠
        elif biome_id == 6:  # 雪地
            return 5  # 雪
        elif biome_id == 7:  # 山脉
            return 6  # 石头
        else:
            return 2  # 默认草地
