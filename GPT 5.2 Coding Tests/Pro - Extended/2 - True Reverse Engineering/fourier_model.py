import math
from dataclasses import dataclass
from typing import Dict, Any

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class ModelConfig:
    k_max: int = 24
    timewarp_j: int = 3

    # Parameter clamps (tanh-scaled)
    trans_max: float = 0.55
    timewarp_max: float = 0.35

    # Scale mapping
    scale_min: float = 0.20
    scale_max: float = 1.60


class FourierCurveBatch(nn.Module):
    """B independent Fourier curves optimized in parallel.

    Curve:
      x(t) = Σ_{k=1..K} [ax_cos[k] cos(k t') + ax_sin[k] sin(k t')]
      y(t) = Σ_{k=1..K} [ay_cos[k] cos(k t') + ay_sin[k] sin(k t')]

    with a generic time warp:
      t' = t + Σ_{j=1..J} (tw_sin[j] sin(j t) + tw_cos[j] cos(j t))

    then a global similarity transform:
      [x;y] = scale * R(rot) * [x;y] + trans

    All coordinates are in normalized image space [-1,1].
    """

    def __init__(self, batch: int, cfg: ModelConfig, device: torch.device, dtype: torch.dtype = torch.float32):
        super().__init__()
        self.batch = batch
        self.cfg = cfg

        k = cfg.k_max
        j = cfg.timewarp_j

        # Fourier coefficients
        self.ax_cos = nn.Parameter(torch.zeros(batch, k, device=device, dtype=dtype))
        self.ax_sin = nn.Parameter(torch.zeros(batch, k, device=device, dtype=dtype))
        self.ay_cos = nn.Parameter(torch.zeros(batch, k, device=device, dtype=dtype))
        self.ay_sin = nn.Parameter(torch.zeros(batch, k, device=device, dtype=dtype))

        # Global transform
        self.scale_raw = nn.Parameter(torch.zeros(batch, 1, device=device, dtype=dtype))
        self.rot_raw = nn.Parameter(torch.zeros(batch, 1, device=device, dtype=dtype))
        self.trans_raw = nn.Parameter(torch.zeros(batch, 2, device=device, dtype=dtype))

        # Time-warp coefficients
        self.tw_sin_raw = nn.Parameter(torch.zeros(batch, j, device=device, dtype=dtype))
        self.tw_cos_raw = nn.Parameter(torch.zeros(batch, j, device=device, dtype=dtype))

    def randomize_(self, seed: int = 0) -> None:
        """Reasonable random initialization for multi-start."""
        g = torch.Generator(device=self.ax_cos.device)
        g.manual_seed(seed)

        # Start smooth: higher frequencies small.
        k = torch.arange(1, self.cfg.k_max + 1, device=self.ax_cos.device, dtype=self.ax_cos.dtype)
        decay = (1.0 / (k ** 1.3))[None, :]

        def rnd(shape, scale):
            return torch.randn(*shape, generator=g, device=self.ax_cos.device, dtype=self.ax_cos.dtype) * scale

        base = 0.22
        self.ax_cos.data = rnd(self.ax_cos.shape, base) * decay
        self.ax_sin.data = rnd(self.ax_sin.shape, base) * decay
        self.ay_cos.data = rnd(self.ay_cos.shape, base) * decay
        self.ay_sin.data = rnd(self.ay_sin.shape, base) * decay

        # Random rotation, small translation, moderate scale.
        self.rot_raw.data = rnd(self.rot_raw.shape, 0.9)
        self.trans_raw.data = rnd(self.trans_raw.shape, 0.35)
        self.scale_raw.data = rnd(self.scale_raw.shape, 0.5)

        # Small time warp
        self.tw_sin_raw.data = rnd(self.tw_sin_raw.shape, 0.35)
        self.tw_cos_raw.data = rnd(self.tw_cos_raw.shape, 0.35)

    def _map_params(self):
        # scale in [scale_min, scale_max]
        s = torch.sigmoid(self.scale_raw)
        scale = self.cfg.scale_min + (self.cfg.scale_max - self.cfg.scale_min) * s

        # rot in [-pi, pi]
        rot = torch.tanh(self.rot_raw) * math.pi

        # trans in [-trans_max, trans_max]
        trans = torch.tanh(self.trans_raw) * self.cfg.trans_max

        # time warp in [-timewarp_max, timewarp_max]
        tw_sin = torch.tanh(self.tw_sin_raw) * self.cfg.timewarp_max
        tw_cos = torch.tanh(self.tw_cos_raw) * self.cfg.timewarp_max
        return scale, rot, trans, tw_sin, tw_cos

    def forward(self, t: torch.Tensor, k_active: int) -> torch.Tensor:
        """Return points [B, N, 2] for a given time grid t (shape [N])."""
        assert t.ndim == 1
        B = self.batch
        N = t.shape[0]

        scale, rot, trans, tw_sin, tw_cos = self._map_params()

        # Build warped time t' in a vectorized way.
        if self.cfg.timewarp_j > 0:
            j = torch.arange(1, self.cfg.timewarp_j + 1, device=t.device, dtype=t.dtype)[:, None]  # [J,1]
            jt = j * t[None, :]  # [J,N]
            sin_jt = torch.sin(jt)
            cos_jt = torch.cos(jt)
            # (B,J) @ (J,N) -> (B,N)
            warp = tw_sin @ sin_jt + tw_cos @ cos_jt
            tp = t[None, :] + warp
        else:
            tp = t[None, :].expand(B, N)

        K = k_active
        k = torch.arange(1, K + 1, device=t.device, dtype=t.dtype)[None, :, None]  # [1,K,1]
        ang = tp[:, None, :] * k  # [B,K,N]
        cos_k = torch.cos(ang)
        sin_k = torch.sin(ang)

        axc = self.ax_cos[:, :K, None]
        axs = self.ax_sin[:, :K, None]
        ayc = self.ay_cos[:, :K, None]
        ays = self.ay_sin[:, :K, None]

        x_raw = (axc * cos_k + axs * sin_k).sum(dim=1)  # [B,N]
        y_raw = (ayc * cos_k + ays * sin_k).sum(dim=1)

        cr = torch.cos(rot)  # [B,1]
        sr = torch.sin(rot)

        x = scale * (x_raw * cr + (-y_raw) * sr) + trans[:, 0:1]
        y = scale * (x_raw * sr + y_raw * cr) + trans[:, 1:2]

        return torch.stack([x, y], dim=-1)  # [B,N,2]

    @torch.no_grad()
    def export_one(self, idx: int, k_active: int) -> Dict[str, Any]:
        """Export a single candidate's parameters to JSON-serializable dict."""
        scale, rot, trans, tw_sin, tw_cos = self._map_params()
        out = {
            "k_active": int(k_active),
            "k_max": int(self.cfg.k_max),
            "timewarp_j": int(self.cfg.timewarp_j),
            "ax_cos": self.ax_cos[idx, :k_active].detach().cpu().tolist(),
            "ax_sin": self.ax_sin[idx, :k_active].detach().cpu().tolist(),
            "ay_cos": self.ay_cos[idx, :k_active].detach().cpu().tolist(),
            "ay_sin": self.ay_sin[idx, :k_active].detach().cpu().tolist(),
            "scale": float(scale[idx].item()),
            "rot_rad": float(rot[idx].item()),
            "trans": trans[idx].detach().cpu().tolist(),
            "timewarp_sin": tw_sin[idx].detach().cpu().tolist(),
            "timewarp_cos": tw_cos[idx].detach().cpu().tolist(),
        }
        return out
