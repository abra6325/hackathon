from .crane import Crane2
from .socket import DedicatedServer, DedicatedServerV2

from .gameobject.gameobject import *
from .interface import PyNamical
from .events import EventType, Executable, change_debug_attacher
from .debugger import Debugger
from .logger import Logger
import threading
import time
import traceback


class Event:
    def __init__(self, func, typeC=None, condition=None, ):
        self.func = func
        self.type = typeC
        self.condition = condition

    def type_down(self) -> str:
        # theType = self.type
        # if theType == EventType.KEYPRESSED:
        #     return keyboard.read_key()
        pass

    def type_bool_down(self) -> bool:
        # theKey = self.type
        # if theKey == EventType.APRESSED:
        #     return keyboard.is_pressed("a")
        pass



class GameManager(PyNamical):
    def __init__(self,
                 dimensions: Dimension,
                 tps: int = 128,
                 fps: int = 0,
                 event_tracker: bool = False):
        super().__init__(None, no_parent=True)
        self.dimensions = dimensions
        self.width = dimensions.x
        self.height = dimensions.y
        self.object_count = 0
        self.objects = set()
        self.updates = []
        self.listeners = []
        self.tpu = 1
        self.ticks = 0
        self.tpl = 1
        self.tps = tps
        self._epoch_tps = 1 / self.tps
        self.listenthread = threading.Thread(target=self.listen)
        self.framethread = threading.Thread(target=self.frame)
        self.event_track = event_tracker
        if fps == 0:
            self.fps = 0
            self._epoch_fps = 0.001
        else:
            self.fps = fps
            self._epoch_fps = 1 / self.fps
        self.updatethread = threading.Thread(target=self.update)
        self.terminated = False
        self.f = 0
        self.t = 0
        self.uptick = 0
        self.parent = None
        self.children = []
        self.starttime = 0
        self.ghosts = []
        self.pressed = {}

        self.mouse = Dimension(-1, -1)
        self.client = None

        self.debug = None

        self._timedifferencetick = time.time()
        self.deltatime = 0

        self._fpstime = time.time()
        self.fps_deltatime = 0

        self.ticksteplisteners = 1

        self.displayorder = []

        PyNamical.MAIN_GAMEMANAGER = self


    def set_as_main_manager(self):
        PyNamical.MAIN_GAMEMANAGER = self


    def _key(self, e):
        if e.keysym == "quoteleft":


            if self.debug == None:
                Logger.print("Debugger not found! Creating window instance", channel=5)
                #self.debug = Debugger(self, enable_event_listener=self.event_track)
                self.debug = Debugger(self, True, True)

                change_debug_attacher(self.debug._call_callevent)


            self.debug.run()

        eventCode = int(e.type)
        if eventCode == 2:
            # KeyPress
            self.pressed[e.keysym] = True
            self.call_event_listeners(EventType.KEYDOWN, str(e.keysym), key=str(e.keysym))
        elif eventCode == 3:  # KeyUp
            self.pressed[e.keysym] = False
            self.call_event_listeners(EventType.KEYUP, str(e.keysym), key=str(e.keysym))
        pass

    def start(self, alternative_listener=None):
        # if alternative_listener is not None:
        #     Logger.print(f"{alternative_listener} is now responsible of ", channel=3)
        if self.client is not None:
            Logger.print(f"{self.client} is responsible of sending and recieving game data!", channel=2)
            # self.client.listen()

        self.updatethread.start()
        self.listenthread.start()

        try:
            self.window
        except AttributeError:
            err = RuntimeError(
                "No ViewPort Object found for this specific GameManager instance. Create a viewport by using pynamics.ProjectWindow.")
            raise err

        self.starttime = time.time()

        self.call_event_listeners(EventType.STARTUP)

        if isinstance(self.window, (DedicatedServer, DedicatedServerV2)):
            Logger.print("Using DedicatedServer as display port!", channel=2)
            self.window.listen()
        else:
            self.window._tk.after(100, self.frame)
            self.window._tk.bind("<KeyPress>", self._key)
            self.window._tk.bind("<KeyRelease>", self._key)
            self.window._tk.bind("<Motion>", self._mouse)
            self.window._tk.bind("<Button-1>", lambda i: self._click(i, 0))
            self.window._tk.bind("<Button-2>", lambda i: self._click(i, 1))
            self.window._tk.bind("<Button-3>", lambda i: self._click(i, 2))
            self.window.start()

    def _click(self, event, click_type):
        if click_type == 0:
            
            
            self.call_event_listeners(EventType.KEYDOWN, key="mousebutton1")

            for i in self.objects:
                if i.position.x <= event.x <= i.position.x + i.size.x and i.position.y <= event.y <= i.position.y + i.size.y:

                    i.call_event_listeners(EventType.ONCLICK)

        if click_type == 1:
            self.call_event_listeners(EventType.KEYDOWN, key="mousebutton2")

        if click_type == 2:
            self.call_event_listeners(EventType.KEYDOWN, key="mousebutton3")
    def after(self, duration=0):

        def inner(func):
            self.window._tk

    def _mouse(self, event):
        x, y = event.x, event.y
        self.mouse.x = x
        self.mouse.y = y

    def update(self):

        while True:

            if self.terminated: break

            while self.debug != None and self.debug.tickchanger_paused:
                time.sleep(0.01)
                if self.debug.tickchanger_stepping > 0:
                    self.debug.tickchanger_stepping -= 1
                    break
                continue


            


            self.deltatime = time.time() - self._timedifferencetick
            self._timedifferencetick = time.time()

            self.check_mouse_events()

            self.call_event_listeners(EventType.TICK)
            self.call_event_listeners(EventType.THREAD)

            for i in self.pressed:
                if self.pressed[i]:
                    
                    self.call_event_listeners(EventType.KEYHOLD, i, key=i)

            self.pressed["quoteleft"] = False

            self.ticks += 1
            self.t += 1

            for i in self.updates:
                print(i)
                i()

            self.window.update()
            
            # TODO: Fix Deltatime since time.sleep yeilds more delay than specificed
            # x = self.deltatime - self._epoch_tps
            # k = self._epoch_tps - x - 0.0005
            # if k < 0: k = self._epoch_tps
            # print(k)
            time.sleep(self._epoch_tps)
            # time.sleep(0.0001)
            # time.sleep(random.randint(0, 100) / 1000)

    # Checks if the mouse is hovering or clicking anything.
    def check_mouse_events(self):
        for i in self.objects:
            if isinstance(i, GameObject):
                pass


    def listen(self):
        while True:

            if self.terminated: break

            for i in self.listeners:
                if isinstance(i, Event):
                    if i.condition is not None and i.condition():
                        i.func()
                    elif i.condition is None:
                        if i.type_bool_down():
                            i.func()
            time.sleep(self._epoch_tps)

    def test(self):
        print(1)

    def frame(self, recursion=True):
        self.call_event_listeners(EventType.FRAME)
        #self.f += 1

        self.window.blit()

        if recursion:
            self.window.surface.after(int(self._epoch_fps * 1000), self.frame)

            
            self.fps_deltatime = time.time() - self._fpstime
            self._fpstime = time.time()

    def add_tick_update(self, function):
        self.events[EventType.TICK].append(Executable(function, lambda i: True))

    def set_ticks_per_update(self, tick: int):
        self.tpu = tick

    def set_ticks_per_listener(self, tick: int):
        self.tpl = tick

    def add_object(self, object: GameObject):

        self.objects.add(object)
        #print(self.objects)
        self.displayorder.append(object)
        self.displayorder.sort(key=lambda i: i.zindex) # fix
        if self.debug is not None:
            self.debug.workspace_reload(object)

    def remove_object(self, object: GameObject):
        self.objects.remove(object)
        if self.debug is not None:
            self.debug.workspace_remove(object)

    def set_title(self, str):
        self.window._tk.title(str)

    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        self.window.surface.create_rectangle(x1, y1, x2, y2, **kwargs)

    def delete_draws(self, id):
        self.window.surface.delete(id)

    def attach_update_thread(self, object: PyNamical):
        self.ticksteplisteners += 1

        def update_self():
            while self.terminated == False:

                try:
                    if object.terminated: break
                except:
                    pass

                while self.debug != None and self.debug.tickchanger_paused:
                    time.sleep(0.01)
                    if self.debug.tickchanger_stepping:
                        self.debug.tickchanger_stepping = 0
                        break
                    continue

                try:
                    object.update()
                except Exception as e:
                    print(traceback.format_exc())
                time.sleep(self._epoch_tps)

        threading.Thread(target=update_self).start()
