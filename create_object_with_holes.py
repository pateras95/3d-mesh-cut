import trimesh
import numpy as np

def create_test_stl(filename="cube_with_hole_generated.stl"):
    # Δημιουργία ενός απλού κουτιού
    mesh = trimesh.creation.box()

    # Πάρε τις όψεις ως μια λίστα που μπορεί να τροποποιηθεί
    faces = list(mesh.faces)

    # Αφαίρεσε μία όψη (π.χ. την πρώτη) για να δημιουργήσεις μια τρύπα
    if len(faces) > 0:
        print(f"Original number of faces: {len(faces)}")
        del faces[0]
        print(f"Number of faces after removing one: {len(faces)}")

    # Δημιούργησε ένα νέο mesh με την τρύπα
    mesh_with_hole = trimesh.Trimesh(vertices=mesh.vertices, faces=np.array(faces))

    # Έλεγξε αν είναι watertight (θα πρέπει να είναι False)
    print(f"Generated mesh is watertight: {mesh_with_hole.is_watertight}")

    # Εξαγωγή του προβληματικού mesh σε αρχείο STL
    try:
        mesh_with_hole.export(filename)
        print(f"Successfully created and exported '{filename}'")
    except Exception as e:
        print(f"Error exporting mesh: {e}")

if __name__ == '__main__':
    # Κάλεσε αυτή τη συνάρτηση για να δημιουργήσεις το αρχείο STL
    # Θα δημιουργηθεί στον ίδιο φάκελο που εκτελείς το script.
    create_test_stl()

    # ... (ο υπόλοιπος κώδικας της εφαρμογής σου)
    # root = tk.Tk()
    # app = MeshRepairApp(root)
    # root.mainloop()