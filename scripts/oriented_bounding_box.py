import slicer
import vtk
import numpy as np

# Get the segmentation node and specify the segment ID
segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
segmentID = segmentationNode.GetSegmentation().GetNthSegmentID(0)  # Replace 0 with your segment index if necessary

# Export the segment to a binary label map representation
labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, [segmentID], labelmapVolumeNode)

# Access the voxel data of the label map
imageData = labelmapVolumeNode.GetImageData()
dims = imageData.GetDimensions()

# Iterate over voxels to find the bounding box of the segmented region
minRAS = [float('inf'), float('inf'), float('inf')]
maxRAS = [-float('inf'), -float('inf'), -float('inf')]

# Transform IJK to RAS coordinates
ijkToRasMatrix = vtk.vtkMatrix4x4()
labelmapVolumeNode.GetIJKToRASMatrix(ijkToRasMatrix)

# Iterate over voxels to find min and max RAS coordinates
for z in range(dims[2]):
    for y in range(dims[1]):
        for x in range(dims[0]):
            if imageData.GetScalarComponentAsDouble(x, y, z, 0) > 0:  # Check if voxel is part of the segment
                rasCoord = [0, 0, 0, 1]  # RAS point in homogeneous coordinates
                ijkCoord = [x, y, z, 1]
                ijkToRasMatrix.MultiplyPoint(ijkCoord, rasCoord)

                # Update min and max RAS coordinates
                minRAS[0] = min(minRAS[0], rasCoord[0])
                minRAS[1] = min(minRAS[1], rasCoord[1])
                minRAS[2] = min(minRAS[2], rasCoord[2])
                maxRAS[0] = max(maxRAS[0], rasCoord[0])
                maxRAS[1] = max(maxRAS[1], rasCoord[1])
                maxRAS[2] = max(maxRAS[2], rasCoord[2])

# Calculate center and dimensions in RAS space
centerX = (minRAS[0] + maxRAS[0]) / 2
centerY = (minRAS[1] + maxRAS[1]) / 2
centerZ = (minRAS[2] + maxRAS[2]) / 2
diameterX = maxRAS[0] - minRAS[0]
diameterY = maxRAS[1] - minRAS[1]
diameterZ = maxRAS[2] - minRAS[2]

# Print the bounding box center and dimensions
print("Bounding Box Center (RAS):", (centerX, centerY, centerZ))
print("Bounding Box Diameter (RAS):", (diameterX, diameterY, diameterZ))

# Create a cube source to represent the bounding box
cube = vtk.vtkCubeSource()
cube.SetCenter(centerX, centerY, centerZ)
cube.SetXLength(diameterX)
cube.SetYLength(diameterY)
cube.SetZLength(diameterZ)
cube.Update()

# Create a model node for the bounding box
boundingBoxModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "SegmentBoundingBox")
boundingBoxModelNode.SetAndObservePolyData(cube.GetOutput())

# Create and configure display node for bounding box visibility
displayNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
displayNode.SetColor(0, 1, 0)  # Green color for visibility
displayNode.SetOpacity(0.5)  # Semi-transparent
displayNode.SetVisibility(True)

# Enable visibility in 2D slice views
displayNode.SetSliceIntersectionVisibility(True)
displayNode.SetSliceIntersectionThickness(2)  # Adjust thickness if needed

boundingBoxModelNode.SetAndObserveDisplayNodeID(displayNode.GetID())

# Clean up temporary label map node
slicer.mrmlScene.RemoveNode(labelmapVolumeNode)

print("Bounding box created and displayed in 3D and 2D views.")
