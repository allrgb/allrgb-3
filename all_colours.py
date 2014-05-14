import numpy
from PIL import Image
import math
import random
import time
from color import Color
from canvas import Canvas
from colorset import Colorset
import sys

bits = 4
seed = 42
starting_pixels = 5
random.seed(seed)
print 'making colors'
colorset = Colorset(bits)

print 'initializing'
height = width = int(math.sqrt(colorset.size()))
print ('dims', height * width, colorset.size())
canvas = Canvas(width, height)

colors = [x for x in colorset.iterate()]
random.shuffle(colors)

for i in xrange(starting_pixels):
    starting_color = colorset.get_nearest(colors[i])
    last_x = random.randrange(width)
    last_y = random.randrange(height)
    canvas.set(last_x, last_y, starting_color)

i = 0
start_time = time.time()
last_save_time = time.time()
time_color = 0.0
time_point = 0.0

def write_image(i, last_save_time):
    name = '/tmp/colors-nextrand.%d.%d.png' % (bits, i)
    avg_rate = i / (time.time() - start_time)
    print (name, time.time() - last_save_time, int(avg_rate), int(time_color), int(time_point))
    last_save_time = time.time()
    canvas.save(name)

for color in colorset.iterate():
    (x, y) = canvas.find_pixel_with_average_near(color)
    canvas.set(x, y, color)
    if i % 1000 == 0:
        write_image(i, last_save_time)
    i += 1

write_image(i, last_save_time)
sys.exit()

while colorset.size() > 0:
    get_nearby_start = time.time()
    (x, y) = canvas.find_blank_nearby_opt(last_x, last_y)
    diff = time.time() - get_nearby_start
    time_point += diff

    avg_col = canvas.get_avg_color(x, y)
    get_nearest_start = time.time()
    new_col = colorset.get_nearest(avg_col)
    diff = time.time() - get_nearest_start
    time_color += diff

    canvas.set(x, y, new_col)
    last_x = x
    last_y = y
    i = i + 1

    if i % 1000 == 0:
        write_image(i, last_save_time)

write_image(i, last_save_time)
