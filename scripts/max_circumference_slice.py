import slicer
import vtk
from scipy.spatial import ConvexHull
import numpy as np

def plan_max_circum_head(segmentation_node, start_percentage, end_percentage, step_percentage):
    """
    Trouver la circonférence max de la tête dans un plan horizontal, et afficher le plan correspondant ainsi que le contour mesuré.
    
    Ajoute également la mesure de la longueur et de la largeur de la tête à ce niveau.

    :param segmentation_node: Noeud de segmentation dans 3D Slicer.
    :param start_percentage: Position de départ en pourcentage de la hauteur de la tête.
    :param end_percentage: Position finale en pourcentage de la hauteur de la tête.
    :param step_percentage: Incrément en pourcentage entre chaque étape.
    :return: Le plus grand périmètre trouvé, son pourcentage de hauteur, la largeur et la longueur mesurées.
    """
    # Vérification du noeud de segmentation
    if not segmentation_node or not isinstance(segmentation_node, slicer.vtkMRMLSegmentationNode):
        raise ValueError("Veuillez fournir un nœud de segmentation valide.")
    
    # Obtenir les limites (bounding box) de la segmentation en coordonnées RAS
    segmentation_bounds = [0] * 6
    segmentation_node.GetRASBounds(segmentation_bounds)
    z_min, z_max = segmentation_bounds[4], segmentation_bounds[5]
    z_height = z_max - z_min

    if z_height <= 0:
        raise ValueError("La hauteur de la tête est invalide. Vérifiez la segmentation.")

    # Générer une surface fermée si elle n'existe pas déjà
    segmentation = segmentation_node.GetSegmentation()
    representation_name = slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName()
    if not segmentation.ContainsRepresentation(representation_name):
        segmentation.CreateRepresentation(representation_name)

    # Obtenir la surface fermée
    poly_data = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(segmentation.GetNthSegmentID(0), poly_data)

    max_perimeter = 0.0
    best_percentage = 0
    best_hull_polydata = None
    best_points = None  # Pour stocker les points du contour optimal
    best_plane_position = 0

    # Boucle sur les pourcentages spécifiés
    for percentage in range(start_percentage, end_percentage + 1, step_percentage):
        plane_position = z_min + (percentage / 100.0) * z_height

        # Découper la surface avec un plan horizontal
        plane = vtk.vtkPlane()
        plane.SetOrigin(0, 0, plane_position)
        plane.SetNormal(0, 0, 1)  # Plan horizontal (normale Z)

        cutter = vtk.vtkCutter()
        cutter.SetInputData(poly_data)
        cutter.SetCutFunction(plane)
        cutter.Update()

        # Récupérer les lignes résultantes de l'intersection
        contour_polydata = cutter.GetOutput()
        if contour_polydata.GetNumberOfCells() == 0:
            continue

        # Convertir les lignes en points pour construire le Convex Hull
        points = []
        for i in range(contour_polydata.GetNumberOfCells()):
            cell = contour_polydata.GetCell(i)
            for j in range(cell.GetNumberOfPoints()):
                points.append(cell.GetPoints().GetPoint(j))

        points = np.array(points)
        if len(points) == 0:
            continue

        # Construire l'enveloppe convexe avec scipy.spatial.ConvexHull
        try:
            hull = ConvexHull(points[:, :2])  # Utiliser uniquement les coordonnées X et Y
        except Exception:
            continue

        # Calculer le périmètre de l'enveloppe convexe
        perimeter = sum(np.linalg.norm(points[simplex[0]] - points[simplex[1]]) for simplex in hull.simplices)

        # Mise à jour si plus grande circonférence trouvée
        if perimeter > max_perimeter:
            max_perimeter = perimeter
            best_percentage = percentage
            best_plane_position = plane_position
            best_points = points

            # Sauvegarder les données pour le contour correspondant
            hull_points = vtk.vtkPoints()
            for vertex in hull.vertices:
                hull_points.InsertNextPoint(points[vertex][0], points[vertex][1], plane_position)

            hull_lines = vtk.vtkCellArray()
            for i in range(len(hull.vertices)):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, i)
                line.GetPointIds().SetId(1, (i + 1) % len(hull.vertices))
                hull_lines.InsertNextCell(line)

            best_hull_polydata = vtk.vtkPolyData()
            best_hull_polydata.SetPoints(hull_points)
            best_hull_polydata.SetLines(hull_lines)

    # Calculer la largeur et la longueur de la tête à ce niveau
    if best_points is not None:
        x_min, x_max = np.min(best_points[:, 0]), np.max(best_points[:, 0])
        y_min, y_max = np.min(best_points[:, 1]), np.max(best_points[:, 1])
        width = x_max - x_min  # Largeur
        length = y_max - y_min  # Longueur
    else:
        width, length = 0, 0

    # Ajouter le meilleur contour comme modèle dans la scène
    if best_hull_polydata:
        contour_model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "MeilleurContourExterne")
        contour_model_node.SetAndObservePolyData(best_hull_polydata)

        # Configurer l'affichage du modèle (couleur rouge)
        contour_display_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelDisplayNode")
        contour_display_node.SetColor(1.0, 0.0, 0.0)  # Rouge
        contour_display_node.SetOpacity(1.0)  # Opaque
        contour_display_node.SetLineWidth(2)  # Épaisseur de la ligne
        contour_model_node.SetAndObserveDisplayNodeID(contour_display_node.GetID())

         # Créer un noeud de plan logique pour le rendre visible dans toutes les vues
        plane_position = z_min + (best_percentage / 100.0) * z_height

        plane_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "PlanHorizontal")
        plane_node.SetOrigin([0, 0, plane_position])
        plane_node.SetNormal([0, 0, 1])  # Plan horizontal

        # Définir les dimensions du plan (agrandir le plan)
        plane_size = [300, 300]  # Largeur et hauteur du plan en millimètres
        plane_node.SetSize(plane_size[0], plane_size[1])

        # Configurer l'affichage du plan
        plane_node.GetDisplayNode().SetVisibility2D(True)  # Visible dans les vues de coupe
        plane_node.GetDisplayNode().SetVisibility3D(True)  # Visible en 3D
        plane_node.GetDisplayNode().SetOpacity(0.5)  # Semi-transparent
        plane_node.GetDisplayNode().SetColor(0.0, 0.5, 1.0)  # Rose/Orange

        # Affichage des résultats
        print(f"Le plus grand périmètre trouvé est : {max_perimeter:.2f} mm")
        print(f"Il se situe à : {best_percentage}% de la hauteur de la tête")
        print(f"Largeur de la tête à ce niveau : {width:.2f} mm")
        print(f"Longueur de la tête à ce niveau : {length:.2f} mm")

    return max_perimeter, best_percentage, width, length

# Utilisation
segmentation_node = slicer.util.getNode("Segmentation_3")  # Mettre la segmentation associée
start_percentage = 40
end_percentage = 100
step_percentage = 1
plan_max_circum_head(segmentation_node, start_percentage, end_percentage, step_percentage)
