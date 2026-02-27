from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import torch
import torch.nn as nn


class Sine(nn.Module):
    def __init__(self, w0: float = 1.0):
        super().__init__()
        self.w0 = float(w0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sin(self.w0 * x)


def siren_init_first(layer: nn.Linear, w0: float, in_features: int) -> None:
    # SIREN first-layer init
    with torch.no_grad():
        bound = 1.0 / in_features
        layer.weight.uniform_(-bound, bound)
        layer.bias.uniform_(-bound, bound)


def siren_init(layer: nn.Linear, w0: float, in_features: int) -> None:
    # SIREN hidden-layer init
    with torch.no_grad():
        bound = math.sqrt(6.0 / in_features) / w0
        layer.weight.uniform_(-bound, bound)
        layer.bias.uniform_(-bound, bound)


@dataclass
class SirenConfig:
    in_dim: int = 2
    out_dim: int = 3
    hidden_dim: int = 512
    num_layers: int = 8  # includes first + hidden, excludes output
    w0: float = 30.0
    w0_hidden: float = 1.0
    use_sigmoid_out: bool = True


class SirenMLP(nn.Module):
    """SIREN MLP for implicit neural representations."""

    def __init__(self, cfg: SirenConfig):
        super().__init__()
        self.cfg = cfg

        layers: List[nn.Module] = []

        # First layer
        first = nn.Linear(cfg.in_dim, cfg.hidden_dim)
        siren_init_first(first, cfg.w0, cfg.in_dim)
        layers.append(first)
        layers.append(Sine(cfg.w0))

        # Hidden layers
        for _ in range(cfg.num_layers - 1):
            lin = nn.Linear(cfg.hidden_dim, cfg.hidden_dim)
            siren_init(lin, cfg.w0_hidden, cfg.hidden_dim)
            layers.append(lin)
            layers.append(Sine(cfg.w0_hidden))

        self.net = nn.Sequential(*layers)

        self.final = nn.Linear(cfg.hidden_dim, cfg.out_dim)
        # Final layer init (use smaller init for stability)
        with torch.no_grad():
            bound = math.sqrt(6.0 / cfg.hidden_dim) / cfg.w0_hidden
            self.final.weight.uniform_(-bound, bound)
            self.final.bias.uniform_(-bound, bound)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.net(x)
        out = self.final(h)
        if self.cfg.use_sigmoid_out:
            out = torch.sigmoid(out)
        return out
