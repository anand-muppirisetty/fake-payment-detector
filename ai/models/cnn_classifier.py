"""
Placeholder CNN-based image-manipulation classifier.

Project spec calls for a "CNN-based image classification (placeholder
architecture)" component. This module defines a small, real, trainable
PyTorch CNN (a shallow ResNet-style binary classifier: genuine vs
manipulated) so the architecture is genuine and swappable, but ships
WITHOUT pretrained weights, since no labeled dataset of real/fake UPI
screenshots is bundled with this project.

Behavior:
- If a trained weights file is found at MODEL_WEIGHTS_PATH, it is loaded
  and used for real inference.
- Otherwise, this falls back to a deterministic, transparent heuristic
  (based on classical CV statistics) so the pipeline still returns a
  usable, explainable "manipulation probability" out of the box, and logs
  clearly that it is running in placeholder/untrained mode.

To make this production-ready: collect a labeled dataset of genuine vs.
edited UPI screenshots, train via train.py (scaffold below), and drop the
resulting weights.pt file into ai/models/weights/.
"""
from __future__ import annotations

import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

MODEL_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights", "cnn_weights.pt")

_model = None
_model_load_attempted = False


class ManipulationCNN:
    """
    Small CNN architecture: 4 conv blocks + global average pool + FC head.
    Input: 224x224x3 RGB. Output: sigmoid probability of manipulation.

    Kept intentionally lightweight (suitable for CPU inference on a
    final-year project's hardware) while following a standard, real
    architecture pattern (Conv-BN-ReLU-Pool stacks) rather than a toy
    stub, so it is a genuine drop-in target for future training.
    """

    def __init__(self):
        import torch.nn as nn

        class _Net(nn.Module):
            def __init__(self):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
                    nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1),
                )
                self.classifier = nn.Sequential(
                    nn.Flatten(), nn.Linear(256, 64), nn.ReLU(), nn.Dropout(0.3),
                    nn.Linear(64, 1), nn.Sigmoid(),
                )

            def forward(self, x):
                return self.classifier(self.features(x))

        self.net = _Net()
        self.net.eval()

    def predict_proba(self, img_bgr: np.ndarray) -> float:
        import cv2
        import torch

        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224)).astype(np.float32) / 255.0
        tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            prob = float(self.net(tensor).item())
        return prob


def _heuristic_fallback_probability(img_bgr: np.ndarray) -> float:
    """
    Deterministic, explainable stand-in used when no trained weights exist.
    Combines a few cheap global statistics (noise variance, edge density,
    color-channel correlation) into a bounded pseudo-probability. This is
    NOT a trained model — it exists purely so the pipeline has a real
    number to blend with the rule-based forensic findings until the CNN is
    trained on a labeled dataset.
    """
    import cv2
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    noise = float(np.std(cv2.Laplacian(gray, cv2.CV_64F)))
    edges = cv2.Canny(gray, 80, 160)
    edge_density = float(np.mean(edges > 0))
    b, g, r = cv2.split(img_bgr.astype(np.float32))
    corr_bg = float(np.corrcoef(b.flatten(), g.flatten())[0, 1]) if b.size else 0.0

    score = 0.0
    score += 0.35 if noise > 45 else 0.0
    score += 0.25 if edge_density > 0.12 else 0.0
    score += 0.20 if corr_bg < 0.75 else 0.0
    score += 0.10  # small baseline uncertainty
    return float(np.clip(score, 0.0, 0.95))


def classify_manipulation_probability(img_bgr: np.ndarray) -> float:
    """Public entry point used by ai/forensics/analyzer.py."""
    global _model, _model_load_attempted

    if not _model_load_attempted:
        _model_load_attempted = True
        if os.path.exists(MODEL_WEIGHTS_PATH):
            try:
                import torch
                candidate = ManipulationCNN()
                candidate.net.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location="cpu"))
                _model = candidate
                logger.info("Loaded trained CNN weights from %s", MODEL_WEIGHTS_PATH)
            except Exception as exc:
                logger.warning("Failed to load CNN weights (%s); using heuristic fallback.", exc)
                _model = None
        else:
            logger.info(
                "No trained CNN weights found at %s — using explainable heuristic fallback. "
                "See ai/models/train.py to train a real classifier.", MODEL_WEIGHTS_PATH,
            )

    if _model is not None:
        try:
            return _model.predict_proba(img_bgr)
        except Exception as exc:  # pragma: no cover
            logger.warning("CNN inference failed (%s); using heuristic fallback.", exc)

    return _heuristic_fallback_probability(img_bgr)
