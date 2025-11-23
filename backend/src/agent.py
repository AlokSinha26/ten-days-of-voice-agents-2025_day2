# source_file_url: /mnt/data/dff05c7d-0874-47cd-a4a7-0f490a9b84fd.png
# ======================================================
# COFFEE SHOP VOICE AGENT - NAME-LAST VERSION (Alok Sinha)
# Behavior: Asks for customer's name LAST (records name exactly as spoken)
# No emojis (Windows-safe)
# ======================================================

import sys
import os

# Ensure stdout uses UTF-8 on Windows to avoid encoding errors
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        os.environ["PYTHONIOENCODING"] = "utf-8"

import logging
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Annotated, Literal

print("\n" + "=" * 80)
print("AI COFFEE AGENT FOR ALOK SINHA — NAME-LAST VERSION LOADED")
print("=" * 80 + "\n")

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    MetricsCollectedEvent,
    RunContext,
    function_tool,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")
logger = logging.getLogger("agent")

# ORDER STATE
@dataclass
class OrderState:
    drinkType: str | None = None
    size: str | None = None
    milk: str | None = None
    extras: list[str] = field(default_factory=list)
    name: str | None = None

    def is_complete(self) -> bool:
        return all([
            self.drinkType is not None,
            self.size is not None,
            self.milk is not None,
            self.extras is not None,
            self.name is not None,
        ])

    def get_summary(self) -> str:
        if not self.is_complete():
            return "Order in progress"
        extras_text = f" with {', '.join(self.extras)}" if self.extras else ""
        return f"{self.size} {self.drinkType} with {self.milk} milk{extras_text} for {self.name}"

    def to_dict(self) -> dict:
        return {
            "drinkType": self.drinkType,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name,
        }

@dataclass
class Userdata:
    order: OrderState
    session_start: datetime = field(default_factory=datetime.now)

# FUNCTION TOOLS
@function_tool
def set_drink_type(ctx: RunContext[Userdata], drink: Annotated[Literal[
    "latte", "cappuccino", "americano", "espresso", "mocha", "coffee", "cold brew", "matcha"
], Field(description="Type of drink")]):
    ctx.userdata.order.drinkType = drink
    print(f"[INFO] Drink set: {drink}")
    return f"Great choice. What size would you like for your {drink}?"

@function_tool
def set_size(ctx: RunContext[Userdata], size: Annotated[Literal[
    "small", "medium", "large", "extra large"
], Field(description="Drink size")]):
    ctx.userdata.order.size = size
    print(f"[INFO] Size set: {size}")
    return f"Got it. What milk would you like in your {size} {ctx.userdata.order.drinkType}?"

@function_tool
def set_milk(ctx: RunContext[Userdata], milk: Annotated[Literal[
    "whole", "skim", "almond", "oat", "soy", "coconut", "none"
], Field(description="Milk type")]):
    ctx.userdata.order.milk = milk
    print(f"[INFO] Milk set: {milk}")
    return "Any extras? (sugar, whipped cream, caramel, extra shot, vanilla, cinnamon, honey, or none)"

@function_tool
def set_extras(ctx: RunContext[Userdata], extras: Annotated[list[Literal[
    "sugar", "whipped cream", "caramel", "extra shot", "vanilla", "cinnamon", "honey"
]] | None, Field(description="Extras list")] = None):
    ctx.userdata.order.extras = extras if extras else []
    print(f"[INFO] Extras set: {ctx.userdata.order.extras}")
    return "Perfect. Finally, whose name should this order be under?"

@function_tool
def set_name(ctx: RunContext[Userdata], name: Annotated[str, Field(description="Customer name exactly as given")]):
    # Record the name exactly as the customer says it (strip leading/trailing whitespace only)
    ctx.userdata.order.name = name.strip()
    print(f"[INFO] Name recorded exactly as given: {ctx.userdata.order.name}")
    return f"Got it — recorded name: {ctx.userdata.order.name}. I'll confirm your order now."

@function_tool
def complete_order(ctx: RunContext[Userdata]):
    order = ctx.userdata.order
    if not order.is_complete():
        missing = []
        if not order.drinkType: missing.append("drink type")
        if not order.size: missing.append("size")
        if not order.milk: missing.append("milk")
        if order.extras is None: missing.append("extras")
        if not order.name: missing.append("name")
        msg = f"Order incomplete. Missing: {', '.join(missing)}"
        print(f"[WARN] {msg}")
        return msg

    path = save_order_to_json(order)
    print(f"[INFO] Order saved: {path}")
    return f"Order confirmed: {order.get_summary()}"

# SAVE ORDERS
def get_orders_folder() -> str:
    base = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(base, ".."))
    folder = os.path.join(root, "orders")
    os.makedirs(folder, exist_ok=True)
    return folder

def save_order_to_json(order: OrderState) -> str:
    folder = get_orders_folder()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"order_{ts}.json"
    path = os.path.join(folder, filename)
    data = order.to_dict()
    data["timestamp"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return path

# BARISTA AGENT
class BaristaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a friendly AI barista at Alok's Cafe.\n"
                "IMPORTANT: Collect the order details first — drink type, size, milk, extras.\n"
                "Ask one question at a time. After collecting all order details, ask for the customer's NAME and record it exactly as given.\n"
                "Then confirm and complete the order."
            ),
            tools=[set_drink_type, set_size, set_milk, set_extras, set_name, complete_order],
        )

# ENTRYPOINT
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    userdata = Userdata(order=OrderState())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(voice="en-US-matthew", style="Conversation", text_pacing=True),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata,
    )

    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

    await session.start(
        agent=BaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()

# PREWARM
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    print("[INIT] VAD model loaded")

# RUN
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
