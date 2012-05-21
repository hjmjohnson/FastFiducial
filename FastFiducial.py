import os
from __main__ import slicer
from __main__ import ctk
from __main__ import qt
from __main__ import vtk
from ffHelper import FFCollapsibleButton, AddVolumeMRMLNodeComboBox

class FastFiducial:
    def __init__(self, parent):
        parent.title = "Fast Fiducial Registration"
        parent.categories = ["Wizards"]
        parent.dependencies = ["FiducialRegistration"]
        parent.contributors =["Dave Welch (UIowa)", "Hans Johnson (UIowa)", "Nicole Aucoin (BWH)", "Ron Kikinis (BWH)"]
        slicerWikiDocUrl = parent.slicerWikiUrl + '/Documentation'
        parent.helpText = 'The Fast Fiducial Registration module is used to quickly register two images of a patient during \
        treatment in the AMIGO suite.  See <a href="{0}/{1}.{2}/Modules/FastFiducial">{0}/{1}.{2}/Modules/FastFiducial</a> \
        for more information.'.format(slicerWikiDocUrl, slicer.app.majorVersion, slicer.app.minorVersion)
        # TODO: Get working BRAINS icon
        # parent.icon = qt.QIcon(':Icons/Small/BRAINSLogo.png')
        parent.acknowledgementText = 'This work is supported by NIH grants {0} and {1}, in addition to support by NA-MIC, \
        NIH, NIBIB, NIMH and the Slicer Community.'.format('5R01NS050568-04AI','5U54EB005149-07')
        self.parent = parent

class ImageDataContainer():
    """ Data container class to keep image data matched with it's fiducial list and subclass all functions of fiducial list"""
    def __init__(self):
        self.image = slicer.vtkMRMLVolumeNode
        self.fiducialList = slicer.vtkMRMLFiducialListNode

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
        self._threeByThreeCompareView()
        self._inputLayoutSection()
        self._fiducialLayoutSection()
        ### Registration section
        # self.registrationFormLayout = self.addFormLayoutWidget('Register Images')
        # self.fixed = ImageDataContainer()
        # self.moving = ImageDataContainer()
        # self.addLoadVolumeButton('Fixed', parent=self.volumesFormLayout)
        # self.addLoadVolumeButton('Moving', parent=self.volumesFormLayout)
        # TODO: self.addPickFiducialsWidget(parent=self.fiducialsFormLayout)
        # qtFile = os.path.join(os.path.dirname(slicer.modules.fastfiducial.path),'Designer','moduleGUI.ui')
        # self.fiducialFormLayout = self._load_QtUIFile(qtFile)
        self.layout.addStretch(1)

    # def _load_QtUIFile(self, filename):
    #     fiducialLayout = None
    #     # Load UI file
    #     uiloader = qt.QUiLoader()
    #     file = qt.QFile(filename)
    #     try:
    #         file.open(qt.QFile.ReadOnly)
    #         fiducialLayoutWidget = uiloader.load(file)
    #         self.layout.addWidget(fiducialLayoutWidget)
    #     finally:
    #         file.close()
    #     return qt.QFormLayout(fiducialLayout)
    #     # Get references to both the QPushButton and the QLineEdit
    #     # clear_button = line_edit_widget.findChild(qt.QPushButton, 'ClearButton')
    #     # line_edit = line_edit_widget.findChild(qt.QLineEdit, 'LineEdit')
    #     # clear_button.connect('clicked()', line_edit, 'clear()')
    #     # line_edit_widget.show()

    def _threeByThreeCompareView(self):
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
            sliceViews.GetItemAsObject(ii+3).Modified()
            # sliceViews.Modified()
            # slicer.mrmlScene.Modified()

    def _inputLayoutSection(self):
        inputCollapsibleButton = FFCollapsibleButton('Input volumes')
        self.layout.addWidget(inputCollapsibleButton)
        fixedVolumeSelector = AddVolumeMRMLNodeComboBox(objectName='fixedVolumeSelector', toolTip='Select a fixed volume')
        movingVolumeSelector = AddVolumeMRMLNodeComboBox(objectName='movingVolumeSelector', toolTip='Select a moving volume')
        # Set the interior layout
        inputFormLayout = qt.QFormLayout(inputCollapsibleButton)
        inputFormLayout.addRow('Fixed Volume:', fixedVolumeSelector)
        inputFormLayout.addRow('Moving Volume:', movingVolumeSelector)

    def _sliceTitleLayout(self):
        titleLayout = qt.QHBoxLayout()
        titleLayout.addWidget(qt.QLabel(text='Red'))
        titleLayout.addWidget(qt.QLabel(text='Yellow'))
        titleLayout.addWidget(qt.QLabel(text='Green'))
        return titleLayout

    def _fiducialLayoutSection(self):
        fiducialCollapsibleButton = FFCollapsibleButton('Pick fiducials')
        self.layout.addWidget(fiducialCollapsibleButton)
        # Create first row widgets
        fixedLabelWidget = qt.QLabel(text='Fixed(Top)')
        movingLabelWidget = qt.QLabel(text='Moving(Bottom)')
        spacerItem = qt.QSpacerItem(20,20)
        # Add widgets to layout
        fiducialGridLayout = qt.QGridLayout(fiducialCollapsibleButton)
        fiducialGridLayout.addWidget(fixedLabelWidget, 0, 0)
        fiducialGridLayout.addWidget(movingLabelWidget, 0, 1)
        # fiducialGridLayout.addItem(spacerItem, 0, 2) <-- This line causes crash!!!
        fiducialGridLayout.addLayout(self._sliceTitleLayout(),0,2)
        # fiducialGridLayout.addLayout(self._sliceTitleLayout(),1,1)
        # fiducialGridLayout.addWidget(qt.QLabel(text='Active'),1,2,-1)
        # Add up to five points
        # fiducialHorizontalLayout.addItem(self._fiducialCoordinateRow())
        # fiducialHorizontalLayout.addItem(self._fiducialCoordinateRow())
        # fiducialHorizontalLayout.addItem(self._fiducialCoordinateRow())
        # fiducialHorizontalLayout.addItem(self._fiducialCoordinateRow())

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
        initialTransformNode = _runFiducialRegistration(self.fixedFiducialList, self.movingFiducialList)
        # 2) Apply resulant transform to moving image
        # 3) Run affine registration
        # 4) Apply transform to moving image
        # 5) Display MMI difference image?
        return true

def _runFiducialRegistration(sceneFixedList, sceneMovingList):
    # Verify that the lists are equal lengths and not zero
    fixedCount = sceneFixedList.GetNumberOfChildren()
    assert fixedCount == sceneMovingList.GetNumberOfChildren()
    assert not sceneFixedList.GetNumberOfChildren() == 0
    # Verify that the lists have only one parent volume each
    try:
        _checkFiducialReferenceVolume(sceneFixedList)
        _checkFiducialReferenceVolume(sceneMovingList)
    except AssertionError:
        raise AssertionError('Fiducial list(s) have different parent volumes for member fiducials')
    # Reparent fiducials
    fixedFiducialList = slicer.vtkMRMLAnnotationHierarchyNode()
    movingFiducialList = slicer.vtkMRMLAnnotationHierarchyNode()
    __reparentFiducials(fixedCount, sceneFixedList, fixedFiducialList)
    __reparentFiducials(fixedCount, sceneMovingList, movingFiducialList)
    # return initalTransformNode

def __reparentFiducials(count, oldParentList, newParentList):
    for index in range(count):
        fiducialNode = oldParentList.GetItemAsObject(index)
        fiducialNode.SetParentNodeID(newParentList.GetID())

def __checkFiducialReferenceVolume(fiducialList):
    firstFiducialReferenceNodeID = fiducialList.GetNthChildNode(0).GetReferenceNodeID()
    for index in range(fiducialList.GetNumberOfChildern() - 1):
        thisFiducialReferenceNodeID = fiducialList.GetNthChildNode(index + 1).GetReferenceNodeID()
        assert firstFiducialReferenceNodeID == thisFiducialReferenceNodeID

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
