from typing import Dict, List, ClassVar
from enum import Enum
from dataclasses import dataclass

from performences.goal_locations import (
    GOALS_LOCATIONS_WAREHOUSE,
    GOALS_LOCATIONS_ROOM,
    GOALS_LOCATIONS_MAZE,
    GOALS_LOCATIONS_RANDOM_64,
)


class ConfigType(str, Enum):
    ROOMS_32 = "room_32"
    MAZE_32 = "maze_32"
    WAREHOUSE = "warehouse"
    RANDOM_64 = "random_64"


@dataclass
class BaseConfig:
    NUMBER_OF_GOALS_LIST: ClassVar[List[int]] = [5]
    MAP_NAME: ClassVar[str] = "room-32.map"
    NETWORK_MODES: ClassVar[List[str]] = ["stays", "hot_swapping-2", "disappearing", "hot_swapping-0"]
    NUMBER_OF_RUNS: ClassVar[int] = 10
    GOAL_LOCATIONS: ClassVar[List[str]] = GOALS_LOCATIONS_ROOM
    index: ClassVar[int] = 1


@dataclass
class Rooms32Config(BaseConfig):
    NUMBER_OF_GOALS_LIST: ClassVar[List[int]] = [10, 20, 30, 40, 50]
    MAP_NAME: ClassVar[str] = "room-32.map"
    NETWORK_MODES: ClassVar[List[str]] = ["stays", "hot_swapping-2", "disappearing", "hot_swapping-0"]
    NUMBER_OF_RUNS: ClassVar[int] = 50
    GOAL_LOCATIONS: ClassVar[List[str]] = GOALS_LOCATIONS_ROOM
    index: ClassVar[int] = 1


@dataclass
class Maze32Config(BaseConfig):
    NUMBER_OF_GOALS_LIST: ClassVar[List[int]] = [10, 20, 30, 40, 50]
    MAP_NAME: ClassVar[str] = "maze-32.map"
    NETWORK_MODES: ClassVar[List[str]] = ["stays", "hot_swapping-2", "disappearing", "hot_swapping-0"]
    NUMBER_OF_RUNS: ClassVar[int] = 50
    GOAL_LOCATIONS: ClassVar[List[str]] = GOALS_LOCATIONS_MAZE
    index: ClassVar[int] = 1


@dataclass
class WarehouseConfig(BaseConfig):
    NUMBER_OF_GOALS_LIST: ClassVar[List[int]] = [10, 20, 30, 40, 50]
    MAP_NAME: ClassVar[str] = "warehouse.map"
    NETWORK_MODES: ClassVar[List[str]] = ["stays", "hot_swapping-2", "disappearing", "hot_swapping-0"]
    NUMBER_OF_RUNS: ClassVar[int] = 50
    GOAL_LOCATIONS: ClassVar[List[str]] = GOALS_LOCATIONS_WAREHOUSE
    index: ClassVar[int] = 1


@dataclass
class Random64Config(BaseConfig):
    NUMBER_OF_GOALS_LIST: ClassVar[List[int]] = [5]
    MAP_NAME: ClassVar[str] = "random-64.map"
    NETWORK_MODES: ClassVar[List[str]] = ["stays", "hot_swapping-2", "disappearing", "hot_swapping-0"]
    NUMBER_OF_RUNS: ClassVar[int] = 50
    GOAL_LOCATIONS: ClassVar[List[str]] = GOALS_LOCATIONS_RANDOM_64



CONFIG_TYPES_TO_CONFIGS: Dict[ConfigType, BaseConfig] =  {
    ConfigType.ROOMS_32: Rooms32Config(),
    ConfigType.MAZE_32: Maze32Config(),
    ConfigType.WAREHOUSE: WarehouseConfig(),
    ConfigType.RANDOM_64: Random64Config(),
}


def get_config(config_type: ConfigType) -> BaseConfig:
    return CONFIG_TYPES_TO_CONFIGS.get(
        config_type,
        BaseConfig(),
    )
