from typing import Literal
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from app.agent.models import InsuranceFormState
from langgraph.types import Command


@tool
def record_emirate(
    emirate: Literal[
        "Abu Dhabi", "Dubai", "Sharjah", "RAK", "Ajman", "Fujairah", "Umm Al-Quwaim"
    ],
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
    premium = "AED 1000"
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Calculated premium recorded as: premium",
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
