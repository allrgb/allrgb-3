import numpy
from PIL import Image
import math
import random
import time
from color import Color
from canvas import Canvas
from colorset import Colorset
import sys

# constants to configure how we're making things!

# how many bits should we use per channel?  "normal" 24-bit color
# uses 8 bits per channel, but will take a very long time to generate
# a full image.  Image size = # colors = 2^(3 * bits)
bits = 4

# How many pixels do we start by randomly filling in?  This is only
# relevant for the "find the best place for a color" approach, rather
# than the "find the best color for a place" approach.
starting_pixels = 3

# This is just a seed for the random number generator so we can do
# things like performance testing deterministically
seed = 27

print 'initializing'

random.seed(seed)
colorset = Colorset(bits)
# This is technically only correct for an even number of bits, but
# it rounds down for an odd number of bits, and there are simply some colors
# that we never use.  Shrug.
height = width = int(math.sqrt(colorset.size()))
canvas = Canvas(width, height)

# Grab some random starting colors just by making a randomly-sorted
# list of all the colors and taking the first few.
# Not the most efficient, but doesn't really matter.
colors = [x for x in colorset.iterate()]
random.shuffle(colors)

# Choose random starting colors and place them randomly on the canvas
last_y = 0
last_x = 0
for i in xrange(width/10):
    starting_color = colorset.get_nearest(colors[i])
    last_x = i * 10 # TODO why not randomize this?
    canvas.set(last_x, last_y, starting_color)

start_time = time.time()
last_save_time = time.time()
time_color = 0.0
time_point = 0.0

class Filler(object):
    def __init__(self, canvas, colorset, starting_pixel_count):
        self.canvas = canvas
        self.colorset = colorset
        self.starting_pixel_count = starting_pixel_count

        self.start_time = time.time()
        self.last_save_time = time.time()

        self.time_color = 0.0
        self.time_point = 0.0

    def write_image(self, i):
        bits = self.colorset.bits
        name = '/tmp/colors-coloriter.%d.%d.%d.png' % (bits, self.starting_pixel_count, i)
        avg_rate = i / (time.time() - self.start_time)
        print (name,
               time.time() - self.last_save_time,
               int(avg_rate),
               int(self.time_color),
               int(self.time_point))
        self.canvas.save(name)
        self.last_save_time = time.time()

class ByColorFiller(Filler):
    def go(self):
        i = 0
        # For each color generated, find the pixel where it fits "best"
        # (i.e. the pixel where the average of the filled-in pixels surrounding it
        # is closest to this color)
        for color in self.colorset.iterate():
            # TODO: just check if canvas is full first?
            point = self.canvas.find_pixel_with_average_near(color)
            if point is None:
                # it is possible we have more colors than pixels (since the canvas
                # is a square, but the number of colors is not a perfect square if
                # bits is odd)
                break
            (x, y) = point
            canvas.set(x, y, color)
            if i % 1000 == 0:
                self.write_image(i)

            i += 1

        self.write_image(i)

class ByWalkFiller(Filler):

    def go(self):
        print colorset
        last_x = 0
        last_y = 0
        i = 0
        print ('last_x after', last_x)
        while colorset.size() > 0:
            get_nearby_start = time.time()

            # find the open pixel nearest the last one we filled in
            (x, y) = canvas.find_blank_nearby_opt(last_x, last_y)
            diff = time.time() - get_nearby_start
            self.time_point += diff

            # figure out what the "average" color is of all the pixels
            # around the open pixel we found
            avg_col = canvas.get_avg_color(x, y)

            # now find the color closest to that average
            get_nearest_start = time.time()
            new_col = colorset.get_nearest(avg_col)
            diff = time.time() - get_nearest_start
            self.time_color += diff

            canvas.set(x, y, new_col)
            last_x = x
            last_y = y

            i += 1

            if i % 1000 == 0:
                self.write_image(i)

        self.write_image(i)

print ('last_x before', last_x)
# filler = ByColorFiller(canvas, colorset, starting_pixels)
filler = ByWalkFiller(canvas, colorset, starting_pixels)
filler.go()

