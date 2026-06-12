from __future__ import annotations

import logging


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )

