from PIL import Image
from subprocess import call
import shutil
import sys
import os

brickh = 30
brickw = 30
brick = "brick.png"

cmdargs = list(sys.argv)

if len(cmdargs) < 2:
    print('No input file specified, please use the command "python legoGif.py gifname.gif" to create a legofied version of "gifname.gif". It will automatically be saved as "lego_gifname.gif"')
    sys.exit(0)

filename = cmdargs[1]


# function that iterates over the gif's frames
def iter_frames(imageToIter):
    try:
        i = 0
        while 1:
            imageToIter.seek(i)
            imframe = imageToIter.copy()
            if i == 0:
                palette = imframe.getpalette()
            else:
                imframe.putpalette(palette)
            yield imframe
            i += 1
    except EOFError:
        pass


# small function to apply an effect over an entire image
def applyEffect(image, effect):
    width, height = image.size
    poa = image.load()
    for x in range(width):
        for y in range(height):
            poa[x, y] = effect(poa[x, y])
    return image


def overUnder(value, min=-100, max=100):
    if value > max:
        return max
    elif value < min:
        return min
    else:
        return value

 
# create a lego brick from a single color
def makeLegoBrick(overlayRed, overlayGreen, overlayBlue):
    # colorizing the brick function
    def colorize(blockColors):
        newRed = overUnder(133 - overlayRed)
        newGreen = overUnder(133 - overlayGreen)
        newBlue = overUnder(133 - overlayBlue)
        
        return (blockColors[0] - newRed, blockColors[1] - newGreen, blockColors[2] - newBlue, 255)
    
    return applyEffect(Image.open(brick), colorize)


# create a lego version of an image from an image
def makeLegoImage(baseImage):
    baseWidth, baseHeight = baseImage.size
    basePoa = baseImage.load()

    legoImage = Image.new("RGB", (baseWidth * brickw, baseHeight * brickh), "white")

    for x in range(baseWidth):
        for y in range(baseHeight):
            bp = basePoa[x, y]
            isinstance(bp, (int, long))
            legoImage.paste(makeLegoBrick(bp[0], bp[1], bp[2]), (x * brickw, y * brickh, (x + 1) * brickw, (y + 1) * brickh))
    return legoImage

# check if image is animated
def is_animated(im):
    try:
        im.seek(1)
        return True
    except EOFError:
        return False


# open gif to start splitting
baseImage = Image.open(filename)
newSize = baseImage.size
static = filename.lower().endswith(".gif") and is_animated(baseImage)

# scale image
scale = 1

if newSize[0] > 30 or newSize[1] > 30:
    if newSize[0] < newSize[1]:
        scale = newSize[1] / 30
    else:
        scale = newSize[0] / 30
    
    newSize = (int(round(newSize[0] / scale)), int(round(newSize[1] / scale)))

if(static):
    print("Animated gif detected, will now legofy each frame and recreate the gif and save as lego_{}".format(filename))
    # check if dir exists, if not, make it
    if not os.path.exists("./tmp_frames/"):
        os.makedirs("./tmp_frames/")

    # for each frame in the gif, save it
    for i, frame in enumerate(iter_frames(baseImage)):
        frame.save('./tmp_frames/frame_{}.png'.format(("0" * (4 - len(str(i)))) + str(i)), **frame.info)

    # make lego images from gif
    for file in os.listdir("./tmp_frames"):
        if file.endswith(".png"):
            print("Working on {}".format(file))
            im = Image.open("./tmp_frames/{}".format(file)).convert("RGBA")
            if scale != 1:
                im.thumbnail(newSize, Image.ANTIALIAS)
            makeLegoImage(im).save("./tmp_frames/{}".format(file))

    # make new gif "convert -delay 10 -loop 0 *.png animation.gif"
    delay = str(baseImage.info["duration"] / 10)
    
    command = "convert -delay {} -loop 0 ./tmp_frames/*.png lego_{}".format(delay, filename)

    print(command)
    call(command.split(" "))
    print("Creating gif with filename\"lego_{}\"".format(filename))
    shutil.rmtree('./tmp_frames')
else:
    print("Static image detected, will now legofy and save as lego_{}".format(filename))
    if scale != 1:
        im.thumbnail(newSize, Image.ANTIALIAS)
    makeLegoImage(baseImage).save("lego_{}".format(filename))

print("Finished!")
