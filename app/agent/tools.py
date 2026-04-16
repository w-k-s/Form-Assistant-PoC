import csv
import difflib
import structlog
from importlib.resources import files
from app.services.premium import calculate_premium as _calculate_premium
from typing import Literal, List
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from app.agent.models import InsuranceFormState
from langgraph.types import Command

log = structlog.get_logger(__name__)

# Load car model data once at module init.
# Structure: { (make_lower, model_lower): (start_year, end_year) }
_CAR_MODELS: dict[tuple[str, str], tuple[int, int]] = {}

with (files("app.resources") / "car_models.csv").open(newline="", encoding="utf-8") as _f:
    for row in csv.DictReader(_f):
        key = (row["make"].strip().lower(), row["model"].strip().lower())
        _CAR_MODELS[key] = (int(row["start_year"]), int(row["end_year"]))

VALID_EMIRATES = [
    "Dubai",
    "Abu Dhabi",
    "Sharjah",
    "Umm AlQuwaim",
    "Fujairah",
    "Ras Al-Khaimah",
]

VALID_EMIRATES_LOWER = [e.lower() for e in VALID_EMIRATES]


@tool
def validate_emirate(
    emirate: str,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> List[str]:
    """Validates emirate.Returns a list of validation errors. An empty"""
    # Should do fuzzy matching
    result = []
    if not emirate.lower() in VALID_EMIRATES_LOWER:
        result = [
            f"{emirate} is not a recognised emirate. Please enter one of {VALID_EMIRATES}"
        ]

    log.info(f"validate_emirate", emirate=emirate, result=result)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=result,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "emirate": emirate,
            "current_step": "car_make_collector",
        }
    )


@tool
def record_emirate(
    emirate: str,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Record the customer's emirate and transition to make collection."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Emirate recorded as: {emirate}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "emirate": emirate,
            "current_step": "car_make_collector",
        }
    )


@tool
def record_car_make(
    car_make: str,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Record the customer's car make and transition to model collector."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Make recorded as: {car_make}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "car_make": car_make,
            "current_step": "car_model_collector",
        }
    )


@tool
def record_car_model(
    car_model: str,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Record the customer's car model and transition to year collector."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Model recorded as: {car_model}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "car_model": car_model,
            "current_step": "car_year_collector",
        }
    )


@tool
def validate_year_of_manufacture(
    car_make: str,
    car_model: str,
    car_year: int,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> List[str]:
    """Validates the year of manufacture. If invalid, returns validation errors as an array. If valid, an empty array is returned"""
    result = []
    make_lower = car_make.strip().lower()
    model_lower = car_model.strip().lower()

    # Try exact match first, then fuzzy match on the combined "make model" string.
    key = (make_lower, model_lower)
    if key not in _CAR_MODELS:
        all_keys = list(_CAR_MODELS.keys())
        combined_lookup = f"{make_lower} {model_lower}"
        combined_keys = [f"{m} {mod}" for m, mod in all_keys]
        matches = difflib.get_close_matches(
            combined_lookup, combined_keys, n=1, cutoff=0.6
        )
        if matches:
            matched_make, matched_model = matches[0].split(" ", 1)
            key = (matched_make, matched_model)

    if key in _CAR_MODELS:
        start_year, end_year = _CAR_MODELS[key]
        if car_year < start_year or car_year > end_year:
            result = [
                f"{car_make} {car_model} was not manufactured in {car_year}. "
                f"Valid range is {start_year}–{end_year}."
            ]
    # If still not found, let it slide — unrecognised make/model is not an error.
    log.info(
        f"validate_year_of_manufacture",
        car_make=car_make,
        car_model=car_model,
        car_year=car_year,
        result=result,
    )
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=result,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def record_car_year(
    car_year: int,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Record the customer's car year and transition to number of accidents collector."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Year recorded as: {car_year}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "car_year": car_year,
            "current_step": "number_of_accidents_collector",
        }
    )


@tool
def record_number_of_accidents(
    number_of_accidents: int,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Record the customer's car number of accident and transition to print_premium."""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Number of accidents recorded as: {number_of_accidents}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "number_of_accidents": number_of_accidents,
            "current_step": "print_premium",
        }
    )


@tool
def calculate_premium(
    emirate: str,
    car_make: str,
    car_model: str,
    car_year: int,
    number_of_accidents: int,
    runtime: ToolRuntime[None, InsuranceFormState],
) -> Command:
    """Calculate the customer's insurance premium and transition to print premium step."""
    premium = _calculate_premium(
        emirate, car_make, car_model, car_year, number_of_accidents
    )
    log.info(
        f"calculate_premium",
        car_make=car_make,
        car_model=car_model,
        car_year=car_year,
        number_of_accidents=number_of_accidents,
        premium=premium,
    )
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Calculated premium recorded as: {premium}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "premium": premium,
            "current_step": "print_premium",
        }
    )


@tool
def print_premium(
    premium: str,
) -> str:
    """Print the customer's premium."""
    return f"The calculated premium for your car is: {premium}"
