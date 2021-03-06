# common
from buttleofx.core.params import Param
# undo redo
from buttleofx.core.undo_redo.manageTools import CommandManager
from buttleofx.core.undo_redo.commands.params import CmdSetParamInt


class ParamInt(Param):
    """
        Core class, which represents an int parameter.
        Contains :
            - _oldValue : the old value of the param.
            - _hasChanged : to know if the value of the param is changed by the user (at least once).
    """

    def __init__(self, tuttleParam):
        Param.__init__(self, tuttleParam)

        self._oldValue = self.getValue()

        self._hasChanged = False

    #################### getters ####################

    def getParamType(self):
        return "ParamInt"

    def getParamDoc(self):
        return self._tuttleParam.getProperties().getStringProperty("OfxParamPropHint")

    def getDefaultValue(self):
        return self._tuttleParam.getProperties().getIntProperty("OfxParamPropDefault")

    def getOldValue(self):
        return self._oldValue

    def getValue(self):
        return self._tuttleParam.getIntValue()

    def getMinimum(self):
        return self._tuttleParam.getProperties().getIntProperty("OfxParamPropDisplayMin")

    def getMaximum(self):
        return self._tuttleParam.getProperties().getIntProperty("OfxParamPropDisplayMax")

    def getHasChanged(self):
        return self._hasChanged

    #################### setters ####################

    def setHasChanged(self, changed):
        self._hasChanged = changed

    def setOldValue(self, value):
        self._oldValue = value

    # distinction between setValue and pushValue, because it's a slider : we do not push a command until the user don't release the cursor (but we update the model).

    def setValue(self, value):
        # used to know if bold font or not
        if(self.getDefaultValue() != value):
            self.setHasChanged(True)

        self._tuttleParam.setValue(int(value))

    def pushValue(self, newValue):
        if newValue != self.getOldValue():
            # Push the command
            cmdUpdate = CmdSetParamInt(self, int(newValue))
            cmdManager = CommandManager()
            cmdManager.push(cmdUpdate)
