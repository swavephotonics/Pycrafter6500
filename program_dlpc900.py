import argparse
parser = argparse.ArgumentParser(description="Programs a sequence of images through Texas Instruments' DLPLCRC900EVM evaluation module for DLP displays")
parser.add_argument("-i", "--images", nargs='+', help="Input images", required=True)
parser.add_argument("--fps", type=float, default=3)
parser.add_argument("--avg", action='store_true')
parser.add_argument("--sum", action='store_true')
parser.add_argument("--temporal_dither", action='store_true')
parser.add_argument("--dilation", type=int)
parser.add_argument("--shiftx", type=int, default=0)
parser.add_argument("--shifty", type=int, default=0)
args = parser.parse_args()


import pycrafter6500
import numpy
import itertools
from PIL import Image, ImageChops, ImageOps, ImageFilter

Image.MAX_IMAGE_PIXELS = None

def temporal_dither(image):
    return [(image>i).astype(numpy.dtype('uint8')) for i in range(255)]

dlp_resolution=(1920,1080)

# Load input images
images=[ImageOps.pad(Image.open(path).convert('L'), size=dlp_resolution, color='black', centering=(args.shiftx/dlp_resolution[0], args.shifty/dlp_resolution[1])) for path in args.images]
if args.dilation:
    images=[image.filter(ImageFilter.MaxFilter(args.dilation)) for image in images]
images=[numpy.asarray(image) for image in images]
if args.avg:
    images=[sum(images)]+[0*images[0] for _ in range(len(images)-1)]
if args.sum:
    images=[sum(images)]

if args.temporal_dither:
    images=list(itertools.chain.from_iterable((temporal_dither(image) for image in images)))
    # for image,i in zip(images, itertools.count()):
        # img = Image.fromarray(image, 'RGB')
        # img.save(f'tempdither{i}.png')
else:
    images = [image//129 for image in images]

# Program the display controller
dlp=pycrafter6500.dmd()
dlp.stopsequence()
dlp.changemode(3)

exposure=[int(1000000/args.fps)]*len(images)
dark_time=[0]*len(images)
trigger_in=[False]*len(images)
trigger_out=[1]*len(images)

dlp.defsequence(images,exposure,trigger_in,dark_time,trigger_out,0)

dlp.startsequence()
