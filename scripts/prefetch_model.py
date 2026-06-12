from __future__ import annotations

import os
from pathlib import Path


REQUIRED_ENV_VARS = ("MT_MODEL", "MODEL_CACHE_DIR")


def read_prefetch_config() -> tuple[str, Path]:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): " + ", ".join(missing)
        )

    return (os.environ["MT_MODEL"], Path(os.environ["MODEL_CACHE_DIR"]))


def main() -> None:
    model_id, cache_dir = read_prefetch_config()
    cache_dir.mkdir(parents=True, exist_ok=True)

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    print(f"Prefetching tokenizer and model '{model_id}' into '{cache_dir}'")
    AutoTokenizer.from_pretrained(model_id, cache_dir=str(cache_dir))
    AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=str(cache_dir))
    print("Model prefetch complete")


if __name__ == "__main__":
    main()
