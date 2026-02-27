from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import torch
import torch.nn as nn

from .siren import SirenConfig, SirenMLP
from .encoding import FourierEncoding, FourierEncodingConfig, MLP, MLPConfig


ModelType = Literal["siren", "fourier_mlp"]


@dataclass
class INRConfig:
    model: ModelType = "siren"

    # shared
    out_dim: int = 3

    # siren
    siren_hidden: int = 512
    siren_layers: int = 8
    siren_w0: float = 30.0
    siren_w0_hidden: float = 1.0

    # fourier+mlp
    ff_num_frequencies: int = 12
    ff_include_input: bool = True
    mlp_hidden: int = 512
    mlp_layers: int = 6
    mlp_activation: str = "gelu"


class INR(nn.Module):
    """Implicit neural representation wrapper."""

    def __init__(self, cfg: INRConfig):
        super().__init__()
        self.cfg = cfg

        if cfg.model == "siren":
            self.encoder = None
            self.net = SirenMLP(
                SirenConfig(
                    in_dim=2,
                    out_dim=cfg.out_dim,
                    hidden_dim=cfg.siren_hidden,
                    num_layers=cfg.siren_layers,
                    w0=cfg.siren_w0,
                    w0_hidden=cfg.siren_w0_hidden,
                    use_sigmoid_out=True,
                )
            )
        elif cfg.model == "fourier_mlp":
            self.encoder = FourierEncoding(
                FourierEncodingConfig(
                    in_dim=2,
                    num_frequencies=cfg.ff_num_frequencies,
                    include_input=cfg.ff_include_input,
                    log_space=True,
                )
            )
            self.net = MLP(
                MLPConfig(
                    in_dim=self.encoder.out_dim,
                    out_dim=cfg.out_dim,
                    hidden_dim=cfg.mlp_hidden,
                    num_layers=cfg.mlp_layers,
                    activation=cfg.mlp_activation,
                    use_sigmoid_out=True,
                )
            )
        else:
            raise ValueError(f"Unknown model type: {cfg.model}")

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        if self.encoder is not None:
            coords = self.encoder(coords)
        return self.net(coords)
