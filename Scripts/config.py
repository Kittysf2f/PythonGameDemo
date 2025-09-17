import random

# 窗口设置
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
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

# 场景管理设置
SCENE_A = "scene_a"  # 球面地图场景
SCENE_B = "scene_b"  # 2D地图场景

# UI设置
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_X = SCREEN_WIDTH - BUTTON_WIDTH - 20
BUTTON_Y = 20
BUTTON_BASE_COLOR = (50, 150, 50)
BUTTON_HOVER_COLOR = (70, 170, 70)
BUTTON_PRESSED_COLOR = (30, 130, 30)
BUTTON_DISABLED_COLOR = (100, 100, 100)

# 2D地图设置
CHUNK_SIZE = 256  # 每个区块包含256x256个瓦片
TILE_SIZE = 16    # 每个瓦片的像素大小
CHUNK_PIXEL_SIZE = CHUNK_SIZE * TILE_SIZE

# 2D地图瓦片类型
TILE_TYPES = {
    "WATER": (0, 100, 200),
    "GRASS": (50, 150, 50),
    "SAND": (200, 180, 100),
    "ROCK": (120, 120, 120),
    "SNOW": (240, 240, 240),
    "FOREST": (30, 100, 30),
    "DESERT": (200, 160, 80),
}

# 摄像机设置
CAMERA_SPEED = 5.0
# 缩放设置：基于屏幕空间瓦片数量
INITIAL_TILES_ON_SCREEN = 100  # 初始显示100x100个瓦片
MIN_TILES_ON_SCREEN = 50       # 最小显示50x50个瓦片
MAX_TILES_ON_SCREEN = 150      # 最大显示150x150个瓦片
ZOOM_SPEED = 0.1

# 区块加载设置
LOAD_RADIUS = 2  # 加载半径：当前区块周围2个区块范围内的区块都会被加载

# 调试设置
SHOW_CHUNK_BORDERS = True  # 是否显示区块边界（红色实线）