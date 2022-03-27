import SimpleITK as sitk
import sitkUtils
import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import string
#
# SkyscanReconImport
#

class SkyscanReconImport(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "SkyscanReconImport" # TODO make this more human readable by adding spaces
    self.parent.categories = ["SlicerMorph.Input and Output"]
    self.parent.dependencies = []
    self.parent.contributors = ["Murat Maga (UW), Sara Rolfe (UW)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This module imports an image sequence from Bruker Skyscan microCT's into Slicer as a scalar 3D volume with correct image spacing. Accepted formats are TIF, PNG, JPG and BMP.
User needs to be point out to the *_Rec.log file found in the reconstruction folder.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
      This module was developed by Sara Rolfe and Murat Maga for SlicerMorph. SlicerMorph was originally supported by an NSF/DBI grant, "An Integrated Platform for Retrieval, Visualization and Analysis of 3D Morphology From Digital Biological Collections"
      awarded to Murat Maga (1759883), Adam Summers (1759637), and Douglas Boyer (1759839).
      https://nsf.gov/awardsearch/showAward?AWD_ID=1759883&HistoricalAwards=false
""" # replace with organization, grant and thanks.

#
# SkyscanReconImportWidget
#

class SkyscanReconImportWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input selector
    #

    # File dialog to select a file template for series
    self.inputFileSelector = ctk.ctkPathLineEdit()
    self.inputFileSelector.filters  = ctk.ctkPathLineEdit().Files
    self.inputFileSelector.setToolTip( "Select log file from a directory of images." )
    parametersFormLayout.addRow("Select log file from image series:", self.inputFileSelector)

    #
    # output volume selector
    #
    # self.outputSelector = slicer.qMRMLNodeComboBox()
    # self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    # self.outputSelector.selectNodeUponCreation = True
    # self.outputSelector.addEnabled = True
    # self.outputSelector.removeEnabled = True
    # self.outputSelector.noneEnabled = True
    # self.outputSelector.showHidden = False
    # self.outputSelector.showChildNodeTypes = False
    # self.outputSelector.renameEnabled = True
    # self.outputSelector.setMRMLScene( slicer.mrmlScene )
    # self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    # parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.inputFileSelector.connect("currentPathChanged(const QString &)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = bool(self.inputFileSelector.currentPath)


  def onApplyButton(self):
    logic = SkyscanReconImportLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    logic.run(self.inputFileSelector.currentPath, enableScreenshotsFlag)


class LogDataObject:
  """This class i
     """
  def __init__(self):
    self.FileType = "NULL"
    self.X  = "NULL"
    self.Y = "NULL"
    self.Z = "NULL"
    self.Resolution = "NULL"
    self.Prefix = "NULL"
    self.IndexLength = "NULL"
    self.SequenceStart = "NULL"
    self.SequenceEnd = "NULL"

  def ImportFromFile(self, LogFilename):
    lines = [] 					#Declare an empty list to read file into
    with open (LogFilename) as in_file:
      for line in in_file:
        lines.append(line.strip("\n"))     # add that line list, get rid of line endings
      for element in lines:  # For each element in list
        if(element.find("Result File Type=")>=0):
          self.FileType = element.split('=', 1)[1].lower()  #get standard lowercase
          print(self.FileType)
          print(element.split('=', 1)[1])
        if(element.find("Result Image Width (pixels)=")>=0):
          self.X = int(element.split('=', 1)[1])
        if(element.find("Result Image Height (pixels)=")>=0):
          self.Y = int(element.split('=', 1)[1])
        if(element.find("Sections Count=")>=0):
          self.Z = int(element.split('=', 1)[1])
        if(element.find("Pixel Size (um)=")>=0):
          self.Resolution = float(element.split('=', 1)[1])/1000 #convert from um to mm
        if(element.find("Filename Prefix=")>=0):
          self.Prefix = element.split('=', 1)[1]
        if(element.find("Filename Index Length=")>=0):
          self.IndexLength = element.split('=', 1)[1]
        if(element.find("First Section=")>=0):
          self.SequenceStart = element.split('=', 1)[1]
        if(element.find("Last Section=")>=0):
          self.SequenceEnd = element.split('=', 1)[1]
    self.SequenceStart=self.SequenceStart.zfill(int(self.IndexLength)) #pad with zeros to index length
    self.SequenceEnd=self.SequenceEnd.zfill(int(self.IndexLength)) #pad with zeros to index length

  def VerifyParameters(self):
    for attr, value in self.__dict__.items():
        if(str(value) == "NULL"):
          logging.debug("Read Failed: Please check log format")
          logging.debug(attr,value)
          return False
    return True

#
# SkyscanReconImportLogic
#
class SkyscanReconImportLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def isValidImageFileType(self, extension):
    """Checks for extensions from valid image types
    """
    if not extension in ('tif', 'bmp', 'jpg', 'png', 'tiff', 'jpeg'):
      logging.debug('isValidImageFileType failed: not a supported image type')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def applySkyscanTransform(self, volumeNode):
    #set up transform node
    transformNode = slicer.vtkMRMLTransformNode()
    slicer.mrmlScene.AddNode(transformNode)
    volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())

    #set up Skyscan transform
    transformMatrixNp  = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]])
    transformMatrixVTK = vtk.vtkMatrix4x4()
    for row in range(4):
      for col in range(4):
        transformMatrixVTK.SetElement(row, col, transformMatrixNp[row,col])

    transformNode.SetMatrixTransformToParent(transformMatrixVTK)

    #harden and clean up
    slicer.vtkSlicerTransformLogic().hardenTransform(volumeNode)
    slicer.mrmlScene.RemoveNode(transformNode)

  def run(self, inputFile, enableScreenshots=0):
    """
    Run the actual algorithm
    """
    #parse logfile
    logging.info('Processing started')
    imageLogFile = LogDataObject()   #initialize log object
    imageLogFile.ImportFromFile(inputFile)  #import image parameters of log object

    if not(imageLogFile.VerifyParameters()): #check that all parameters were set
      logging.info('Failed: Log file parameters not set')
      return False
    if not(self.isValidImageFileType(imageLogFile.FileType)): #check for valid file type
      logging.info('Failed: Invalid image type')
      logging.info(imageLogFile.FileType)
      return False

    # read image
    (inputDirectory,logPath) = os.path.split(inputFile)
    imageFileTemplate = os.path.join(inputDirectory, imageLogFile.Prefix + imageLogFile.SequenceStart + "." + imageLogFile.FileType)
    readVolumeNode = slicer.util.loadVolume(imageFileTemplate)
    #calculate image spacing
    spacing = [imageLogFile.Resolution, imageLogFile.Resolution, imageLogFile.Resolution]

    # if vector image, convert to scalar using luminance (0.30*R + 0.59*G + 0.11*B + 0.0*A)
    #check if loaded volume is vector type, if so convert to scalar
    if readVolumeNode.GetClassName() =='vtkMRMLVectorVolumeNode':
      scalarVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode', imageLogFile.Prefix)
      ijkToRAS = vtk.vtkMatrix4x4()
      readVolumeNode.GetIJKToRASMatrix(ijkToRAS)
      scalarVolumeNode.SetIJKToRASMatrix(ijkToRAS)

      scalarVolumeNode.SetSpacing(spacing)
      extractVTK = vtk.vtkImageExtractComponents()
      extractVTK.SetInputConnection(readVolumeNode.GetImageDataConnection())
      extractVTK.SetComponents(0, 1, 2)
      luminance = vtk.vtkImageLuminance()
      luminance.SetInputConnection(extractVTK.GetOutputPort())
      luminance.Update()
      scalarVolumeNode.SetImageDataConnection(luminance.GetOutputPort()) # apply
      slicer.mrmlScene.RemoveNode(readVolumeNode)

    else:
      scalarVolumeNode = readVolumeNode
      scalarVolumeNode.SetSpacing(spacing)
      scalarVolumeNode.SetName(imageLogFile.Prefix)

    self.applySkyscanTransform(scalarVolumeNode)
    slicer.util.resetSliceViews() #update the field of view

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('SkyscanReconImportTest-Start','MyScreenshot',-1)
    logging.info('Processing completed')

    return True


class SkyscanReconImportTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_SkyscanReconImport1()

  def test_SkyscanReconImport1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """
    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = SkyscanReconImportLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
