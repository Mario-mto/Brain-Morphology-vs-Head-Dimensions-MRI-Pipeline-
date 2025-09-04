# Brain-Morphology-vs-Head-Dimensions-MRI-3D Slicer Scripts (MRI / Head & Brain)
Brain Morphology vs Head Dimensions — Semi-automated MRI pipeline (Python · 3D Slicer) to compute head/brain metrics (length, width, brain volume, circumference) using RAS landmarks and bounding boxes. Includes reproducible notebooks for correlation analysis and repeatability tests. Stack: Python, 3D Slicer, NumPy/pandas, OpenCV, Matplotlib.

Semi-automated **3D Slicer** scripts for cranial/head measurements on MRI:  
- Oriented bounding box (OBB) modelling and size readout  
- Max head circumference slice (with width/length at that level)  
- Vertical distance from tragion to top (plane-to-plane)

> Designed to run **inside 3D Slicer** (Python Interactor or “Run Script”).  
> Some scripts use `numpy`, `scipy`; the `slicer` and `vtk` modules are provided by Slicer itself.  
> Scripts come from my research project on **brain morphology vs head dimensions**.

---

## ✨ What’s inside

- `scripts/oriented_bounding_box.py`  
  Creates an **oriented bounding box** around a head model/segment and reports approximate box sizes; displays a semi-transparent model in green.  
  _Ref: exported segment → obb via `vtkOBBTree`, cube transform, model display._  
- `scripts/max_circumference_slice.py`  
  Scans horizontal planes (% of head height), cuts the closed surface, builds a **convex hull** (2D XY) to estimate **maximum circumference**, and outputs **width/length** at that level. Also spawns a visible plane + red contour model.  
- `scripts/tragion_top_plane_distance.py`  
  Creates a **horizontal plane** from a tragion **fiducial** and another plane **above the top** (bounding box Zmax + offset); reports the **vertical distance** between both.

---

## 🧰 Requirements

- **3D Slicer 5.x** (the `slicer` and `vtk` modules come with it)  
- Python packages if you run parts outside Slicer (not required in Slicer):  
  ```bash
  pip install -r requirements.txt
