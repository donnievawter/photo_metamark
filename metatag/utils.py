import os
import tempfile
import rawpy
import imageio
import shutil
from pillow_heif import register_heif_opener
from PIL import Image
from metatag.logger import log_action
from metatag.logger import get_logger

log = get_logger()

NATIVE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
RAW_EXTENSIONS = {".cr2", ".nef", ".arw", ".dng", ".rw2", ".orf", ".raf", ".sr2"}
HEIF_EXTENSIONS = {".heic", ".heif"}
SUPPORTED_EXTENSIONS = NATIVE_EXTENSIONS.union(RAW_EXTENSIONS).union(HEIF_EXTENSIONS)

DONE_MARKER = ".metamark.done"
register_heif_opener()


def is_supported_image(path):
    ext = os.path.splitext(path.lower())[1]
    return ext in SUPPORTED_EXTENSIONS


def get_image_type(path):
    ext = os.path.splitext(path.lower())[1]
    if ext in RAW_EXTENSIONS:
        return "raw"
    elif ext in HEIF_EXTENSIONS:
        return "heif"
    elif ext in NATIVE_EXTENSIONS:
        return "native"
    return "unsupported"


def convert_heic_to_jpeg(heic_path, output_dir="/tmp"):
    filename = os.path.splitext(os.path.basename(heic_path))[0] + ".jpg"
    output_path = os.path.join(output_dir, filename)
    img = Image.open(heic_path)
    img.save(output_path, format="JPEG")
    log_action("SAVE0", output_path)
    return output_path


def get_output_path(image_path, output_dir):
    """Return the destination path for a copied image."""
    filename = os.path.basename(image_path)
    return os.path.join(output_dir, filename)


def get_dest_path(image_path, output_dir=None, dry_run=False):
    """
    Return the path to operate on:
    - If output_dir is set, copy image there and return new path
    - If dry_run is True, do not copy, just simulate
    - If no output_dir, return original path
    """
    if output_dir:
        dest_path = get_output_path(image_path, output_dir)
        if not dry_run:
            shutil.copy2(image_path, dest_path)
            log_action("COPY", dest_path)
        return dest_path
    return image_path


def find_images(folder):
    """Recursively find supported image files in a folder."""
    image_paths = []
    for root, _, files in os.walk(folder):
        for f in files:
            ext = os.path.splitext(f.lower())[1]
            if ext in SUPPORTED_EXTENSIONS:
                image_paths.append(os.path.join(root, f))
    return image_paths


def already_tagged(image_path):
    """Check if a .done marker exists for this image."""
    marker_path = image_path + "." + DONE_MARKER
    return os.path.exists(marker_path)


def mark_as_tagged(image_path):
    """Create a .done marker to avoid reprocessing."""
    marker_path = image_path + "." + DONE_MARKER
    log_action("MARK", marker_path)
    with open(marker_path, "w") as f:
        f.write("tagged")


def prepare_image(image_path):
    """Convert RAW to JPEG if needed, else return original path."""
    ext = os.path.splitext(image_path.lower())[1]
    if ext in RAW_EXTENSIONS:
        return convert_raw_to_jpg(image_path)
    elif ext in {".heic", ".heif"}:
        return convert_heic_to_jpeg(image_path)
    return image_path


def convert_raw_to_jpg(raw_path):
    """Convert RAW image to JPEG using rawpy + imageio."""
    with rawpy.imread(raw_path) as raw:
        rgb = raw.postprocess()

    tmp_dir = os.path.join(tempfile.gettempdir(), "metamark_previews")
    os.makedirs(tmp_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(raw_path))[0] + ".jpg"
    jpg_path = os.path.join(tmp_dir, base_name)

    imageio.imwrite(jpg_path, rgb, format="JPEG")
    log_action("CONVERT", jpg_path)
    return jpg_path
