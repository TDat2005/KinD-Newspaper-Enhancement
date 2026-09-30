"""Retinex-inspired illumination correction for text-heavy page images.

This is a classical, lightweight approximation for a classroom demo. It is not
the trained KinD neural network from the linked paper.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from skimage import color, data, filters, util


def grayscale_float(image: np.ndarray) -> np.ndarray:
    """Convert a supported image array to grayscale float in [0, 1]."""
    values = np.asarray(image)
    if values.ndim == 3:
        values = util.img_as_float(values)
        if values.shape[2] == 4:
            values = color.rgba2rgb(values)
        else:
            values = values[..., :3]
        values = color.rgb2gray(values)
    else:
        values = util.img_as_float(values)
    return np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)


def sample_low_light_page() -> np.ndarray:
    """Return a reproducible, unevenly lit test page based on skimage's page sample."""
    page = grayscale_float(data.page())
    page = ndi.zoom(page, 3.0, order=3, mode="reflect").astype(np.float32)
    height, width = page.shape
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    xx /= max(width - 1, 1)
    yy /= max(height - 1, 1)

    illumination = 0.32 + 0.62 * (0.45 * xx + 0.55 * yy)
    shadow = 0.12 * np.exp(-(((xx - 0.82) ** 2) / 0.035 + ((yy - 0.24) ** 2) / 0.08))
    illumination = np.clip(illumination - shadow, 0.24, 0.96)

    rng = np.random.default_rng(42)
    sensor_noise = rng.normal(0.0, 0.012, size=page.shape).astype(np.float32)
    return np.clip(page * illumination + sensor_noise, 0.0, 1.0)


def gamma_baseline(image: np.ndarray, gamma: float = 0.55) -> np.ndarray:
    """Simple global brightening baseline; gamma < 1 brightens dark pixels."""
    gray = grayscale_float(image)
    return np.power(gray, max(float(gamma), 1e-3)).astype(np.float32)


def retinex_illumination_correction(
    image: np.ndarray,
    *,
    strength: float = 0.85,
    sigma_fraction: float = 0.12,
    target_paper_level: float = 0.92,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate smooth page lighting, divide it out, and lightly suppress noise.

    The slowly varying Gaussian estimate approximates illumination L; dividing
    the input by L leaves a reflectance-like image. A mild median blend reduces
    speckle without replacing the text strokes.
    """
    gray = grayscale_float(image)
    height, width = gray.shape
    sigma = max(3.0, min(height, width) * float(sigma_fraction))
    illumination = ndi.gaussian_filter(gray, sigma=sigma, mode="reflect")

    floor = max(0.035, float(np.quantile(illumination, 0.02)) * 0.5)
    safe_illumination = np.maximum(illumination, floor)
    corrected = gray / safe_illumination * float(target_paper_level)
    corrected = np.clip(corrected, 0.0, 1.0)

    denoised = ndi.median_filter(corrected, size=3, mode="reflect")
    corrected = 0.88 * corrected + 0.12 * denoised

    amount = float(np.clip(strength, 0.0, 1.0))
    result = (1.0 - amount) * gray + amount * corrected
    return np.clip(result, 0.0, 1.0).astype(np.float32), illumination.astype(np.float32)


def sauvola_binarize(image: np.ndarray, k: float = 0.20) -> np.ndarray:
    """Create a local black/white text view using Sauvola's threshold."""
    gray = grayscale_float(image)
    height, width = gray.shape
    shortest_side = min(height, width)
    max_odd_window = shortest_side if shortest_side % 2 else shortest_side - 1
    window = min(51, max_odd_window)
    window = max(3, window)
    if window % 2 == 0:
        window -= 1
    threshold = filters.threshold_sauvola(gray, window_size=window, k=float(k))
    return (gray > threshold).astype(np.float32)
