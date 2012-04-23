from __main__ import slicer
from __main__ import ctk
from __main__ import qt
from __main__ import vtk

class FastFiducial:
    def __init__(self, parent):
        parent.title = "Fast Fiducial Registration"
        parent.categories = ["Wizards"]
        parent.dependencies = ["FiducialRegistration"]
        parent.contributors =["Dave Welch (UIowa)", "Hans Johnson (UIowa)", "Nicole Aucoin (BWH)", "Ron Kikinis (BWH)"]
        parent.helpText = 'The Fast Fiducial Registration module is used to quickly register two images of a patient during treatment in the AMIGO suite.  See <a href="{0}/Documentation/{1}.{2}/Modules/FastFiducial">{0}/Documentation/{1}.{2}/Modules/FastFiducial</a> for more information.'.format(parent.slicerWikiUrl, slicer.app.majorVersion, slicer.app.minorVersion)
        # TODO: Get working BRAINS icon
        # parent.icon = qt.QIcon(':Icons/Small/BRAINSLogo.png')
        parent.acknowledgementText = 'This work is supported by NIH grants {0} and {1}, in addition to support by NA-MIC, NIH, NIBIB, NIMH and the Slicer Community.'.format('5R01NS050568-04AI','5U54EB005149-07')
        self.parent = parent

class SectionButton(ctk.ctkCollapsibleButton):
    def __init__(self, sectionTitle='Title'):
        ctk.ctkCollapsibleButton.__init__(self)
        self.text = sectionTitle

class ImageDataContainer():
    """ Data container class to keep image data matched with it's fiducial list and subclass all functions of fiducial list"""
    def __init__(self):
        self.image = slicer.vtkMRMLVolumeNode
        self.fiducialList = slicer.vtkMRMLFiducialListNode

class FiducialCoordinateLayout():
    def __init__(self, parent = None, imageString='fixed'):
        qt.QFormLayout.__init__(self)
        if parent is None:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(QHBoxLayout()) # Is this necessary?
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.imageString = imageString
        self.setLayout(qt.QHBoxLayout())

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

class FastFiducialWidget:
    """Slicer module that creates a Qt GUI for fast registration of two data sets with fiducial markers"""
    def __init__(self, parent=None):
        if parent is None:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
            self.layout = self.parent.layout()
            self.fixed = None
            self.moving = None
            self.setup()
            self.parent.show()
        else:
            self.parent = parent
            self.layout = self.parent.layout()

    def setup(self):
        self.threeByThreeCompareView()
        self.fixed = ImageDataContainer()
        self.moving = ImageDataContainer()
        ### Input section
        self.volumesFormLayout = self.addFormLayoutWidget('Input Images')
        fixedVolumeSelector = AddVolumeMRMLNodeComboBox('fixedVolumeSelector', 'Select a volume to be fixed')
        self.volumesFormLayout.addRow('Fixed Volume:', fixedVolumeSelector)
        movingVolumeSelector = AddVolumeMRMLNodeComboBox('movingVolumeSelector', 'Select a volume to be moving')
        self.volumesFormLayout.addRow('Moving Volume:', movingVolumeSelector)
        ### Fiducials section
        self.fiducialFormLayout = self.addFormLayoutWidget('Pick Fiducials')

        ### Registration section
        self.registrationFormLayout = self.addFormLayoutWidget('Register Images')

        # self.addLoadVolumeButton('Fixed', parent=self.volumesFormLayout)
        # self.addLoadVolumeButton('Moving', parent=self.volumesFormLayout)
        # TODO: self.addPickFiducialsWidget(parent=self.fiducialsFormLayout)

        self.layout.addStretch(1)

    def threeByThreeCompareView(self):
        # Create scene view with three slice views on top and three beneath (colors either R,G,Y)
        layoutManager = slicer.app.layoutManager()
        if layoutManager is None:
            return
        layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView)
        sliceViews = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceNode')
        for ii in range(3):
            sliceView = sliceViews.GetItemAsObject(ii)
            color = sliceView.GetLayoutColor()
            # TODO: sliceView.Get
            sliceViews.GetItemAsObject(ii+3).SetLayoutColor(color)
        # slicer.mrmlScene.

    def addFormLayoutWidget(self, text):
        """ Creates section widgets """
        sectionWidget = SectionButton(text)
        self.layout.addWidget(sectionWidget)
        return qt.QFormLayout(sectionWidget)

    # def addLoadVolumeButton(self, title, parent=None):
    #     addVolumeButton = qt.QPushButton('Add {0} Volume'.format(title))
    #     addVolumeButton.toolTip = "Add a volume to be registered"
    #     addVolumeButton.connect('clicked(bool)', self.onLoadVolumeButtonClicked)
    #     if parent is not None:
    #         parent.addWidget(addVolumeButton)
    #
    # def onLoadVolumeButtonClicked(self):
    #     try:
    #         isLoaded = slicer.util.openAddVolumeDialog()
    #     except AttributeError:
    #         isLoaded = False
    #     if isLoaded:
    #         # Load the volume into top red, green, yellow or bottom red, green, yellow
    #         if self.displayVolumeInSliceViews():
    #             qt.QMessageBox.information(slicer.util.mainWindow(), 'Input Volume', 'Loading successful!')
    #         else:
    #             print "Slice view display failed"
    #     else:
    #         print "Loading data failed"

    def displayVolumeInSliceViews(self):
        # 1) Determine if top or bottom is empty
        #     Top = Fixed image
        #     Bottom = Moving image
        sliceViews = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceNode')
        # 2) Get volume node
        volumes = slicer.mrmlScene.GetNodesByClass('vtkMRMLScalarVolumeDisplayNode')
        if volumes.GetNumberOfItems() == 0:
            print 'No volumes found!'
        volOne = volumes.GetItemAsObject(0)
        volTwo = volumes.GetItemAsObject(1)

        # 3) Display volume in correct windows

        return true

    def addPickFiducialButton(self):
        pass

    def addFiducialLogic(self, imageName):
        if self.fixed.image is not None:
            pass
        else:
            print 'Hello, fixed image.'

    def onRegisterButtonClicked(self):
        qt.QMessageBox.information(slicer.util.mainWindow(), 'Register', 'Registration beginning...')
        # 1) Run fiducial registration
        # 2) Apply resulant transform to moving image
        # 3) Run affine registration
        # 4) Apply transform to moving image
        # 5) Display MMI difference image?
        return true

def Execute(fixedVolume='', movingVolume=''):
    print "Fixed and moving"

    """
    vtkMRMLScene* scene = vtkMRMLScene::New();
    vtkMRMLLayoutLogic* layoutLogic = vtkMRMLLayoutLogic::New();
    layoutLogic->SetMRMLScene(scene);
    layoutLogic->GetLayoutNode()->SetViewArrangement( vtkMRMLLayoutNode::SlicerLayoutConventionalView);
    vtkCollection* views = layoutLogic->GetViewNodes();
    vtkMRMLViewNode* viewNode = vtkMRMLViewNode::SafeDownCast( views->GetItemAsObject(0));
    vtkMRMLSliceNode* redNode = vtkMRMLSliceNode::SafeDownCast( views->GetItemAsObject(1));
    vtkMRMLSliceNode* yellowNode = vtkMRMLSliceNode::SafeDownCast( views->GetItemAsObject(2));
    vtkMRMLSliceNode* greenNode = vtkMRMLSliceNode::SafeDownCast( views->GetItemAsObject(3));
    """
