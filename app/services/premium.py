"""Insurance premium calculation logic."""

# Base annual premiums by emirate (AED).
# Dubai and Abu Dhabi carry higher premiums due to traffic density and repair costs.
_EMIRATE_BASE: dict[str, float] = {
    "dubai": 2800,
    "abu dhabi": 2600,
    "sharjah": 2200,
    "ras al-khaimah": 1900,
    "fujairah": 1800,
    "umm alquwaim": 1700,
    "ajman": 1700,
}
_EMIRATE_BASE_DEFAULT = 2000

# Make-level multipliers — luxury / high-performance brands cost more to repair.
_MAKE_MULTIPLIER: dict[str, float] = {
    "rolls-royce": 3.5,
    "bentley": 3.2,
    "lamborghini": 3.0,
    "ferrari": 3.0,
    "maserati": 2.5,
    "porsche": 2.2,
    "land rover": 2.0,
    "bmw": 1.8,
    "mercedes-benz": 1.8,
    "audi": 1.7,
    "lexus": 1.5,
    "genesis": 1.4,
    "cadillac": 1.4,
    "infiniti": 1.3,
    "tesla": 1.3,
    "ford": 1.1,
    "chevrolet": 1.1,
    "jeep": 1.1,
    "dodge": 1.1,
}
_MAKE_MULTIPLIER_DEFAULT = 1.0

# Vehicle age factor — newer cars cost more to insure (higher value / repair cost),
# older cars attract a flat uplift for parts availability.
def _age_factor(car_year: int, current_year: int = 2026) -> float:
    age = current_year - car_year
    if age <= 1:
        return 1.30   # brand new
    elif age <= 3:
        return 1.20
    elif age <= 5:
        return 1.10
    elif age <= 10:
        return 1.00   # sweet spot
    elif age <= 15:
        return 1.05   # parts getting scarcer
    else:
        return 1.15   # classic / hard-to-source parts


# Accident loading — each at-fault claim raises risk profile.
def _accident_loading(number_of_accidents: int) -> float:
    if number_of_accidents == 0:
        return 0.90   # no-claims discount
    elif number_of_accidents == 1:
        return 1.15
    elif number_of_accidents == 2:
        return 1.40
    elif number_of_accidents == 3:
        return 1.75
    else:
        return 2.20   # high risk


def calculate_premium(
    emirate: str,
    car_make: str,
    car_model: str,
    car_year: int,
    number_of_accidents: int,
) -> str:
    base = _EMIRATE_BASE.get(emirate.strip().lower(), _EMIRATE_BASE_DEFAULT)
    make_mult = _MAKE_MULTIPLIER.get(car_make.strip().lower(), _MAKE_MULTIPLIER_DEFAULT)
    age_mult = _age_factor(car_year)
    accident_mult = _accident_loading(number_of_accidents)

    total = base * make_mult * age_mult * accident_mult

    # Round to nearest 50 AED to look like a real quote.
    rounded = round(total / 50) * 50
    return f"AED {rounded:,.0f}"
