import traceback

from PIL import Image as ImageUtils
import numpy as np

from OpenGL.GL import *

from yik import YikObject
from yik.dimensions import Dimension
from yik.gameobject.simple import RenderableGameObject
from yik.logger import Logger

IMAGETEXTURE_TEXTURE_CACHE = {}
IMAGETEXTURE_PIL_CACHE = {}
IMAGETEXTURE_LOADED = {}
IMAGETEXTURE_GL_IMAGEBIND = {}
IMAGETEXTURE_LIST = []

class ImageTexture:

    def __init__(self, path, crop_resize=True, crop=None):
        self.path = path

        self.crop_resize = crop_resize
        self.gl_bind_id = None


        if not self.path in IMAGETEXTURE_TEXTURE_CACHE:

            self.texture = ImageUtils.open(path)
            # self.texture = self.texture.transpose(ImageUtils.FLIP_TOP_BOTTOM)

            self.texture = self.texture.convert("RGBA")
            self.data = self.texture.tobytes()

            IMAGETEXTURE_TEXTURE_CACHE[self.path] = self.data
            IMAGETEXTURE_PIL_CACHE[self.path] = self.texture
            IMAGETEXTURE_LOADED[self.path] = False
        else:
            self.texture = IMAGETEXTURE_PIL_CACHE[self.path]
            self.data = IMAGETEXTURE_TEXTURE_CACHE[self.path]

        self.size = self.texture.size
        self.width = self.texture.width
        self.height = self.texture.height
        if crop is None:
            self.effective = (0, 0, self.width, self.height)
        else:
            self.effective = crop

    @property
    def loaded(self):
        return IMAGETEXTURE_LOADED[self.path]

    @loaded.setter
    def loaded(self, value):
        IMAGETEXTURE_LOADED[self.path] = value

    def load(self):

        if self.loaded:
            Logger.print(f"{self}: Texture already loaded to GL Cache", channel=5)
            return

        try:
            id = glGenTextures(1)
        except Exception as e:
            Logger.warn(f"{self}: GL Texture cannot be loaded before GL runtime! Manually use {self.__class__.__name__}.load() after runtime or add event Event.Initialization.PostLoadEvent. \n{traceback.format_exc()}")

        self.gl_bind_id = id

        IMAGETEXTURE_GL_IMAGEBIND[self.path] = id



        glBindTexture(GL_TEXTURE_2D, id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE,
        #              None)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                     self.data)
        glBindTexture(GL_TEXTURE_2D, 0)

        self.loaded = True

        Logger.print(f"Loaded texture: {self.path} ({len(self.data)} bytes) [ID={id}]", channel=5)

    def resize(self, size, resample=None):
        pass

    def crop(self, a, b, x, y, crop_resize=None):
        if crop_resize is None:
            crop_resize = self.crop_resize
        self.effective = (a, b, x, y)
        self.crop_resize = crop_resize

    def color_content(self, x, y):
        x = min(x, self.texture.width - 1)
        y = min(y, self.texture.height - 1)
        return self.texture.getpixel((x, y))


class Image(RenderableGameObject):

    def __init__(self, parent: YikObject, x: float = 0, y: float = 0, width: float = -1, height: float = -1,
                 path: str = None,
                 ratio: int = 1,
                 texture: ImageTexture = None,
                 crop_resize: bool = False,
                 *args,
                 **kwargs):

        if texture is None:
            self.image = ImageTexture(path, crop_resize=crop_resize)
        else:
            self.image = texture


        YikObject.__init__(self, parent)
        RenderableGameObject.__init__(self, parent, screen_position=Dimension(x, y), size=Dimension(self.image.size[0], self.image.size[1]), *args, **kwargs)

        w = self.image.width
        h = self.image.height

        if width != -1:
            w = width
        if height != -1:
            h = height

        self.image.resize((int(w * ratio), int(h * ratio)), resample=ImageUtils.BOX)

        self.size.x = int(w * ratio)
        self.size.y = int(h * ratio)

    @property
    def photosize(self):
        return self.size

    def __pn_render__(self):
        glBindTexture(GL_TEXTURE_2D, self.image.gl_bind_id)
        glBegin(GL_QUADS)

        if self.image.crop_resize:
            deltax = self.size.x
            deltay = self.size.y
        else:
            deltax = self.image.effective[2] - self.image.effective[0]
            deltay = self.image.effective[3] - self.image.effective[1]

        # deltax *= self.scale
        # deltay *= self.scale

        # print(i.photosize, deltax, deltay)

        posx = self.x * 1 #self.scale
        posy = self.y * 1 #self.scale

        glTexCoord2f((self.image.effective[0] / self.photosize.x), (self.image.effective[1] / self.photosize.y))
        glVertex2f(posx, posy)
        glTexCoord2f((self.image.effective[2] / self.photosize.x), (self.image.effective[1] / self.photosize.y))
        glVertex2f(posx + deltax, posy)
        glTexCoord2f((self.image.effective[2] / self.photosize.x), (self.image.effective[3] / self.photosize.y))
        glVertex2f(posx + deltax, posy + deltay)
        glTexCoord2f((self.image.effective[0] / self.photosize.x), (self.image.effective[3] / self.photosize.y))
        glVertex2f(posx, posy + deltay)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    def __repr__(self):
        return f"Image(file={self.image.path})"