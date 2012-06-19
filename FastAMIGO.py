from __main__ import vtk, qt, ctk, slicer

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


class FastAMIGO:
  def __init__(self, parent):
    parent.title = "FastAMIGO Multimodal Fiducial Registration"
    parent.category = "Registration"
    parent.contributor = "David Welch"
    parent.helpText = """
    TODO: Help text here.
    """
    parent.acknowledgementText = """
    This file was originally developed by David Welch, University of Iowa.
    """
    self.parent = parent

#
# qFastAMIGOWidget
#

class FastAMIGOWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    # Collapsible button
    #dummyCollapsibleButton = ctk.ctkCollapsibleButton()
    #dummyCollapsibleButton.text = "A collapsible button"
    #self.layout.addWidget(dummyCollapsibleButton)

    # Create file IO widget
    fileIOWidget = ct.ctkFileDialog()

    # Layout within the dummy collapsible button
    dummyFormLayout = qt.QFormLayout(dummyCollapsibleButton)

    # HelloWorld button
    helloWorldButton = qt.QPushButton("Hello world")
    helloWorldButton.toolTip = "Print 'Hello world' in standard ouput."
    dummyFormLayout.addWidget(helloWorldButton)
    helloWorldButton.connect('clicked(bool)', self.onHelloWorldButtonClicked)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    self.helloWorldButton = helloWorldButton

  def onHelloWorldButtonClicked(self):
    print "Hello World !"

