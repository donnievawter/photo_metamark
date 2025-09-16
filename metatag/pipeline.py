import os
import time
from metatag import extractor, tagger, utils
from pprint import pprint
from metatag.logger import log_action
from metatag.logger import get_logger

log = get_logger()


def run_batch(
    input_dir,
    output_dir,
    dry_run=False,
    model="qwen2.5vl:7b",
    prompt_file=None,
    ollama_url=None,
    log=None,
    timeout=240,
):
    log.info(f"📁 Running MetaMark in batch mode on: {input_dir}")
    image_paths = utils.find_images(input_dir)

    for path in image_paths:
        log.debug(f"path: {path}")
        if utils.already_tagged(path):
            log.debug(f"⏭️ Already tagged, skipping: {path}")
            continue

        jpg_path = utils.prepare_image(path)
        metadata = extractor.generate_metadata(
            jpg_path, model, prompt_file, ollama_url, timeout
        )
        dest_path = utils.get_dest_path(path, output_dir, dry_run)

        if dry_run:
            log.info(f"📝 [DRY RUN] Would tag: {path}")
            log.info(f"     → Keywords: {metadata.get('keywords')}")
            log.info(f"     → Description: {metadata.get('description')}")
        else:
            tagger.embed_metadata(dest_path, metadata)
            utils.mark_as_tagged(path)

    log.info("✅ Batch processing complete.")


def run_watch(
    input_dir,
    output_dir,
    dry_run=False,
    model="qwen2.5vl:7b",
    prompt_file=None,
    ollama_url=None,
    log=None,
    timeout=240,
    poll_interval=5,
):
    log.info(f"👀 Watching folder: {input_dir}")
    seen = set()

    while True:
        image_paths = utils.find_images(input_dir)
        new_files = [p for p in image_paths if p not in seen]

        for path in new_files:
            log.debug(f"New file detected: {path}")
            if utils.already_tagged(path):
                log.debug(f"⏭️ Already tagged, skipping: {path}")
                continue

            jpg_path = utils.prepare_image(path)
            metadata = extractor.generate_metadata(
                jpg_path, model, prompt_file, ollama_url, timeout
            )
            dest_path = utils.get_dest_path(path, output_dir, dry_run)

            if dry_run:
                log.info(f"[DRY-RUN] Metadata for {path}:")
                pprint.pprint(metadata, width=100)
            else:
                tagger.embed_metadata(dest_path, metadata)
                utils.mark_as_tagged(path)
            log.debug(f"Marking as seen: {path}")
            seen.add(path)

        time.sleep(poll_interval)
