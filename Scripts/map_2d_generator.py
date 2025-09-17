import numpy as np
import noise
import random
from config import *

class Map2DGenerator:
    def __init__(self, planet):
        self.planet = planet
        self.generated_chunks = {}  # 存储已生成的区块 {(chunk_x, chunk_y): chunk_data}
        self.global_seed = planet.seed  # 使用行星种子确保一致性
    
    def get_chunk(self, chunk_x, chunk_y):
        """获取指定坐标的区块，如果不存在则生成"""
        chunk_key = (chunk_x, chunk_y)
        
        if chunk_key not in self.generated_chunks:
            # 生成新区块
            self.generated_chunks[chunk_key] = self._generate_chunk(chunk_x, chunk_y)
        
        return self.generated_chunks[chunk_key]
    
    def _generate_chunk(self, chunk_x, chunk_y):
        """生成指定坐标的区块"""
        # 获取对应的球面瓦片坐标
        planet_tile = self._chunk_to_planet_tile(chunk_x, chunk_y)
        
        # 获取主瓦片和邻近瓦片的生物群系信息
        main_biome = self._get_planet_biome(planet_tile[0], planet_tile[1])
        neighbor_biomes = self._get_neighbor_biomes(planet_tile[0], planet_tile[1])
        
        # 生成区块数据
        chunk_data = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 根据生物群系生成不同的地形
        if main_biome in ["DEEP_OCEAN", "OCEAN"]:
            # 海洋生物群系：生成较多水域
            chunk_data = self._generate_ocean_chunk(chunk_x, chunk_y, main_biome, neighbor_biomes)
        elif main_biome == "BEACH":
            # 海滩生物群系：生成沙滩和少量水域
            chunk_data = self._generate_beach_chunk(chunk_x, chunk_y, neighbor_biomes)
        elif main_biome == "DESERT":
            # 沙漠生物群系：生成沙漠地形
            chunk_data = self._generate_desert_chunk(chunk_x, chunk_y, neighbor_biomes)
        elif main_biome == "SNOW":
            # 雪地生物群系：生成雪地地形
            chunk_data = self._generate_snow_chunk(chunk_x, chunk_y, neighbor_biomes)
        elif main_biome == "MOUNTAIN":
            # 山地生物群系：生成山地地形
            chunk_data = self._generate_mountain_chunk(chunk_x, chunk_y, neighbor_biomes)
        elif main_biome == "FOREST":
            # 森林生物群系：生成森林地形
            chunk_data = self._generate_forest_chunk(chunk_x, chunk_y, neighbor_biomes)
        else:  # GRASSLAND
            # 草原生物群系：生成草地地形
            chunk_data = self._generate_grassland_chunk(chunk_x, chunk_y, neighbor_biomes)
        
        return chunk_data
    
    def _chunk_to_planet_tile(self, chunk_x, chunk_y):
        """将区块坐标转换为球面瓦片坐标"""
        # 这里使用简单的映射关系，实际项目中可能需要更复杂的映射
        # 假设每个区块对应一个球面瓦片
        tile_x = chunk_x + self.planet.resolution // 2
        tile_y = chunk_y + self.planet.resolution // 2
        
        # 确保坐标在有效范围内
        tile_x = max(0, min(self.planet.resolution - 1, tile_x))
        tile_y = max(0, min(self.planet.resolution - 1, tile_y))
        
        return (tile_x, tile_y)
    
    def _get_planet_biome(self, tile_x, tile_y):
        """获取球面瓦片的生物群系"""
        if 0 <= tile_x < self.planet.resolution and 0 <= tile_y < self.planet.resolution:
            color = self.planet.colors[tile_x, tile_y]
            return self._color_to_biome(color)
        return "GRASSLAND"
    
    def _get_neighbor_biomes(self, tile_x, tile_y):
        """获取邻近瓦片的生物群系"""
        neighbors = {}
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = tile_x + dx, tile_y + dy
            biome = self._get_planet_biome(nx, ny)
            neighbors[(dx, dy)] = biome
        
        return neighbors
    
    def _color_to_biome(self, color):
        """将颜色转换为生物群系名称"""
        for biome, biome_color in BIOME_COLORS.items():
            if np.array_equal(color, biome_color):
                return biome
        return "GRASSLAND"
    
    def _get_continuous_noise(self, global_x, global_y, scale, octaves=2, seed_offset=0):
        """获取连续的噪声值，确保区块间的一致性"""
        return noise.pnoise2(global_x * scale, global_y * scale, 
                           octaves=octaves, base=self.global_seed + seed_offset)
    
    def _generate_ocean_chunk(self, chunk_x, chunk_y, main_biome, neighbor_biomes):
        """生成海洋区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查是否有陆地邻居，如果有则减少水域比例
        has_land_neighbor = any(biome in ["GRASSLAND", "FOREST", "DESERT", "SNOW", "MOUNTAIN"] for biome in neighbor_biomes.values())
        
        # 海洋区块主要是水域，但会有一些岛屿
        if main_biome == "DEEP_OCEAN":
            water_ratio = 0.95 if not has_land_neighbor else 0.85
        else:  # OCEAN
            water_ratio = 0.9 if not has_land_neighbor else 0.75
        
        # 使用噪声生成水域分布
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                # 计算全局坐标用于噪声
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                # 使用多层噪声，确保连续性
                noise_val = 0
                noise_val += self._get_continuous_noise(global_x, global_y, 0.01, 4, 0) * 0.5
                noise_val += self._get_continuous_noise(global_x, global_y, 0.05, 2, 1000) * 0.3
                noise_val += self._get_continuous_noise(global_x, global_y, 0.1, 1, 2000) * 0.2
                
                # 根据噪声值决定地形类型
                if noise_val < water_ratio - 0.4:
                    chunk[x, y] = 0  # WATER
                elif noise_val < water_ratio - 0.1:
                    chunk[x, y] = 2  # SAND (小岛边缘)
                elif noise_val < water_ratio:
                    chunk[x, y] = 1  # GRASS (小岛)
                else:
                    chunk[x, y] = 1  # GRASS (大岛)
        
        return chunk
    
    def _generate_beach_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成海滩区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.02, 3, 3000)
                
                if noise_val < 0.2:
                    chunk[x, y] = 0  # WATER
                elif noise_val < 0.4:
                    chunk[x, y] = 2  # SAND
                else:
                    chunk[x, y] = 1  # GRASS
        
        return chunk
    
    def _generate_desert_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成沙漠区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查邻近生物群系
        has_ocean_neighbor = any(biome in ["OCEAN", "DEEP_OCEAN"] for biome in neighbor_biomes.values())
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.03, 2, 4000)
                
                # 根据是否有海洋邻居调整水域比例
                water_threshold = 0.01 if has_ocean_neighbor else 0.005
                
                if noise_val < water_threshold:
                    chunk[x, y] = 0  # WATER (绿洲)
                elif noise_val < 0.85:
                    chunk[x, y] = 6  # DESERT
                else:
                    chunk[x, y] = 3  # ROCK (岩石)
        
        return chunk
    
    def _generate_snow_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成雪地区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查邻近生物群系
        has_ocean_neighbor = any(biome in ["OCEAN", "DEEP_OCEAN"] for biome in neighbor_biomes.values())
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.025, 3, 5000)
                
                # 根据是否有海洋邻居调整水域比例
                water_threshold = 0.01 if has_ocean_neighbor else 0.005
                
                if noise_val < water_threshold:
                    chunk[x, y] = 0  # WATER (冰湖)
                elif noise_val < 0.8:
                    chunk[x, y] = 4  # SNOW
                else:
                    chunk[x, y] = 3  # ROCK
        
        return chunk
    
    def _generate_mountain_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成山地区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查邻近生物群系
        has_ocean_neighbor = any(biome in ["OCEAN", "DEEP_OCEAN"] for biome in neighbor_biomes.values())
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.02, 4, 6000)
                
                # 根据是否有海洋邻居调整水域比例
                water_threshold = 0.01 if has_ocean_neighbor else 0.005
                
                if noise_val < water_threshold:
                    chunk[x, y] = 0  # WATER (山间湖泊)
                elif noise_val < 0.4:
                    chunk[x, y] = 1  # GRASS (山脚)
                else:
                    chunk[x, y] = 3  # ROCK (山峰)
        
        return chunk
    
    def _generate_forest_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成森林区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查邻近生物群系
        has_ocean_neighbor = any(biome in ["OCEAN", "DEEP_OCEAN"] for biome in neighbor_biomes.values())
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.03, 2, 7000)
                
                # 根据是否有海洋邻居调整水域比例
                water_threshold = 0.01 if has_ocean_neighbor else 0.005
                
                if noise_val < water_threshold:
                    chunk[x, y] = 0  # WATER (小溪)
                elif noise_val < 0.75:
                    chunk[x, y] = 5  # FOREST
                else:
                    chunk[x, y] = 1  # GRASS (林间空地)
        
        return chunk
    
    def _generate_grassland_chunk(self, chunk_x, chunk_y, neighbor_biomes):
        """生成草原区块"""
        chunk = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=int)
        
        # 检查邻近生物群系，如果是海洋则增加水域
        has_ocean_neighbor = any(biome in ["OCEAN", "DEEP_OCEAN"] for biome in neighbor_biomes.values())
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                global_x = chunk_x * CHUNK_SIZE + x
                global_y = chunk_y * CHUNK_SIZE + y
                
                noise_val = self._get_continuous_noise(global_x, global_y, 0.025, 2, 8000)
                
                # 根据是否有海洋邻居调整水域比例
                water_threshold = 0.005 if has_ocean_neighbor else 0.002
                
                if noise_val < water_threshold:
                    chunk[x, y] = 0  # WATER (小池塘)
                elif noise_val < 0.85:
                    chunk[x, y] = 1  # GRASS
                else:
                    chunk[x, y] = 5  # FOREST (小片森林)
        
        return chunk
