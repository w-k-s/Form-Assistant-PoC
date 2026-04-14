from typing import NotRequired, Literal
from langchain.agents import AgentState

FormStep = Literal[
    "emirate_collector",
    "car_make_collector",
    "car_model_collector",
    "car_year_collector",
    "number_of_accidents_collector",
    "print_premiun",
]


class InsuranceFormState(AgentState):
    current_step: NotRequired[FormStep]
    emirate: NotRequired[
        Literal[
            "Abu Dhabi", "Dubai", "Sharjah", "RAK", "Ajman", "Fujairah", "Umm Al-Quwaim"
        ]
    ]
    car_make: NotRequired[str]
    car_model: NotRequired[str]
    car_year: NotRequired[int]
    number_of_accidents: NotRequired[int]
    premium: NotRequired[str]
