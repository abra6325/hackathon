from .. import YikObject
from ..dimensions import Dimension
from ..physics.kinematics import KinematicsHolder
from ..render import Renderable
from ..script import ScriptableObject
from ..timing import CanTick, Routine
from ..physics.position import DimensionHolder

class RenderableGameObject(Renderable, CanTick, ScriptableObject, DimensionHolder):

    def __init__(self, parent, screen_position: Dimension = Dimension(0, 0), size: Dimension = Dimension(0, 0), routine_include=False, *args, **kwargs):
        """

        :param parent: The parent of this object
        :param update: A callable function for this object's routine target. Set to None if this object does not tick.
        """
        YikObject.__init__(self, parent, *args, **kwargs)
        CanTick.__init__(self, parent, primary_initialization=False, routine_include=routine_include)
        Renderable.__init__(self, parent, screen_position=screen_position, size=size, primary_initialization=False)
        ScriptableObject.__init__(self, parent, primary_initialization=False)
        DimensionHolder.__init__(self, parent, position=screen_position, primary_initialization=False)

    def __pn_routine_update__(self, routine: Routine = None):
        pass





