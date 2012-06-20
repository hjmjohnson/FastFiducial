import os
from __main__ import slicer
from __main__ import ctk
from __main__ import qt
from __main__ import vtk
from ffHelper import FFCollapsibleButton, qMRMLNodeAddVolumeComboBox, ImageDataContainer


# #
# # FastAMIGO
# #
# class WorkflowConfiguration:
#   step_widget_files = [ 'fileIO',
#                         'getFiducials',
#                         'getROI',
#                         'displayResults']

#   step_widget_files = { 'fileIO':[('FixedImage', 'currentPath'),
#                                   ('MixedImage', 'currentPath')],
#                         'getFiducials':[()],
#                         'getROI':[()],
#                         'displayResults':[()] }

#   def __init__(self):
#         self.slicerVolumesLogic = slicer.vtkSlicerVolumesLogic()
#         self.slicerVolumesLogic.SetMRMLScene(slicer.mrmlScene)


class FastFiducial:

    def __init__(self, parent):
        parent.title = "Fast Fiducial Registration"
        parent.categories = ["Wizards"]
        parent.dependencies = ["FiducialRegistration", "BRAINSFit"]
        parent.contributors =["Dave Welch (UIowa)", "Hans Johnson (UIowa)",
                              "Nicole Aucoin (BWH)", "Ron Kikinis (BWH)"]
        slicerWikiDocUrl = parent.slicerWikiUrl + '/Documentation'
        parent.helpText = 'The Fast Fiducial Registration module quickly \
        registers two images of a patient using fiducial registration as a \
        starting place for BRAINSFit registration.  Designed for use during \
        clinical treatment in the AMIGO suite.  See \
        <a href="{0}/{1}.{2}/Modules/FastFiducial">{0}/{1}.{2}/Modules/FastFiducial</a> \
        for more information.'.format(slicerWikiDocUrl,slicer.app.majorVersion,
                                      slicer.app.minorVersion)
        # TODO: Get working BRAINS icon
        # parent.icon = qt.QIcon(':Icons/Small/BRAINSLogo.png')
        parent.acknowledgementText = 'This work is supported by NIH grants {0} \
        and {1}, in addition to support by NA-MIC, NIH, NIBIB, NIMH and the \
        Slicer Community.'.format('5R01NS050568-04AI','5U54EB005149-07')
        self.parent = parent


class FastFiducialWidget:
    """
    Slicer module that creates a Qt GUI for fast registration of two data sets
    with fiducial markers
    """
    def __init__(self, parent=None):
        if parent is None:
            self.fixed = None
            self.moving = None
            self.fixedVolumeSelector = None
            self.movingVolumeSelector = None
            self.interactor = None
            self.selector = None
            self.slicerVersion = None
            # Boilerplate code
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
            self.layout = self.parent.layout()
            self.setup()
            self.parent.show()
        else:
            self.parent = parent
            self.layout = self.parent.layout()
        self.logic = FastFiducialLogic()

    def setup(self):
        ### DEVELOPER ###
        self.reloadButton = qt.QPushButton('Reload')
        self.reloadButton.toolTip = 'Developer reload button'
        self.reloadButton.name = 'FastFiducial Reload'
        self.layout.addWidget(self.reloadButton)
        self.reloadButton.connect('clicked()', self.onReload)
        ###    END    ###
        self.slicerVersion = int(slicer.app.majorVersion)
        self.fixed = ImageDataContainer(self.slicerVersion)
        self.fixed.addToScene(slicer.mrmlScene)
        self.moving = ImageDataContainer(self.slicerVersion)
        self.interactor = slicer.mrmlScene.AddNode(slicer.vtkMRMLInteractionNode())
        self.selector = slicer.mrmlScene.AddNode(slicer.vtkMRMLSelectionNode())
        # self._threeByThreeCompareView()
        self._inputLayoutSection()
        self._fiducialLayoutSection()
        self._registrationLayoutSection()
        ### DEVELOPER ###
        import os
        if os.environ['USER'] == 'dmwelch':
            self.logic.testingData()
            self.fixedVolumeSelector.setCurrentNode(slicer.util.getNode('fixed*'))
            self.movingVolumeSelector.setCurrentNode(slicer.util.getNode('moving*'))
        ### ***END*** ###
        self.layout.addStretch(1)

    def onReload(self, moduleName="FastFiducial"):
        """ Generic reload method for any scripted module.
            ModuleWizard will subsitute correct default moduleName.
        """
        import imp, sys, os, slicer
        widgetName = moduleName + "Widget"
        # reload the source code
        # - set source file path
        # - load the module to the global space
        filePath = eval('slicer.modules.%s.path' % moduleName.lower())
        p = os.path.dirname(filePath)
        if not sys.path.__contains__(p):
            sys.path.insert(0,p)
        fp = open(filePath, "r")
        globals()[moduleName] = imp.load_module(moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
        fp.close()
        # rebuild the widget
        # - find and hide the existing widget
        # - create a new widget in the existing parent
        parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
        print parent
        for child in parent.children():
            try:
                child.hide()
            except AttributeError:
                pass
        globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
        globals()[widgetName.lower()].setup()

    def _threeByThreeCompareView(self):
        """
        Create scene view with three slice views on top and three beneath
        (colors R,G,Y for top and bottom)
        """
        layoutManager = slicer.app.layoutManager()
        if layoutManager is None:
            return
        layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView)
        sliceViewCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceNode')
        for ii in range(3):
            sliceViewTop = sliceViewCollection.GetItemAsObject(ii)
            sliceViewBottom = sliceViewCollection.GetItemAsObject(ii+3)
            color = sliceViewTop.GetLayoutColor()
            print "The color of slice %d is %d, %d, %d" % (ii, color[0], color[1], color[2])
            sliceViewBottom.SetLayoutColor(color[0], color[1], color[2])
            # Get scene to update!!!
            sliceViewBottom.Modified()
            slicer.mrmlScene.Modified()
            layoutManager.layoutChanged(True)

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

    def _inputLayoutSection(self):
        inputCollapsibleButton = FFCollapsibleButton('Input volumes')
        self.layout.addWidget(inputCollapsibleButton)
        # Layout within the input collapsible button
        inputFormLayout = qt.QFormLayout(inputCollapsibleButton)
        ### Fixed Volume Selector ###
        # The fixed volume frame
        fixedVolumeFrame = qt.QFrame(inputCollapsibleButton)
        fixedVolumeFrame.setLayout(qt.QHBoxLayout())
        inputFormLayout.addWidget(fixedVolumeFrame)
        # The volume selector button label
        fixedVolumeLabel = qt.QLabel('Fixed Volume: ', fixedVolumeFrame)
        fixedVolumeFrame.layout().addWidget(fixedVolumeLabel)
        # The volume selector buttom
        self.fixedVolumeSelector = qMRMLNodeAddVolumeComboBox(objectName='fixedVolumeSelector',
                                                              toolTip='Select a fixed volume')
        self.fixedVolumeSelector.connect('currentNodeChanged(vtkMRMLNode*)',
                                         self.setFixedVolumeNode)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', self.setFixedSliceViews)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                            self.fixedVolumeSelector,
                            'setMRMLScene(vtkMRMLScene*)')
        fixedVolumeFrame.layout().addWidget(self.fixedVolumeSelector)
        ### The Moving Volume Selector ###
        # The moving volume frame
        movingVolumeFrame = qt.QFrame(inputCollapsibleButton)
        movingVolumeFrame.setLayout(qt.QHBoxLayout())
        inputFormLayout.addWidget(movingVolumeFrame)
        # The volume selector button label
        movingVolumeLabel = qt.QLabel('Moving Volume: ', movingVolumeFrame)
        movingVolumeFrame.layout().addWidget(movingVolumeLabel)
        # The volume selector buttom
        self.movingVolumeSelector = qMRMLNodeAddVolumeComboBox(objectName='movingVolumeSelector',
                                                               toolTip='Select a moving volume')
        self.movingVolumeSelector.connect('currentNodeChanged(vtkMRMLNode*)',
                                          self.setMovingVolumeNode)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', self.setMovingSliceViews)
        self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                            self.movingVolumeSelector,
                            'setMRMLScene(vtkMRMLScene*)')
        movingVolumeFrame.layout().addWidget(self.movingVolumeSelector)
        # Moved from __init__()
        self.fixedVolumeSelector.setMRMLScene(slicer.mrmlScene)
        self.movingVolumeSelector.setMRMLScene(slicer.mrmlScene)

    def setFixedVolumeNode(self, newVolumeNode):
        self._setVolumeNode(newVolumeNode, 'fixed')
        # self._setFixedSliceViews()

    def setMovingVolumeNode(self, newVolumeNode):
        self._setVolumeNode(newVolumeNode, 'moving')
        # self._setMovingSliceViews()

    def _setVolumeNode(self, newVolumeNode, flag):
        # print "Attempting to set %s" % flag
        newDisplayNode = None
        if not newVolumeNode is None:
            newDisplayNode = newVolumeNode.GetScalarVolumeDisplayNode()
        if flag == 'fixed':
            self.fixed.volume = newVolumeNode
            self.fixed.display = newDisplayNode
        elif flag == 'moving':
            self.moving.volume = newVolumeNode
            self.moving.display = newDisplayNode
        else:
            raise Exception('I have no idea why this would ever happen...')

    def setFixedSliceViews(self):
        pass

    def setMovingSliceViews(self):
        pass

    def _fiducialLayoutSection(self):
        fiducialCollapsibleButton = FFCollapsibleButton('Pick fiducials')
        self.layout.addWidget(fiducialCollapsibleButton)
        # Create first row widgets
        fiducialFormLayout = qt.QFormLayout(fiducialCollapsibleButton)
        # Create button frame
        fiducialPickFrame = qt.QFrame(fiducialCollapsibleButton)
        fiducialPickFrame.setLayout(qt.QHBoxLayout())
        fiducialFormLayout.addWidget(fiducialPickFrame)
        fiducialPickLabel = qt.QLabel('New fiducial: ', fiducialPickFrame)
        fiducialPickButton = qt.QPushButton('Create')
        fiducialPickLabel.setBuddy(fiducialPickButton)
        fiducialPickButton.connect('clicked()', self.createNewFiducial)
        fiducialPickButton.connect('clicked()', self.fixed.fiducialList.Modified)
        fiducialPickFrame.layout().addWidget(fiducialPickLabel)
        fiducialPickFrame.layout().addWidget(fiducialPickButton)
        # self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', self.setNewFiducial)
        # # Create spin box frame
        # fiducialEditFrame = qt.QFrame(fiducialCollapsibleButton)
        # fiducialEditFrame.setLayout(qt.QHBoxLayout())
        # fiducialFormLayout.addWidget(fiducialEditFrame)
        # fiducialEditLabel = qt.QLabel('Edit fiducial: ', fiducialEditFrame)
        # fiducialEditSpinBox = qt.QSpinBox()
        # fiducialEditSpinBox.minimum = 1
        # fiducialEditSpinBox.maximum = 5
        # fiducialEditSpinBox.prefix = 'Fiducial '
        # fiducialEditLabel.setBuddy(fiducialEditSpinBox)
        # fiducialEditSpinBox.connect('valueChanged(int)', self.editSelectedFiducial)
        # fiducialEditFrame.layout().addWidget(fiducialEditLabel)
        # fiducialEditFrame.layout().addWidget(fiducialEditSpinBox)

    def createNewFiducial(self):
        # TODO: Write this function
        # If the lists are not already added to the scene, add them
        if not slicer.mrmlScene.IsNodePresent(self.fixed.fiducialList):
            slicer.mrmlScene.AddNode(self.fixed.fiducialList)
        if not slicer.mrmlScene.IsNodePresent(self.moving.fiducialList):
            slicer.mrmlScene.AddNode(self.moving.fiducialList)
        # Get the singleton interactor from the scene
        self.interactor.SwitchToSinglePlaceMode()
        # Get the singleton selector from the scene
        self.selector.SetActiveFiducialListID(self.fixed.fiducialList.GetID())
        self.selector.SetActiveAnnotationID(self.fixed.newFiducial.GetID())
        self.setNewFiducial(slicer.mrmlScene)

    def setNewFiducial(self, newSceneNode):
        # Allow click to set the new fiducial to the list
        if self.fixed.fiducialList:
            self.fixed.fiducialList.RemoveObserver(vtk.vtkCommand.ModifiedEvent)
            self.fixed.fiducialList.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onMRMLNodeAdded)
        self.fixed.fiducialList.UpdateScene(newSceneNode)
        collection = vtk.vtkCollection()
        self.fixed.fiducialList.GetDirectChildren(collection)
        print collection.GetNumberOfItems()
        ######
        #        create fiducial in volume labeled with fiducial list index
        #        add fiducial to appropriate list
        #    else:
        #        self.createNewFiducial() (i.e. ignore)
        #    if volume is not marked done:
        #        mark volume as done
        #    else:
        #        give warning
        #    if both are marked done:
        #        reset done flag
        #        quit
        #    else:
        #        self.createNewFiducial()
        # elif right-click:
        #    ignore
        # elif ESC:
        #    remove latest fiducial if lengths not equal (assumes ordered list!!!)
        #    reset done flags
        # elif RET:
        #    ignore (both fiducials need to be set (i.e. both flags need to == 'done'))
        # self.selector.AddNewAnnotationIDToList(self.fixed.newFiducial.GetID())
        print "Created a new fiducial node"

    def onMRMLNodeAdded(self, observer, eventid):
        if eventid == slicer.mrmlScene.NodeAddedEvent: #slicer.vtkMRMLAnnotationFiducialNode.FiducialNodeAddedEvent???
            # Get the node added
            print "Getting the new node ID..."
            newNodeID = self.selector.GetActiveAnnotationID()
            newNode = slicer.mrmlScene.GetNodeByID(newNodeID)
            if newNode.GetClassName() == 'vtkMRMLAnnotationFiducialNode':
                print "Adding the new fiducial to the fixed list..."
                newHeirarchyNode = newNode.GetParentNode()
                newHeirarchyNode.SetParentNodeID(self.fixed.fiducialList.GetID())
            else:
                print "Not an annotation node OR not implemented for Slicer3"

    def editSelectedFiducial(self, fiducialIndex):
        print "The value is %d" % fiducialIndex
        # TODO: Write this function
        # 1) Get next mouse click or keyboard
        #    a) If ESC, escape without saving changes
        #    b) If left-click:
        #        i) Unlock (modify) ONLY the fiducial with matching index
        #               (need to get version for Slicer3 to determine list numbering)
        #       ii) Get fiducial under mouse and modify WITHOUT saving
        #      iii) call editSelectedFiducial
        #    c) If right-click:
        #        i) modify slice views (i.e. ignore)
        #    d) if RET, save new fiducial location

    def _registrationLayoutSection(self):
        registrationCollapsibleButton = FFCollapsibleButton('Register Images')
        self.layout.addWidget(registrationCollapsibleButton)
        registrationFormLayout = qt.QFormLayout(registrationCollapsibleButton)
        registrationFrame = qt.QFrame(registrationCollapsibleButton)
        registrationFrame.setLayout(qt.QHBoxLayout())
        registrationFormLayout.addWidget(registrationFrame)
        self.registerButton = qt.QPushButton('Run')
        self.registerButton.toolTip = "Run fast registration method"
        self.registerButton.connect('clicked()', self.onRegisterButtonClicked)
        registrationFrame.layout().addWidget(self.registerButton)

    def onRegisterButtonClicked(self):
        qt.QMessageBox.information(slicer.util.mainWindow(), 'Register', 'Completed!')
        print "Running registration..."
        # 1) Run fiducial registration
        initialTransformNode = FastFiducialRegistration(self.fixedFiducialList, self.movingFiducialList)
        # 2) Apply resulant transform to moving image
        self.movingVolume.SetParentNodeID(initialTransformNode.GetID())
        # 3) Run affine registration
        finalTransformNode = BRAINSFitEZRegistration(self.fixedVolume, self.movingVolume, initialTransformNode)
        # 4) Apply transform to moving image
        finalTransformNode.SetParentID(initialTransformNode.GetID())
        self.movingVolume.SetParentID(finalTransformNode.GetID())
        # 5) TODO: Display MMI difference image?
        return True

class FastFiducialLogic(object):
    """ Implement fiducial picking logic and registration logic for the module
    """
    def __init__(self, fixed=None, moving=None):
        self.fixedList = None
        self.movingList = None
        self.fixed = fixed
        self.moving = moving

    def testingData(self):
        """ Load some default data for development
            and set up a transform and viewing scenario for it.
        """
        dataDirectory = 'Development/src/extensions/FastFiducial/Testing/Data'
        if not slicer.util.getNodes('fixed*'):
            import os
            fileName = os.path.join(os.environ['HOME'], dataDirectory, 'fixed.nii.gz')
            vl = slicer.modules.volumes.logic()
            volumeNode = vl.AddArchetypeScalarVolume (fileName, "fixed", 0)
        if not slicer.util.getNodes('moving*'):
            import os
            fileName = os.path.join(os.environ['HOME'], dataDirectory, 'moving.nii.gz')
            vl = slicer.modules.volumes.logic()
            volumeNode = vl.AddArchetypeScalarVolume (fileName, "neutral", 0)
        head = slicer.util.getNode('fixed')
        neutral = slicer.util.getNode('moving')
        compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
        for compositeNode in compositeNodes.values():
            compositeNode.SetBackgroundVolumeID(head.GetID())
            compositeNode.SetForegroundVolumeID(neutral.GetID())
            compositeNode.SetForegroundOpacity(0.5)
        applicationLogic = slicer.app.applicationLogic()
        applicationLogic.FitSliceToAll()


class FastFiducialRegistration():
    """ Run the registration once the registration button is clicked """
    def __init__(self, fixedImage=None, movingImage=None):
        self.fixedImage = fixedImage
        self.movingImage = movingImage

    def _setFiducialLists(self, sceneFixedList=None, sceneMovingList=None):
        self.fixed = sceneFixedList
        self.moving = sceneMovingList
        if self.fixed.GetClassName() == 'vtkMRMLAnnotationHierarchyNode':
            # slicer4 style
            self.fiducialStyle = 4
            self.fixedCount = self.fixed.GetNumberOfChildren()
            self.movingCount = self.moving.GetNumberOfChildren()
            self.newFixed = slicer.vtkMRMLAnnotationHierarchyNode()
            self.newMoving = slicer.vtkMRMLAnnotationHierarchyNode()
        else:
            # slicer3 style
            self.fiducialStyle = 3
            self.fixedCount = self.fixed.GetNumberOfFiducials()
            self.movingCount = self.moving.GetNumberOfFiducials()
            self.newFixed = slicer.vtkMRMLFiducialListNode()
            self.newMoving = slicer.vtkMRMLFiducialListNode()
        return self.run()

    def _checkCounts(self):
        # Verify that the lists are equal lengths and not zero
        try:
            assert not self.fixedCount == 0
        except AssertionError:
            raise Warning('One or more fiducial lists are empty')
            return False
        try:
            assert self.fixedCount == self.movingCount
        except AssertionError:
            raise Warning('Fiducial lists are not of equal length')
            return False
        return True

    def __checkFiducialReferenceVolume(self, fiducialList):
        # Verify that the lists have only one parent volume each
        if self.style == 4:
            firstVolumeID = fiducialList.GetNthChildNode(0).GetReferenceNodeID()
            for index in range(fiducialList.GetNumberOfChildern() - 1):
                thisVolumeID = fiducialList.GetNthChildNode(index + 1).GetReferenceNodeID()
                try:
                    assert firstVolumeID == thisVolumeID
                except AssertionError:
                    raise AssertionError('Fiducial list has different parent volumes for member fiducial %d' % index)
        else:
            # firstVolumeID = fiducialList.GetNthFiducial(0).??GetMRMLSceneID()??
            # for index in range(fiducialList.GetNumberOfFiducials() -1):
            #     thisVolumeID = fiducialList.GetNthFiducial(index + 1).??GetMRMLSceneID()??
            #     try:
            #         assert firstVolumeID == thisVolumeID
            #     except AssertionError:
            #         raise AssertionError('Fiducial list has different parent volumes for member fiducial %d' % index)
            raise Exception('Slicer3 style volume checking not yet implemented!')

    def __reparentFiducials(self, oldParent, newParent):
        if self.style == 4:
            for index in range(self.fixedCount):
                fiducialNode = oldParentList.GetItemAsObject(index)
                fiducialNode.SetParentNodeID(newParentList.GetID())
        else:
            raise Exception('Slicer3 style volume checking not yet implemented!')

    def run(self):
        self._checkCounts()
        self._checkFiducialReferenceVolume(self.fixed)
        self._checkFiducialReferenceVolume(self.moving)
        self._reparentFiducials(self.fixed, self.newFixed)
        self._reparentFiducials(self.moving, self.newMoving)
        # return initalTransformNode
        fiducialRegistrationParameters = {}
        fiducialRegistrationParameters['fixedLandmarks'] = self.newFixed.GetName()
        fiducialRegistrationParameters['movingLandmarks'] = self.moving.GetName()
        fiducialRegistrationParameters['transformType'] = 'Rigid'
        fiducialRegistrationParameters['saveTransform'] = 'initialTransformOutput'
        initialTransformNode = slicer.cli.run(slicer.modules.fiducialregistration, None,
                                              fiducialRegistrationParameters, True)
        return initialTransformNode

class BRAINSFitEZRegistration():
    def __init__(fixedVolume, movingVolume, initialTransform):
        brainsFitEZParameters = {}
        brainsFitEZParameters['fixedVolume'] = fixedVolume.GetName()
        brainsFitEZParameters['movingVolume'] = movingVolume.GetName()
        brainsFitEZParameters['linearTransform'] = 'finalTransformOutput'
        brainsFitEZParameters['useRigid'] = True
        brainsFitEZParameters['useAffine'] = False
        brainsFitEZParameters['initialTransform'] = initialTransform.GetName()
        finalTransformNode = slicer.cli.run(slicer.modules.brainsFitEZ, None,
                                            brainsFitEZParameters, True)
        return initialTransformNode
