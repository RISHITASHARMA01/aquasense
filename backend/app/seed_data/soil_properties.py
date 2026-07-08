"""Soil hydraulic reference properties by texture class.

Field capacity (FC) and wilting point (WP) are volumetric water content
fractions (m3/m3), consistent with the ranges in FAO-56 Annex 8
("Saturation, field capacity and wilting point for different types of
soil"). Available water capacity per meter of soil = (FC - WP) * 1000 mm.

Basic infiltration rate (mm/hr) is a representative value used to convert
a recommended irrigation depth into an estimated sprinkler/flood run time;
drip systems are handled separately via emitter flow rate, not infiltration
rate, since drip wetting is localized rather than a uniform sheet.
"""

SOIL_PROPERTIES = [
    {
        "soil_type": "sandy",
        "field_capacity": 0.10,
        "wilting_point": 0.05,
        "infiltration_rate_mm_per_hr": 25.0,
    },
    {
        "soil_type": "sandy_loam",
        "field_capacity": 0.18,
        "wilting_point": 0.08,
        "infiltration_rate_mm_per_hr": 15.0,
    },
    {
        "soil_type": "loam",
        "field_capacity": 0.27,
        "wilting_point": 0.12,
        "infiltration_rate_mm_per_hr": 10.0,
    },
    {
        "soil_type": "clay_loam",
        "field_capacity": 0.31,
        "wilting_point": 0.17,
        "infiltration_rate_mm_per_hr": 5.0,
    },
    {
        "soil_type": "clay",
        "field_capacity": 0.38,
        "wilting_point": 0.24,
        "infiltration_rate_mm_per_hr": 2.0,
    },
]
