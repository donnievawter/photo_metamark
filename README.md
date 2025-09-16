# 📷 MetaMark: Local Photo Tagging with LLMs

MetaMark is a lightweight tool for tagging and enriching your photos using local language models. It runs entirely on your machine—no cloud, no upload, no nonsense.

---

## 🧩 What MetaMark Does

- Reads your image folder
- Uses a local LLM (via [Ollama](https://ollama.com)) to generate semantic tags
- Outputs metadata in a clean, inspectable format
- Designed for photographers, archivists, and curious humans

---

## ⚙️ Requirements

To use MetaMark, you **must** have:

- A machine capable of running [Ollama](https://ollama.com) (8GB+ RAM recommended)
- [Docker](https://www.docker.com) installed
- A folder of images you want to tag

---

## 🚀 Quickstart (Photographers)

1. Make sure [Docker](https://www.docker.com) is installed and running.

2. Pull the MetaMark image from GitHub Container Registry:

```
docker pull ghcr.io/donnievawter/photo_metamark/metamark:latest
```

3. Run MetaMark using the provided wrapper script:
    From a terminal:

```
curl -O https://raw.githubusercontent.com/donnievawter/photo_metamark/main/metamark.sh
chmod +x metamark.sh
bash metamark.sh ~/Pictures ~/PicturesOut


```

This will process all images in `~/Pictures` and write results to `~/PicturesOut`.

To continuously watch for new images:

```
bash metamark.sh ~/Pictures ~/PicturesOut --watch
```

---

## 🧑‍💻 Quickstart (Techies)

1. Clone the repo:

```
git clone https://github.com/donnievawter/photo_metamark.git
cd photo_metamark
```

2. Build the image:

```
docker build -t metamark -f docker/Dockerfile.slim .
```

3. Run the container:

```
docker run --rm \
  -v ~/Pictures:/input \
  -v ~/PicturesOut:/output \
  -v $(pwd)/prompts:/prompts \
  metamark \
  /entrypoint.sh --input /input --output /output
```

---

## 🔁 Watch Mode

By default, MetaMark processes all images in the input folder once.

To continuously watch the folder for new images:

```
/entrypoint.sh --input /input --output /output --watch
```

---

## 🧪 CLI Arguments

MetaMark supports the following flags:

```
--input         Path to input folder (default: /input)
--output        Path to output folder (default: /output)
--timeout       Timeout in seconds for model response (default: 240)
--watch         Watch input folder for new files
--dry-run       Run without writing output
--log-dir       Directory to save logs (default: ./logs)
--verbose       Enable verbose logging
--model         Model to use with Ollama (default: qwen2.5vl:7b or $METAMARK_MODEL)
--prompt-file   Path to prompt file (default: prompts/default.txt)
--ollama-url    URL for Ollama API (default: http://localhost:11434)
```

---

## 🧠 Philosophy

MetaMark is local-first, restart-safe, and modular. It doesn’t phone home, doesn’t require cloud APIs, and doesn’t assume you want to share your photos with anyone but future-you.

---

## 🛠️ Notes

- This repo does **not** include any server references or token logic
- Ollama must be running **outside** the container
- For Windows users: Docker Desktop works fine, but you’ll need to adjust paths
- To customize prompts, mount your own folder with `-v /your/prompts:/prompts` and pass `--prompt-file /prompts/custom.txt`

---

## 📬 Feedback

If you have questions, ideas, or want to contribute, open an issue or reach out. MetaMark is built to empower—not overwhelm.
