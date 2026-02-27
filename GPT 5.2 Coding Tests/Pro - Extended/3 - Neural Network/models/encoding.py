from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn


@dataclass
class FourierEncodingConfig:
    in_dim: int = 2
    num_frequencies: int = 10
    include_input: bool = True
    log_space: bool = True


class FourierEncoding(nn.Module):
    """Positional encoding similar to NeRF.

    Encodes x into: [x, sin(2^k * pi x), cos(2^k * pi x), ...]
    """

    def __init__(self, cfg: FourierEncodingConfig):
        super().__init__()
        self.cfg = cfg
        if cfg.log_space:
            freqs = 2.0 ** torch.arange(cfg.num_frequencies)
        else:
            freqs = torch.linspace(1.0, 2.0 ** (cfg.num_frequencies - 1), cfg.num_frequencies)
        self.register_buffer("freqs", freqs, persistent=False)

    @property
    def out_dim(self) -> int:
        base = self.cfg.in_dim if self.cfg.include_input else 0
        # for each freq, sin and cos per input dim
        return base + (2 * self.cfg.num_frequencies * self.cfg.in_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (..., in_dim)
        xb = x
        # (..., num_freq, in_dim)
        x_exp = xb.unsqueeze(-2) * self.freqs.view(1, -1, 1) * math.pi
        sin = torch.sin(x_exp)
        cos = torch.cos(x_exp)
        enc = torch.cat([sin, cos], dim=-1).flatten(-2)
        if self.cfg.include_input:
            return torch.cat([xb, enc], dim=-1)
        return enc


@dataclass
class MLPConfig:
    in_dim: int
    out_dim: int = 3
    hidden_dim: int = 512
    num_layers: int = 6
    activation: str = "relu"  # relu | gelu
    use_sigmoid_out: bool = True


class MLP(nn.Module):
    def __init__(self, cfg: MLPConfig):
        super().__init__()
        self.cfg = cfg
        act: nn.Module
        if cfg.activation == "relu":
            act = nn.ReLU(inplace=True)
        elif cfg.activation == "gelu":
            act = nn.GELU()
        else:
            raise ValueError(f"Unknown activation: {cfg.activation}")

        layers = []
        dim = cfg.in_dim
        for _ in range(cfg.num_layers):
            layers.append(nn.Linear(dim, cfg.hidden_dim))
            layers.append(act)
            dim = cfg.hidden_dim
        self.body = nn.Sequential(*layers)
        self.head = nn.Linear(cfg.hidden_dim, cfg.out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.body(x)
        out = self.head(h)
        if self.cfg.use_sigmoid_out:
            out = torch.sigmoid(out)
        return out
