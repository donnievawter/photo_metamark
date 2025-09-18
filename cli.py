import argparse
import os
from metatag.logger import setup_logger, get_logger
import metatag
import logging
import sys
import requests


def validate_ollama(ollama_url: str, model: str, timeout: int = 10, log=None):
    if not ollama_url:
        st = "❌ OLLAMA_URL is not set. Please provide --ollama-url or set the environment variable."
        print(st)
        log.error(st)
        sys.exit(1)

    response = None
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=timeout)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to reach Ollama at {ollama_url}: {e}")
        log.error(f"Failed to reach Ollama at {ollama_url}: {e}")
        sys.exit(1)

    try:
        tags = response.json().get("models", [])
    except requests.exceptions.JSONDecodeError:
        print(f"❌ Ollama responded with non-JSON content")
        log.error(f"Ollama responded with non-JSON content: {response.text}")
        sys.exit(1)

    available = [tag["name"] for tag in tags]
    if model not in available:
        print(
            f"❌ Model '{model}' not found in Ollama. Available models: {', '.join(available)}"
        )
        log.error(
            f"Model '{model}' not found in Ollama. Available models: {', '.join(available)}"
        )
        sys.exit(1)

    print(f"✅ Ollama is reachable at {ollama_url}")
    log.info(f"Ollama is reachable at {ollama_url}")
    print(f"✅ Model '{model}' is available")
    log.info(f"Model '{model}' is available")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="/input")
    parser.add_argument("--timeout", type=int, default=240, help="Timeout in seconds")
    parser.add_argument("--output", default="/output")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-dir", default="./logs", help="Directory to save logs")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    default_model = os.getenv("METAMARK_MODEL", "qwen2.5vl:3b")
    parser.add_argument(
        "--model", default=default_model, help="Model to use with Ollama"
    )

    parser.add_argument(
        "--prompt-file",
        default="prompts/default.txt",
        help="Path to prompt file for model guidance",
    )


    parser.add_argument(
        "--ollama-url",
        default=os.getenv("METAMARK_OLLAMA_URL", "http://host.docker.internal:11434"),
        help="URL for Ollama API. Can also be set via METAMARK_OLLAMA_URL env var.",
    )

    args = parser.parse_args()

    setup_logger(
        log_dir=args.log_dir, level=logging.DEBUG if args.verbose else logging.INFO
    )
    log = get_logger()
    log.info("🚀 Starting MetaMark")
    log.info(f"Using model: {args.model}")
    log.debug(f"Arguments: {vars(args)}")
    validate_ollama(args.ollama_url, args.model, args.timeout, log)

    from metatag import pipeline

    if args.watch:
        pipeline.run_watch(
            args.input,
            args.output,
            dry_run=args.dry_run,
            model=args.model,
            prompt_file=args.prompt_file,
            ollama_url=args.ollama_url,
            log=log,
            timeout=args.timeout,
        )
    else:
        pipeline.run_batch(
            args.input,
            args.output,
            dry_run=args.dry_run,
            model=args.model,
            prompt_file=args.prompt_file,
            ollama_url=args.ollama_url,
            log=log,
            timeout=args.timeout,
        )


if __name__ == "__main__":
    main()
