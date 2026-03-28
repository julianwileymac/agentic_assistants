# requires: temporalio
"""Saga with compensations: book hotel/flight, charge card, cancel on failure."""

from __future__ import annotations

_TEMPORAL_IMPORT_ERROR: str | None = None
try:
    from datetime import timedelta

    from temporalio import activity, workflow
except ImportError as exc:
    _TEMPORAL_IMPORT_ERROR = str(exc)

if _TEMPORAL_IMPORT_ERROR is None:

    @activity.defn
    async def book_hotel(city: str) -> str:
        return f"hotel_reserved:{city}"

    @activity.defn
    async def cancel_hotel(booking_id: str) -> str:
        return f"hotel_cancelled:{booking_id}"

    @activity.defn
    async def book_flight(city: str) -> str:
        return f"flight_booked:{city}"

    @activity.defn
    async def cancel_flight(booking_id: str) -> str:
        return f"flight_cancelled:{booking_id}"

    @activity.defn
    async def charge_payment(amount: float) -> str:
        if amount > 900:
            raise RuntimeError("payment_declined")
        return f"charged:{amount}"

    @activity.defn
    async def refund_payment(charge_id: str) -> str:
        return f"refunded:{charge_id}"

    @workflow.defn
    class BookingSagaWorkflow:
        @workflow.run
        async def run(self, city: str, amount: float) -> str:
            hotel_id = await workflow.execute_activity(
                book_hotel,
                city,
                start_to_close_timeout=timedelta(seconds=30),
            )
            flight_id = await workflow.execute_activity(
                book_flight,
                city,
                start_to_close_timeout=timedelta(seconds=30),
            )
            try:
                charge_id = await workflow.execute_activity(
                    charge_payment,
                    amount,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            except Exception:
                await workflow.execute_activity(
                    cancel_flight,
                    flight_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                await workflow.execute_activity(
                    cancel_hotel,
                    hotel_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                raise
            return f"ok hotel={hotel_id} flight={flight_id} charge={charge_id}"


def main() -> None:
    print("Temporal saga pattern with compensating activities")
    print("-" * 60)
    if _TEMPORAL_IMPORT_ERROR is not None:
        print(
            "Missing dependency. Install with:\n"
            "  pip install temporalio\n"
            f"Import error: {_TEMPORAL_IMPORT_ERROR}"
        )
        return

    print("Forward steps: book_hotel, book_flight, charge_payment")
    print("Compensations: cancel_hotel, cancel_flight, refund_payment (refund unused in this branch)")
    print(
        "\nFlow:\n"
        "  - Reserve hotel and flight.\n"
        "  - If charge_payment fails, cancel flight then cancel hotel (order matters).\n"
        "  - Successful path returns a compact confirmation string.\n"
        "\nTry amount<=900 vs amount>900 when executing against a real worker to see rollback.\n"
    )
    print("Workflow class:", BookingSagaWorkflow.__name__)


if __name__ == "__main__":
    main()
