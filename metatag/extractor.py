import os
import requests
import base64
import time
from metatag import utils
from metatag.logger import log_action
from metatag.logger import get_logger

log = get_logger()
# PROMPT_PATH = os.getenv("METAMARK_PROMPT_PATH", "/config/prompts.txt")


def load_prompts(prompt_file=None):
    if not prompt_file:
        log.warning("⚠️ No prompt file provided to load_prompts()")
        return {}
    prompts = {}
    with open(prompt_file, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                prompts[key] = val
    if (
        "DEFAULT_KEYWORD_PROMPT" not in prompts
        or "DEFAULT_DESCRIPTION_PROMPT" not in prompts
    ):
        log.warning("⚠️ Missing expected keys in prompt file")
    return prompts


def infer_with_retry(image_path, prompt, model, ollama_url, timeout=240, retries=3):

    log.debug(f"🔍 Inferring with model: {model} at {ollama_url}")
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [encoded],
        "stream": False,
    }

    response = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json=payload,
                timeout=timeout,
            )
            if response.status_code != 200:
                log.warning(f"🟡 Attempt {attempt}: Status {response.status_code}")
                time.sleep(5)
                continue

            result = response.json().get("response", "").strip()
            if result:
                return result
            log.warning(f"🟡 Attempt {attempt}: Empty response")
        except Exception as e:
            log.error(f"🔴 Attempt {attempt} failed: {e}")
        time.sleep(5)

    return "No response generated after retries"


def generate_metadata(
    image_path, model, prompt_file=None, ollama_url=None, timeout=240
):
    prompts = load_prompts(prompt_file)
    jpg_path = utils.prepare_image(image_path)

    keywords_raw = infer_with_retry(
        jpg_path, prompts["DEFAULT_KEYWORD_PROMPT"], model, ollama_url, timeout
    )
    description = infer_with_retry(
        jpg_path, prompts["DEFAULT_DESCRIPTION_PROMPT"], model, ollama_url, timeout
    )

    keywords = [kw.strip() for kw in keywords_raw.split(",") if kw.strip()]

    return {
        "keywords": keywords,
        "description": description,
        "model": model,
        "prompt": prompts["DEFAULT_DESCRIPTION_PROMPT"],
    }
