"""Load Anomaly Model."""

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from importlib import import_module
from typing import List, Union

from omegaconf import DictConfig, ListConfig
from torch import load

from anomalib.anomalib.models.cflow import Cflow
from anomalib.anomalib.models.components import AnomalyModule
from anomalib.anomalib.models.dfkde import Dfkde
from anomalib.anomalib.models.dfm import Dfm
from anomalib.anomalib.models.draem import Draem
from anomalib.anomalib.models.fastflow import Fastflow
from anomalib.anomalib.models.ganomaly import Ganomaly
from anomalib.anomalib.models.padim import Padim
from anomalib.anomalib.models.patchcore import Patchcore
from anomalib.anomalib.models.reverse_distillation import ReverseDistillation
from anomalib.anomalib.models.stfpm import Stfpm

__all__ = [
    "Cflow",
    "Dfkde",
    "Dfm",
    "Draem",
    "Fastflow",
    "Ganomaly",
    "Padim",
    "Patchcore",
    "ReverseDistillation",
    "Stfpm",
]

logger = logging.getLogger(__name__)


def _snake_to_pascal_case(model_name: str) -> str:
    """Convert model name from snake case to Pascal case.

    Args:
        model_name (str): Model name in snake case.

    Returns:
        str: Model name in Pascal case.
    """
    return "".join([split.capitalize() for split in model_name.split("_")])


def get_model(config: Union[DictConfig, ListConfig]) -> AnomalyModule:
    """Load model from the configuration file.

    Works only when the convention for model naming is followed.

    The convention for writing model classes is
    `anomalib.models.<model_name>.lightning_model.<ModelName>Lightning`
    `anomalib.models.stfpm.lightning_model.StfpmLightning`

    Args:
        config (Union[DictConfig, ListConfig]): Config.yaml loaded using OmegaConf

    Raises:
        ValueError: If unsupported model is passed

    Returns:
        AnomalyModule: Anomaly Model
    """
    logger.info("Loading the model.")

    model_list: List[str] = [
        "cflow",
        "dfkde",
        "dfm",
        "draem",
        "fastflow",
        "ganomaly",
        "padim",
        "patchcore",
        "reverse_distillation",
        "stfpm",
    ]
    model: AnomalyModule

    if config.model.name in model_list:
        module = import_module(f"anomalib.models.{config.model.name}")
        model = getattr(module, f"{_snake_to_pascal_case(config.model.name)}Lightning")(config)

    else:
        raise ValueError(f"Unknown model {config.model.name}!")

    if "init_weights" in config.keys() and config.init_weights:
        model.load_state_dict(load(os.path.join(config.project.path, config.init_weights))["state_dict"], strict=False)

    return model
