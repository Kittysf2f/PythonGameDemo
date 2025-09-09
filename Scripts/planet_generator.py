import numpy as np
import noise
import math
from config import *

class PlanetGenerator:
    def __init__(self, resolution, seed):
        self.resolution = resolution
        self.seed = seed
        self.points = np.zeros((resolution, resolution, 3))
        self.colors = np.zeros((resolution, resolution, 3))

    def generate(self):
        print(f"Generating planet with seed: {self.seed}...")
        lat_step = np.pi / (self.resolution - 1)
        lon_step = 2 * np.pi / (self.resolution - 1)
        lats = np.arange(-np.pi / 2, np.pi / 2 + lat_step, lat_step)
        lons = np.arange(-np.pi, np.pi + lon_step, lon_step)

        for i in range(self.resolution):
            for j in range(self.resolution):
                lat, lon = lats[i], lons[j]
                x = math.cos(lat) * math.cos(lon)
                y = math.cos(lat) * math.sin(lon)
                z = math.sin(lat)
                self.points[i, j] = [x, y, z]
        self._generate_biomes()
        print("Planet generation complete.")

    def _get_noise_value(self, x, y, z, custom_seed):
        return noise.pnoise3(x * SCALE, y * SCALE, z * SCALE,
                             octaves=OCTAVES, persistence=PERSISTENCE,
                             lacunarity=LACUNARITY, base=self.seed + custom_seed)

    def _generate_biomes(self):
        for i in range(self.resolution):
            for j in range(self.resolution):
                x, y, z = self.points[i, j]
                elevation = (self._get_noise_value(x, y, z, 0) + 1) / 2
                base_temp = 1.0 - (i / (self.resolution -1) - 0.5)**2 * 2
                temp_noise = (self._get_noise_value(x, y, z, 1) + 1) / 2
                temperature = base_temp * 0.7 + temp_noise * 0.3
                humidity = (self._get_noise_value(x, y, z, 2) + 1) / 2
                biome = self._determine_biome(elevation, temperature, humidity)
                self.colors[i, j] = BIOME_COLORS[biome]

    def _determine_biome(self, e, t, h):
        if e < 0.3: return "DEEP_OCEAN"
        if e < 0.5: return "OCEAN"
        if e < 0.53: return "BEACH"
        if e > 0.8: return "MOUNTAIN"
        if t < 0.2: return "SNOW"
        if h < 0.3 and t > 0.6: return "DESERT"
        if h > 0.6 and t > 0.4: return "FOREST"
        return "GRASSLAND"