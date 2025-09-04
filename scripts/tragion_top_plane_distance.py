import slicer
import vtk

def create_horizontal_plane_from_point(point_node):
    """
    Crée un plan horizontal à partir d'un point marqué dans 3D Slicer.
    
    :param point_node: Noeud Markups Point utilisé pour définir la hauteur du plan.
    :return: Position Z du plan créé.
    """
    # Vérifier si le point est valide
    if not point_node or not isinstance(point_node, slicer.vtkMRMLMarkupsFiducialNode):
        raise ValueError("Veuillez fournir un nœud de point Markups valide.")

    # Récupérer la position du point en RAS
    point_position = [0, 0, 0]
    point_node.GetNthControlPointPosition(0, point_position)  # Obtenir le premier point
    
    plane_position = point_position[2]  # Récupérer la coordonnée Z pour le plan

    # Créer un noeud de plan logique
    plane_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Plan_Point")
    plane_node.SetOrigin([0, 0, plane_position])
    plane_node.SetNormal([0, 0, 1])  # Plan horizontal (Z constant)
    plane_node.SetSize(300, 300)  # Définir la taille du plan

    # Configurer l'affichage du plan
    plane_display_node = plane_node.GetDisplayNode()
    if plane_display_node:
        plane_display_node.SetVisibility2D(True)  # Visible dans les vues Axiale, Sagittale, Coronale
        plane_display_node.SetVisibility3D(True)  # Visible en 3D
        plane_display_node.SetOpacity(0.5)  # Semi-transparent
        plane_display_node.SetColor(0.0, 0.5, 1.0)  # Bleu

    print(f"✅ Plan horizontal créé à partir du point à la position Z = {plane_position:.2f} mm.")
    return plane_position

def create_horizontal_plane_from_bounding_box(segmentation_node, offset=1.0):
    """
    Crée un plan horizontal situé juste au-dessus de la tête en utilisant la bounding box de la segmentation.

    :param segmentation_node: Noeud de segmentation dans 3D Slicer.
    :param offset: Décalage en millimètres au-dessus du sommet de la tête.
    :return: Position Z du plan créé.
    """
    # Vérifier si la segmentation est valide
    if not segmentation_node or not isinstance(segmentation_node, slicer.vtkMRMLSegmentationNode):
        raise ValueError("Veuillez fournir un nœud de segmentation valide.")

    # Récupérer les limites de la bounding box de la segmentation
    segmentation_bounds = [0] * 6
    segmentation_node.GetRASBounds(segmentation_bounds)
    
    # Déterminer la position du plan (au-dessus du sommet de la tête)
    z_max = segmentation_bounds[5]  # Coordonnée Z maximale (sommet de la tête)
    plane_position = z_max + offset  # Ajouter un petit décalage au-dessus de la tête

    # Créer un noeud de plan logique
    plane_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Plan_Haut_Tete")
    plane_node.SetOrigin([0, 0, plane_position])
    plane_node.SetNormal([0, 0, 1])  # Plan horizontal (Z constant)
    plane_node.SetSize(300, 300)  # Définir la taille du plan

    # Configurer l'affichage du plan
    plane_display_node = plane_node.GetDisplayNode()
    if plane_display_node:
        plane_display_node.SetVisibility2D(True)  # Visible dans Axiale, Sagittale, Coronale
        plane_display_node.SetVisibility3D(True)  # Visible en 3D
        plane_display_node.SetOpacity(1.0)  # Semi-transparent
        plane_display_node.SetColor(1.0, 0.5, 0.0)  # Orange

    print(f"✅ Plan horizontal créé au-dessus de la tête à la position Z = {plane_position:.2f} mm.")
    return plane_position

def calculate_distance_between_planes(z1, z2):
    """
    Calcule la distance entre deux plans horizontaux.
    
    :param z1: Position Z du premier plan.
    :param z2: Position Z du second plan.
    :return: Distance entre les deux plans.
    """
    distance = abs(z2 - z1)
    print(f"📏 Distance entre les deux plans : {distance:.2f} mm.")
    return distance

# Utilisation
point_node = slicer.util.getNode("tragion")  # Remplace par le nom du point marqué
segmentation_node = slicer.util.getNode("Segmentation")  # Remplace par la segmentation choisi

z_point = create_horizontal_plane_from_point(point_node)
z_bbox = create_horizontal_plane_from_bounding_box(segmentation_node, offset=1.0)
distance = calculate_distance_between_planes(z_point, z_bbox)
