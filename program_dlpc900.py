import argparse
parser = argparse.ArgumentParser(description="Programs a sequence of images through Texas Instruments' DLPLCRC900EVM evaluation module for DLP displays")
parser.add_argument("-i", "--images", nargs='+', help="Input images", required=True)
parser.add_argument("--fps", type=int, default=3)
parser.add_argument("--avg", action='store_true')
parser.add_argument("--sum", action='store_true')
parser.add_argument("--dilation", type=int)
args = parser.parse_args()


import pycrafter6500
import numpy
from PIL import Image, ImageChops, ImageOps, ImageFilter

Image.MAX_IMAGE_PIXELS = None

def as_binary_np_array(image):
    return numpy.asarray(image.convert('L'))//129

dlp_resolution=(1920,1080)

# Load input images
images=[ImageOps.pad(Image.open(path), size=dlp_resolution, color='black', centering=(0.5, 0.5)) for path in args.images]
if args.dilation:
    images=[image.filter(ImageFilter.MaxFilter(args.dilation)) for image in images]
images=[as_binary_np_array(image) for image in images]
if args.avg:
    images=[sum(images)]+[0*images[0] for _ in range(len(images)-1)]
if args.sum:
    images=[sum(images)]

# Program the display controller
dlp=pycrafter6500.dmd()
dlp.stopsequence()
dlp.changemode(3)

exposure=[1000000//args.fps]*30
dark_time=[0]*30
trigger_in=[False]*30
trigger_out=[1]*30

dlp.defsequence(images,exposure,trigger_in,dark_time,trigger_out,0)

dlp.startsequence()
