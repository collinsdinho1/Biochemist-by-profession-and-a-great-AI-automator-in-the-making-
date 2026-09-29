from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
    print("Api Client Ready")
else:
    client = None
    print("GROQ_API_KEY not found. Add it to .env or your environment variables to enable API calls.")


# Define the Agent Class
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
    "Answer questions about products, prices, and availability. Be warm and helpful. Use Nigerian English phrases when appropriate. Encourage the customer to make a purchase."
)

support_agent = Agent(
    "Support Agent",
    "A customer support specialist for a Nigerian e-commerce business",
    "Handle complaints about late deliveries, wrong items, or poor service. Be empathetic and solution-oriented. Never make promises you can't keep."
)

order_agent = Agent(
    "Order Agent",
    "An order status specialist",
    "Provide information about order tracking, delivery timelines, and shipping. Be precise and reassuring."
)

router_agent = Agent(
    "Router",
    "A customer service dispatcher",
    "Classify the customer's message into one of the three categories: SALES, SUPPORT, or ORDER. Reply with ONLY the category name."
)

print("Agents created:")
print("1. Sales Agent")
print("2. Support Agent")
print("3. Order Agent")
print("4. Router Agent")


# Multi-Agent pipeline
def handle_customer_message(message):
    print()
    print("=" * 50)
    print("Customer Message:", message)
    print("=" * 50)

    # Step 1: Classify
    print("step 1")
    print("=" * 40)
    category = router_agent.run("Classify this message: " + message).strip().upper()
    print("Category:", category)
    print()

    # Step 2: route to the right agent
    print("step 2")
    print("-" * 40)
    if "SALES" in category:
        response = sales_agent.run(message)
    elif "SUPPORT" in category:
        response = support_agent.run(message)
    elif "ORDER" in category:
        response = order_agent.run(message)
    else:
        response = "I'm sorry, I didn't understand that. Could you please rephrase your question?"

    print()
    print("Final Message")
    print("-" * 40)
    print(response)
    return {"category": category, "reply": response}


# Test Agent
print()
print("Testing Multi-agent System")
print("=" * 50)

# Test 1
handle_customer_message("How much is the ankara dress in your Abuja store?")

# Test 2
handle_customer_message("Abeg, my order never reach oo. I order last week and i don de vex.")

# Test 3
handle_customer_message("What is the status of my order LT-4823?")
