import os
import asyncio
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    input_guardrail,
    TResponseInputItem,
    RunContextWrapper,
)
from pydantic import BaseModel
from typing import List, Optional
from prompt_utils import *


# Load environment variables from .env file
load_dotenv()

# Access your API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")


# Pydantic model for structured output
# This model defines the expected structure of the output from the agent.
class Metadata(BaseModel):
    topics: Optional[List[str]] = None
    dates: Optional[List[str]] = None
    products: Optional[List[str]] = None
    order_number: Optional[str] = None
    requested_action: Optional[str] = None
    sentiment: Optional[str] = None
    urgency: Optional[str] = None
    intent: Optional[str] = None
    delivery_status: Optional[str] = None
    payment_method: Optional[str] = None
    platform: Optional[str] = None
    language: Optional[str] = None
    customer_type: Optional[str] = None
    issue_severity: Optional[str] = None
    product_variant: Optional[str] = None
    expected_resolution_time: Optional[str] = None
    reference_to_past_ticket: Optional[bool] = None
    preferred_contact_method: Optional[str] = None


class GuardrailCheck(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None


# Guardrail Agent to validate the input of the customer query
guardrail_agent = Agent(
    name="e-commerce-query-analyser-guardrail",
    instructions=gaurdrail_system_prompt,
    model="gpt-4o",
    output_type=GuardrailCheck,
)


@input_guardrail
async def guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not (result.final_output.is_valid),
    )


# Agent to generate metadata from customer queries
e_commerce_agent = Agent(
    name="e-commerce-query-analyser",
    instructions=agent_system_prompt,
    model="gpt-4o",
    output_type=Metadata,
    input_guardrails=[guardrail],
)


# Function to process customer queries
# This function takes a customer query as input and uses the e-commerce agent to generate metadata.
async def process_customer_query(query: str):
    input_data = [
        {
            "role": "user",
            "content": query,
        }
    ]
    try:
        result = await Runner.run(e_commerce_agent, input_data)
        return {"success": True, "data": result.final_output}
    except InputGuardrailTripwireTriggered:
        return {"success": False, "error": "Invalid Customer Query"}


async def main():
    user_input = input("Enter a query: ")
    input_data: list[TResponseInputItem] = []
    input_data.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    try:
        result = await Runner.run(
            e_commerce_agent,
            input_data,
        )
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print(f"Invalid Customer Query")
        return


if __name__ == "__main__":
    asyncio.run(main())
