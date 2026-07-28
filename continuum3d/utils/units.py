"""Unit conversion tables and helpers."""
import gradio as gr

UNIT_TABLES = {
    "Length": {
        "m": 1.0, "km": 1e3, "cm": 1e-2, "mm": 1e-3,
        "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254,
    },
    "Mass": {
        "kg": 1.0, "g": 1e-3, "mg": 1e-6, "lb": 0.453592,
        "oz": 0.0283495, "ton (US)": 907.185,
    },
    "Temperature": {"\u00b0C": "C", "\u00b0F": "F", "K": "K"},
    "Force": {
        "N": 1.0, "kN": 1e3, "MN": 1e6, "lbf": 4.44822,
        "dyn": 1e-5, "kgf": 9.80665,
    },
    "Energy": {
        "J": 1.0, "kJ": 1e3, "MJ": 1e6, "cal": 4.184,
        "kcal": 4184.0, "Wh": 3600.0, "kWh": 3.6e6, "BTU": 1055.06,
    },
    "Pressure": {
        "Pa": 1.0, "kPa": 1e3, "MPa": 1e6, "bar": 1e5,
        "atm": 101325.0, "psi": 6894.76, "mmHg": 133.322,
    },
}


def _convert_temperature(value: float, from_u: str, to_u: str) -> float:
    celsius = value if from_u == "C" else (value - 32) * 5 / 9 if from_u == "F" else value - 273.15
    return celsius if to_u == "C" else celsius * 9 / 5 + 32 if to_u == "F" else celsius + 273.15


def unit_convert(value: float, category: str, from_u: str, to_u: str):
    """Universal unit conversion with formula string. Returns (result_str, formula_md)."""
    if category == "Temperature":
        result = _convert_temperature(value, from_u, to_u)
        formula = (
            f"**Result:** `{value} {from_u}` = `{result:.6g} {to_u}`\n\n"
            f"Temperature conversion uses offset-based formulas."
        )
        return str(result), formula
    tables = UNIT_TABLES.get(category, {})
    if from_u not in tables or to_u not in tables:
        return "0", "Invalid unit selection."
    base_val = value * tables[from_u]
    result = base_val / tables[to_u]
    factor = tables[from_u] / tables[to_u]
    formula = (
        f"**Result:** `{value} {from_u}` = `{result:.6g} {to_u}`\n\n"
        f"**Conversion Factor:** `1 {from_u} = {factor:.6g} {to_u}`\n\n"
        f"**Method:** Multiply by base unit equivalence: "
        f"`{value} \u00d7 {tables[from_u]:.6g} / {tables[to_u]:.6g}`"
    )
    return str(result), formula


def update_unit_dropdowns(category):
    """Update from/to dropdown choices when category changes."""
    units = list(UNIT_TABLES.get(category, {}).keys())
    return (
        gr.update(choices=units, value=units[0]),
        gr.update(choices=units, value=units[1] if len(units) > 1 else units[0]),
    )
