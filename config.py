# config.py
MODEL = "gemma3:4b"
PORT = 5000

SPHERE_RADIUS = 1500
TOUCH_DISTANCE = 200

HUNGER_INCREASE = 1
ENERGY_DECREASE = 1
HUNGER_MAX = 100
ENERGY_MIN = 0

CAMPFIRE_HUNGER_RESTORE = 30

MEMORY_MAX_SIZE = 10
MEMORY_CONTEXT_SIZE = 3

WAIT_TIME_MIN = 8
WAIT_TIME_MAX = 20
WAIT_TIME_DEFAULT = 10

DIRECTIONS_TO_OFFSET = {
    "north":     (2000, 0),
    "south":     (-2000, 0),
    "east":      (0, 2000),
    "west":      (0, -2000),
    "northeast": (2000, 2000),
    "northwest": (2000, -2000),
    "southeast": (-2000, 2000),
    "southwest": (-2000, -2000),
    "stay":      (0, 0)
}