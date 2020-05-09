import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_rgb_display.ili9341 as ili9341
from video import Video


class Display:
    
    FONT_SIZE = 24
    TEXT_COLOR = "#FFFFFF"
    
    def __init__(self):
        
        # Configuration for CS and DC pins (these are PiTFT defaults):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)

        # Config for display baudrate (default max is 24mhz):
        BAUDRATE = 24000000

        # Setup SPI bus using hardware SPI:
        spi = board.SPI()
        self.disp = ili9341.ILI9341(
            spi,
            rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
        )
        # pylint: enable=line-too-long
        
        # Current location on display
        self.currentX = 0
        self.currentY = -2

        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.
        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width  # we swap height/width to rotate it to landscape!
            self.width = self.disp.height
        else:
            self.width = self.disp.width  # we swap height/width to rotate it to landscape!
            self.height = self.disp.height

        self.image = Image.new("RGB", (self.width, self.height))
         
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
         
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        self.disp.image(self.image)
    
    def println(self, text=None, color=None, font_size=None, x=None):
        if color == None:
            color = self.TEXT_COLOR
        if font_size == None:
            font_size = self.FONT_SIZE
        if x == None:
            x = self.currentX
        if text == None:
            self.currentX = 0
            self.currentY += (font_size)
            return
        # Load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        self.draw.text((x, self.currentY), text, font=font, fill=color)
        self.drawImage()
        self.currentX = 0
        self.currentY += (font.getsize(text)[1] + 1)
        
    def print(self, text="", color=None, font_size=None, x=None):
        if color == None:
            color = self.TEXT_COLOR
        if font_size == None:
            font_size = self.FONT_SIZE
        if x == None:
            x = self.currentX
        # Load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        self.draw.text((x, self.currentY), text, font=font, fill=color)
        self.drawImage()
        self.currentX += font.getsize(text)[0]
        
    def displayImage(self, image_name, x=None, y=None, width=None, height=None):
        if x == None:
            x = self.currentX
        if y == None:
            y = self.currentY
        if width == None:
            width = self.width
        if height == None:
            height = self.height
        
        image = Image.open(image_name)
         
        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
         
        # Crop and center the image
        xCrop = scaled_width // 2 - width // 2
        yCrop = scaled_height // 2 - height // 2
        image = image.crop((xCrop, yCrop, xCrop + width, yCrop + height))
        
        # Switched x and y because of rotated screen
        self.disp.image(image, x=y, y=self.width-x-width)
        
    def displayVideo(self, file_path, width=None, height=None):
        if width == None:
            width = self.width
        if height == None:
            height = self.height
        video = Video(self.disp, width, height, file_path)
        video.run()
        
    def clear(self, x=0, y=0, width=None, height=None):
        if width == None:
            width = self.width
        if height == None:
            height = self.height
        self.currentX = 0
        self.currentY = -2
        # Draw a black filled box to clear the image.
        self.draw.rectangle((x, y, width, height), outline=0, fill=0)
        self.drawImage()
        
    def clearln(self, y=None, height=None):
        if y == None:
            y = self.currentY
        if height == None:
            height = self.FONT_SIZE
        self.currentX = 0
        self.draw.rectangle((0, y, self.width, height), outline=0, fill=0)
        self.drawImage()
        
 
    def drawImage(self):
        self.disp.image(self.image)
