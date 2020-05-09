import os
import time
import digitalio
import board
from PIL import Image, ImageOps

# pylint: enable=too-few-public-methods
class Video:
    def __init__(self, display, width=None, height=None, file_path=None):
        self._frame_count = 0
        self.__num_loop = 0
        self._duration = 0
        self._frames = []


        if width is not None:
            self._width = width
        else:
            self._width = display.width
        if height is not None:
            self._height = height
        else:
            self._height = display.height
        if file_path is not None:
            self._file_path = file_path
        else:
            raise Exception("Need file path of video to be passed in")
        
        self._display = display
        self.preload()
 
    def preload(self):
        image = Image.open(self._file_path)
        print("Loading {}...".format(self._file_path))
        if "duration" in image.info:
            self._duration = image.info["duration"]
        else:
            self._duration = 0
        if "loop" in image.info:
            self._loop = image.info["loop"]
        else:
            self._loop = 1
        self._frame_count = image.n_frames
        self._frames.clear()
        for frame in range(self._frame_count):
            image.seek(frame)
            # Create blank image for drawing.
            # Make sure to create image with mode 'RGB' for full color.
            frame_object = Frame(duration=self._duration)
            if "duration" in image.info:
                frame_object.duration = image.info["duration"]
            frame_object.image = ImageOps.pad(  # pylint: disable=no-member
                image.convert("RGB"),
                (self._width, self._height),
                method=Image.NEAREST,
                color=(0, 0, 0),
                centering=(0.5, 0.5),
            )
            self._frames.append(frame_object)
 
    def play(self):
        for frame_object in self._frames:
            start_time = time.monotonic()
            self._display.image(frame_object.image)
            while time.monotonic() < (start_time + frame_object.duration / 1000):
                pass
 
    def run(self):
        while True:
            self.play()

# pylint: disable=too-few-public-methods
class Frame:
    def __init__(self, duration=0):
        self.duration = duration
        self.image = None
 
 