from typing import NotRequired, Literal
from langchain.agents import AgentState
from pydantic import Field, BaseModel


class KnowledgeBaseAnswer(BaseModel):
    answer: str = Field(description="The synthesized answer to the user's question.")
    source: str = Field(description="Filename of the source document.")
    page: str = Field(description="Page number in the source document.")
    confidence: float = Field(
        description="Confidence score 0.0–1.0 based on the relevance scores of the search results used.",
    )


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
