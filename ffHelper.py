from __main__ import ctk
from __main__ import slicer

class FFCollapsibleButton(ctk.ctkCollapsibleButton):

    def __init__(self, text='Title'):
        ctk.ctkCollapsibleButton.__init__(self)
        self.text = text


class qMRMLNodeAddVolumeComboBox(slicer.qMRMLNodeComboBox):

    def __init__(self, objectName, toolTip):
        slicer.qMRMLNodeComboBox.__init__(self)
        self.objectName = objectName
        self.toolTip = toolTip
        self.nodeTypes = (('vtkMRMLScalarVolumeNode'), '')
        self.noneEnabled = False
        self.addEnabled = False
        self.removeEnabled = True
        self.enabled = True
        self.setMRMLScene(slicer.mrmlScene)


class ImageDataContainer():
    """
    Data container class to keep image data matched with it's fiducial list
    and subclass all functions of fiducial list
    """

    def __init__(self, slicerVersion):
        self.volume = slicer.vtkMRMLScalarVolumeNode()
        self.display = slicer.vtkMRMLScalarVolumeDisplayNode()
        if slicerVersion == 4:
            self.fiducialList = slicer.vtkMRMLAnnotationHierarchyNode()
            self.newFiducial = slicer.vtkMRMLAnnotationFiducialNode()
        else:
            self.fiducialList = slicer.vtkMRMLFiducialListNode()
            self.newFiducial = slicer.vtkMRMLFiducial()

    def addToScene(self, scene):
        self.fiducialList.SetScene(scene)
