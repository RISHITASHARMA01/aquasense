"""Crop coefficient (Kc) reference data, conceptually sourced from FAO-56
(Allen et al., 1998), Chapter 6 tables and Table 11 (stage lengths).

Each entry stores:
  - kc: [Kc_ini, Kc_mid, Kc_end] — the three FAO-56 reference coefficients.
    Kc during the "development" stage is linearly interpolated between
    Kc_ini and Kc_mid; Kc during "late" is linearly interpolated between
    Kc_mid and Kc_end. This mirrors the FAO-56 crop coefficient curve
    rather than treating Kc as a flat step function per stage.
  - stage_lengths_days: [initial, development, mid, late] in days. These
    are representative example lengths for a sub-humid climate (FAO-56
    Table 11) — actual lengths vary by climate/cultivar/planting date,
    which is a known simplification for this project (flagged in README).
  - root_depth_m: maximum effective rooting depth (FAO-56 Table 22).
  - depletion_fraction_p: fraction of TAW that can be depleted before
    water stress (FAO-56 Table 22), used to compute readily available
    water (RAW = p * TAW).
"""

CROP_COEFFICIENTS = [
    {
        "name": "Maize (grain)",
        "kc": [0.3, 1.2, 0.35],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [20, 35, 40, 30],
        "root_depth_m": 1.35,
        "depletion_fraction_p": 0.55,
    },
    {
        "name": "Wheat (spring)",
        "kc": [0.3, 1.15, 0.4],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [15, 30, 65, 40],
        "root_depth_m": 1.25,
        "depletion_fraction_p": 0.55,
    },
    {
        "name": "Rice",
        "kc": [1.05, 1.2, 0.9],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [30, 30, 60, 30],
        "root_depth_m": 0.75,
        "depletion_fraction_p": 0.2,
    },
    {
        "name": "Tomato",
        "kc": [0.6, 1.15, 0.8],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [30, 40, 40, 25],
        "root_depth_m": 1.1,
        "depletion_fraction_p": 0.4,
    },
    {
        "name": "Potato",
        "kc": [0.5, 1.15, 0.75],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [25, 30, 45, 30],
        "root_depth_m": 0.5,
        "depletion_fraction_p": 0.35,
    },
    {
        "name": "Cotton",
        "kc": [0.35, 1.18, 0.6],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [30, 50, 55, 45],
        "root_depth_m": 1.35,
        "depletion_fraction_p": 0.65,
    },
    {
        "name": "Soybean",
        "kc": [0.4, 1.15, 0.5],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [20, 30, 60, 25],
        "root_depth_m": 0.95,
        "depletion_fraction_p": 0.5,
    },
    {
        "name": "Sugarcane",
        "kc": [0.4, 1.25, 0.75],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [30, 50, 180, 60],
        "root_depth_m": 1.6,
        "depletion_fraction_p": 0.65,
    },
    {
        "name": "Onion (dry)",
        "kc": [0.7, 1.05, 0.75],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [15, 25, 70, 40],
        "root_depth_m": 0.45,
        "depletion_fraction_p": 0.3,
    },
    {
        "name": "Lettuce",
        "kc": [0.7, 1.0, 0.95],
        "stages": ["initial", "development", "mid", "late"],
        "stage_lengths_days": [20, 30, 15, 10],
        "root_depth_m": 0.4,
        "depletion_fraction_p": 0.3,
    },
]
