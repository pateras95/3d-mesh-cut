# Universal 3D Toolkit

Το "Universal 3D Toolkit" είναι μια σουίτα εργαλείων γραφικής διεπαφής χρήστη (GUI) γραμμένη σε Python, σχεδιασμένη για την επεξεργασία τρισδιάστατων μοντέλων. Παρέχει λειτουργίες για την επιδιόρθωση πλεγμάτων, τη βελτιστοποίηση αρχείων GLB/GLTF και τη διαδραστική κοπή τρισδιάστατων μοντέλων.

## Εργαλεία που Περιλαμβάνονται

1.  **Object Repair:**
    *   Επιδιορθώνει κοινά γεωμετρικά σφάλματα σε τρισδιάστατα μοντέλα (π.χ., .obj, .stl, .ply) όπως οπές, λανθασμένος προσανατολισμός εδρών (flipped normals) και ασυνεχή τμήματα.
    *   Χρησιμοποιεί τις βιβλιοθήκες `trimesh` και `pymeshfix`.
2.  **GLTF Optimizer:**
    *   Βελτιστοποιεί (μειώνει το μέγεθος) αρχείων GLB/GLTF.
    *   Εφαρμόζει συμπίεση γεωμετρίας Draco και συμπίεση υφών σε WebP.
    *   Εμφανίζει λεπτομερείς πληροφορίες για το μοντέλο πριν και μετά τη βελτιστοποίηση.
    *   **Απαιτεί την εξωτερική εξάρτηση `gltf-transform` CLI.**
3.  **3D Mesh Cut:**
    *   Παρέχει ένα διαδραστικό παράθυρο για την κοπή τρισδιάστατων μοντέλων "με ελεύθερο χέρι" (free-hand).
    *   Χρησιμοποιεί τη λειτουργία `FreeHandCutPlotter` της βιβλιοθήκης `vedo`.

## Προαπαιτούμενα

*   Python 3.7+
*   pip (Python package installer)
*   `gltf-transform` CLI (μόνο για το "GLTF Optimizer")

## Οδηγίες Εγκατάστασης

1.  **Κλωνοποίηση Αποθετηρίου (ή Λήψη ZIP):**
    ```bash
    git clone https://github.com/your_username/universal-3d-toolkit.git
    cd universal-3d-toolkit
    ```

2.  **Εγκατάσταση Βιβλιοθηκών Python:**
    Συνιστάται η χρήση ενός virtual environment:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```
    Εγκαταστήστε τις εξαρτήσεις:
    ```bash
    pip install tkinter trimesh pymeshfix numpy vedo
    ```
    *   **Σημείωση για Tkinter σε Linux:** Αν δεν είναι ήδη εγκατεστημένη, ίσως χρειαστεί:
        *   Debian/Ubuntu: `sudo apt-get update && sudo apt-get install python3-tk`
        *   Fedora: `sudo dnf install python3-tkinter`
    *   **Σημείωση για Vedo/VTK σε Linux:** Για τη σωστή λειτουργία των γραφικών της Vedo, μπορεί να χρειαστούν επιπλέον βιβλιοθήκες συστήματος:
        ```bash
        sudo apt-get install libgl1-mesa-glx libxt6 libxrender1
        ```

3.  **Εγκατάσταση `gltf-transform` CLI (Απαραίτητο για το GLTF Optimizer):**
    *   Πρώτα, βεβαιωθείτε ότι έχετε εγκατεστημένο το [Node.js](https://nodejs.org/) (που περιλαμβάνει το npm).
    *   Στη συνέχεια, εγκαταστήστε το `gltf-transform` καθολικά:
        ```bash
        npm install --global @gltf-transform/cli
        ```
    *   Επαληθεύστε την εγκατάσταση:
        ```bash
        gltf-transform --version
        ```
## Αντιμετώπιση Προβλημάτων

*	ModuleNotFoundError: Βεβαιωθείτε ότι έχετε εγκαταστήσει όλες τις βιβλιοθήκες Python που αναφέρονται στο Βήμα 2 του οδηγού εγκατάστασης, εκτελώντας την εντολή pip install ... μέσα στον φάκελο της εφαρμογής ή σε ένα ενεργοποιημένο virtual environment.

Το "GLTF Optimizer" αποτυγχάνει με μήνυμα "gltf-transform not found":
*	Βεβαιωθείτε ότι έχετε εγκαταστήσει το gltf-transform CLI καθολικά μέσω npm (Βήμα 3.2).
*	Ελέγξτε ότι η εντολή gltf-transform είναι προσβάσιμη από το τερματικό σας (δοκιμάστε gltf-transform --version).
*	Ίσως χρειαστεί να κάνετε επανεκκίνηση του τερματικού σας ή του υπολογιστή μετά την καθολική εγκατάσταση μέσω npm για να ενημερωθεί το PATH.

Το "3D Mesh Cut" δεν ανοίγει το παράθυρο της vedo ή κλείνει αμέσως (ειδικά σε Linux):
*	Βεβαιωθείτε ότι έχετε εγκαταστήσει τις απαραίτητες βιβλιοθήκες συστήματος για το OpenGL/VTK (δείτε τη σημείωση στο Βήμα 2 για Linux).
*	Ελέγξτε την κονσόλα/τερματικό από όπου εκτελέσατε το main.py για τυχόν μηνύματα σφάλματος που προέρχονται από τη vedo ή το VTK.

Σφάλματα Tkinter σε Linux ("No X server", "DISPLAY not set"):
*	Αυτό το εργαλείο απαιτεί ένα γραφικό περιβάλλον (X server) για να λειτουργήσει. Βεβαιωθείτε ότι εκτελείτε το script από μια περίοδο λειτουργίας με γραφικό περιβάλλον και όχι από μια κονσόλα χωρίς X.
*	Βεβαιωθείτε ότι η python3-tk (ή αντίστοιχη) είναι εγκατεστημένη.

## Εκτέλεση της Εφαρμογής

Αφού εγκαταστήσετε όλες τις εξαρτήσεις, πλοηγηθείτε στον κύριο φάκελο του project (π.χ., `universal-3d-toolkit`) στο τερματικό σας και εκτελέστε:

```bash
python main.py
