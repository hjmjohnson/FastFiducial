from __main__ import ctk
from __main__ import slicer

class FFCollapsibleButton(ctk.ctkCollapsibleButton):
    def __init__(self, text='Title'):
        ctk.ctkCollapsibleButton.__init__(self)
        self.text = text

class AddVolumeMRMLNodeComboBox(slicer.qMRMLNodeComboBox):
    def __init__(self, objectName, toolTip):
        slicer.qMRMLNodeComboBox.__init__(self)
        self.objectName = objectName
        self.toolTip = toolTip
        self.nodeTypes = (('vtkMRMLScalarVolumeNode'), '')
        self.noneEnabled = False
        self.addEnabled = True
        self.removeEnabled = True
        self.enabled = True
        self.setMRMLScene(slicer.mrmlScene)

    # def connect(self, signal, slot):
    #     pass
