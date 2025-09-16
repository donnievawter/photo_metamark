import subprocess
import os
from datetime import datetime
from metatag.logger import log_action
from metatag.logger import get_logger

log = get_logger()

# EXIFTOOL_PATH = "/usr/local/bin/exiftool"  # Can be made configurable later


def embed_metadata(image_path, metadata, model="MetaMark"):
    keywords = metadata.get("keywords", [])
    description = metadata.get("description", "")
    prompt = metadata.get("prompt", None)

    args = [
        "exiftool",
        "-Headline=MetaMark Inference",
        f"-IPTC:Writer-Editor={model}",
        "-overwrite_original",
    ]

    for kw in keywords:
        args.append(f"-IPTC:Keywords={kw}")
        args.append(f"-XMP-dc:Subject={kw}")

    if description:
        args.append(f"-Description={description}")
    if prompt:
        args.append(f"-XMP-dc:Title={prompt}")

    args.append(image_path)

    try:
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL)
        log_action("TAG", image_path)
    except Exception as e:
        log.error(f"❌ Failed to tag {image_path}: {e}")
