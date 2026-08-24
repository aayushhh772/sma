import cv2
import numpy as np
from pathlib import Path
from insightface.app import FaceAnalysis


# ============================================================
# CONFIG
# ============================================================

IMAGE_FOLDER = "person_001"
OUTPUT_FILE = "person_001_embedding.npy"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


# ============================================================
# LOAD INSIGHTFACE
# ============================================================

print("Loading buffalo_l...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("Model loaded.")


# ============================================================
# FIND IMAGES
# ============================================================

folder = Path(IMAGE_FOLDER)

if not folder.exists():
    raise FileNotFoundError(
        f"Folder not found: {IMAGE_FOLDER}"
    )

image_paths = sorted(
    [
        p for p in folder.iterdir()
        if p.suffix.lower() in IMAGE_EXTENSIONS
    ]
)

if len(image_paths) == 0:
    raise ValueError(
        "No images found in the folder."
    )

print(f"\nFound {len(image_paths)} images.")


# ============================================================
# EXTRACT EMBEDDINGS
# ============================================================

embeddings = []

failed_images = []

for image_path in image_paths:

    print(f"\nProcessing: {image_path.name}")

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(str(image_path))

    if image is None:
        print("  ERROR: Could not read image.")
        failed_images.append(image_path.name)
        continue


    # --------------------------------------------------------
    # Detect face
    # --------------------------------------------------------

    faces = app.get(image)


    # Exactly ONE face required
    if len(faces) == 0:

        print("  ERROR: No face detected.")
        failed_images.append(image_path.name)
        continue


    if len(faces) > 1:

        print(
            f"  ERROR: {len(faces)} faces detected."
        )

        failed_images.append(image_path.name)
        continue


    # --------------------------------------------------------
    # Get the only face
    # --------------------------------------------------------

    face = faces[0]


    # --------------------------------------------------------
    # Get normalized embedding
    # --------------------------------------------------------

    embedding = face.normed_embedding

    print(
        f"  Embedding shape: {embedding.shape}"
    )

    embeddings.append(embedding)


# ============================================================
# CHECK RESULTS
# ============================================================

print("\n--------------------------------")
print("PROCESSING COMPLETE")
print("--------------------------------")

print(
    f"Successful images: {len(embeddings)}"
)

print(
    f"Failed images: {len(failed_images)}"
)

if failed_images:

    print("\nFailed images:")

    for filename in failed_images:
        print(f"  - {filename}")


# ============================================================
# MAKE FINAL EMBEDDING
# ============================================================

if len(embeddings) == 0:

    raise ValueError(
        "No valid face embeddings were generated."
    )


# Convert to numpy array
embeddings = np.array(embeddings)

print(
    "\nIndividual embeddings shape:",
    embeddings.shape
)

# Example:
#
# 5 images × 512 dimensions
#
# (5, 512)


# ------------------------------------------------------------
# Average embeddings
# ------------------------------------------------------------

final_embedding = np.mean(
    embeddings,
    axis=0
)


# ------------------------------------------------------------
# Normalize final embedding
# ------------------------------------------------------------

final_embedding = (
    final_embedding /
    np.linalg.norm(final_embedding)
)


# ============================================================
# SAVE
# ============================================================

np.save(
    OUTPUT_FILE,
    final_embedding
)


# ============================================================
# RESULTS
# ============================================================

print("\n--------------------------------")
print("FINAL EMBEDDING")
print("--------------------------------")

print(
    "Shape:",
    final_embedding.shape
)

print(
    "Dimensions:",
    len(final_embedding)
)

print(
    "Norm:",
    np.linalg.norm(final_embedding)
)

print(
    "\nSaved to:",
    OUTPUT_FILE
)
