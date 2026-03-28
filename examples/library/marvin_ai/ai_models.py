# requires: marvin pydantic openai
"""Marvin @ai_model for structured extraction from unstructured text.

Demonstrates:
- Extracting structured Pydantic models from raw text
- Multiple model types for different extraction tasks
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    city: str
    state: str = ""
    country: str
    latitude: float = 0.0
    longitude: float = 0.0


class Person(BaseModel):
    name: str
    age: int = Field(ge=0, default=0)
    occupation: str = ""
    email: str = ""


class Event(BaseModel):
    name: str
    date: str = ""
    location: str = ""
    attendees: int = Field(ge=0, default=0)
    description: str = ""


def _print_usage_hints() -> None:
    print("Usage (when Marvin + OpenAI are configured):")
    print("  location = marvin.cast(")
    print("      'The conference is at the Moscone Center in San Francisco, CA',")
    print("      target=Location,")
    print("  )")
    print()
    print("  people = marvin.cast(")
    print("      'John (35, engineer) and Jane (28, designer) attended the meeting',")
    print("      target=list[Person],")
    print("  )")


def demo_ai_models():
    """Show Marvin's structured extraction via marvin.cast."""
    try:
        import marvin
    except ImportError:
        print("Install: pip install marvin openai")
        print()
        print("Models defined:")
        for cls in (Location, Person, Event):
            print(f"  {cls.__name__}: {list(cls.model_fields.keys())}")
        return

    _print_usage_hints()
    print()

    loc_text = "The conference is at the Moscone Center in San Francisco, CA, USA."
    print(f"Trying marvin.cast(..., target=Location) on:\n  {loc_text!r}\n")
    try:
        location = marvin.cast(loc_text, target=Location)
        print("  Parsed Location:", location.model_dump())
    except Exception as exc:
        print(f"  Could not call the model ({type(exc).__name__}: {exc}).")
        print(
            "  With OPENAI_API_KEY set and a reachable provider, Marvin would infer fields "
            "from the sentence."
        )
        print(
            "  Offline example:",
            Location(city="San Francisco", state="CA", country="USA").model_dump(),
        )

    people_text = "John (35, engineer) and Jane (28, designer) attended the meeting."
    print(f"\nTrying marvin.cast(..., target=list[Person]) on:\n  {people_text!r}\n")
    try:
        people = marvin.cast(people_text, target=list[Person])
        print("  Parsed people:", [p.model_dump() for p in people])
    except Exception as exc:
        print(f"  Could not extract list[Person] ({type(exc).__name__}: {exc}).")
        print(
            "  Offline example:",
            [
                Person(name="John", age=35, occupation="engineer").model_dump(),
                Person(name="Jane", age=28, occupation="designer").model_dump(),
            ],
        )

    event_text = (
        "Team offsite 'Alpine Sync' on 2026-04-12 at Lake Tahoe resort; about 40 people; "
        "focus on roadmap and culture."
    )
    print(f"\nTrying marvin.cast(..., target=Event) on:\n  {event_text!r}\n")
    try:
        event = marvin.cast(event_text, target=Event)
        print("  Parsed Event:", event.model_dump())
    except Exception as exc:
        print(f"  Could not parse Event ({type(exc).__name__}: {exc}).")
        print(
            "  Offline example:",
            Event(
                name="Alpine Sync",
                date="2026-04-12",
                location="Lake Tahoe resort",
                attendees=40,
                description="roadmap and culture",
            ).model_dump(),
        )


def main() -> None:
    """Run structured extraction demos with marvin.cast and offline fallbacks."""
    demo_ai_models()


if __name__ == "__main__":
    main()
