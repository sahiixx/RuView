"""
Shared test fixtures for WiFi-DensePose test suite.

Provides default configurations for hardware, CSI processing, and pose
estimation components so that tests can run without real hardware.

Added by Manus AI agent during E2E pipeline validation (2026-03-12).
"""

import pytest


@pytest.fixture
def router_config():
    """Default router configuration for tests (no real hardware needed)."""
    return {
        "host": "192.168.1.1",
        "port": 22,
        "username": "admin",
        "password": "test-password",
        "interface": "wlan0",
    }


@pytest.fixture
def csi_processor_config():
    """Default CSI processor configuration for tests."""
    return {
        "sampling_rate": 100,
        "window_size": 56,
        "overlap": 0.5,
        "noise_threshold": -60,
    }


@pytest.fixture
def phase_sanitizer_config():
    """Default phase sanitizer configuration for tests."""
    return {
        "sampling_rate": 100,
        "noise_threshold": -60,
        "unwrap_method": "numpy",
    }


@pytest.fixture
def densepose_config():
    """Default DensePose head configuration for tests."""
    return {
        "input_channels": 64,
        "hidden_channels": [128, 256, 512],
        "output_channels": 256,
        "num_keypoints": 17,
        "num_body_parts": 24,
        "num_uv_coordinates": 2,
        "use_attention": True,
    }


@pytest.fixture
def modality_translation_config():
    """Default modality translation network configuration for tests."""
    return {
        "input_channels": 64,
        "hidden_channels": [128, 256, 512],
        "output_channels": 256,
        "use_attention": True,
    }


@pytest.fixture
def mock_csi_data():
    """Generate synthetic CSI data for testing."""
    import numpy as np

    np.random.seed(42)
    num_frames = 100
    num_subcarriers = 56
    num_antennas = 3

    amplitude = np.random.rand(num_frames, num_subcarriers, num_antennas).astype(
        np.float32
    )
    phase = (np.random.rand(num_frames, num_subcarriers, num_antennas) * 2 * np.pi - np.pi).astype(
        np.float32
    )

    return {
        "amplitude": amplitude,
        "phase": phase,
        "num_frames": num_frames,
        "num_subcarriers": num_subcarriers,
        "num_antennas": num_antennas,
        "sampling_rate": 100,
    }
