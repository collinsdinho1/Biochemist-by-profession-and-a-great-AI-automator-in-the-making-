from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
    print("API Client Ready")
else:
    client = None
    print("GROQ_API_KEY not found. Add it to .env or your environment variables to enable API calls.")

app = FastAPI(title="Abuja Threads support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Agent:
    def __init__(self, name, role, instructions):
        self.name = name
        self.role = role
        self.instructions = instructions

    def run(self, task):
        if client is None:
            return "API unavailable: Missing GROQ_API_KEY."

        print(" " + self.name + " is working...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are " + self.name + ", " + self.role + ".\n" + self.instructions},
                {"role": "user", "content": task},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        result = response.choices[0].message.content
        print(" " + self.name + " completed")
        return result


# create specialized Agent
sales_agent = Agent(
    "Sales Agent",
    "A friendly sales representative for an Abuja-based fashion store called Abuja Threads",
    "Answer questions about products, prices, and availability. Be warm and helpful. Use Nigerian English phrases when appropriate. Encourage the customer to make a purchase.",
)

support_agent = Agent(
    "Support Agent",
    "A customer support specialist for a Nigerian e-commerce business",
    "Handle complaints about late deliveries, wrong items, or poor service. Be empathetic and solution-oriented. Never make promises you can't keep.",
)

order_agent = Agent(
    "Order Agent",
    "An order status specialist",
    "Provide information about order tracking, delivery timelines, and shipping. Be precise and reassuring.",
)

router_agent = Agent(
    "Router",
    "A customer service dispatcher",
    "Classify the customer's message into one of the three categories: SALES, SUPPORT, or ORDER. Reply with ONLY the category name.",
)


# Api Models
class CustomerMessage(BaseModel):
    message: str


@app.get("/")
def read_root():
    return {"status": "Abuja Threads Support API is running"}


@app.post("/support")
async def handle_customer_message(request: CustomerMessage):
    try:
        category = router_agent.run("Classify this message: " + request.message).strip().upper()

        if "SALES" in category:
            response = sales_agent.run(request.message)
        elif "SUPPORT" in category:
            response = support_agent.run(request.message)
        elif "ORDER" in category:
            response = order_agent.run(request.message)
        else:
            response = "I'm sorry, I didn't understand that. Could you please rephrase your question?"

        return {
            "success": True,
            "category": category,
            "reply": response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))