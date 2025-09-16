import random

# 窗口设置
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
ROTATION_SPEED = 0.01

# 行星生成设置
RESOLUTION = 150
SEED = random.randint(0, 1000)
SCALE = 2.0
OCTAVES = 6
PERSISTENCE = 0.5
LACUNARITY = 2.0

# 生物群系颜色定义
BIOME_COLORS = {
    "DEEP_OCEAN": (5, 22, 64),
    "OCEAN": (22, 80, 158),
    "BEACH": (230, 214, 153),
    "GRASSLAND": (88, 161, 48),
    "FOREST": (38, 112, 21),
    "DESERT": (219, 186, 112),
    "SNOW": (240, 240, 240),
    "MOUNTAIN": (110, 110, 110),
}

# 生物群系英文名称
BIOME_NAMES = {
    "DEEP_OCEAN": "Deep Ocean",
    "OCEAN": "Ocean",
    "BEACH": "Beach",
    "GRASSLAND": "Grassland",
    "FOREST": "Forest",
    "DESERT": "Desert",
    "SNOW": "Snow",
    "MOUNTAIN": "Mountain",
}