# requires: piccolo
"""Piccolo playground for rapid schema experimentation.

Demonstrates:
- Dynamic schema rebuild
- Interactive exploration
"""

from __future__ import annotations

import asyncio
import tempfile
import uuid
from pathlib import Path


def demo_playground():
    print("Piccolo Playground Pattern:")
    print()
    print("  # Launch interactive playground")
    print("  piccolo playground run")
    print()
    print("  # This dynamically rebuilds the database schema")
    print("  # and opens an IPython shell with all tables loaded.")
    print()
    print("  # Programmatic equivalent:")
    print("  from piccolo.engine.sqlite import SQLiteEngine")
    print("  DB = SQLiteEngine(path='playground.sqlite')  # or tempfile path; :memory: can be tricky with pools")
    print()
    print("  from piccolo.table import Table")
    print("  from piccolo.columns import Varchar, Integer")
    print()
    print("  class Experiment(Table, db=DB):")
    print("      name = Varchar()")
    print("      score = Integer()")
    print()
    print("  import asyncio")
    print("  async def run():")
    print("      await Experiment.create_table().run()")
    print("      await Experiment.insert(Experiment(name='test', score=95)).run()")
    print("      results = await Experiment.select().run()")
    print("      print(results)")
    print()
    print("  asyncio.run(run())")
    print()

    try:
        from piccolo.engine.sqlite import SQLiteEngine
        from piccolo.table import Table
        from piccolo.columns import Varchar, Integer

        # Use a temp file (not :memory:) so all queries share one SQLite database.
        db_path = (
            Path(tempfile.gettempdir()) / f"piccolo_library_playground_{uuid.uuid4().hex}.sqlite"
        )
        DB = SQLiteEngine(path=str(db_path))

        class Experiment(Table, db=DB):
            name = Varchar()
            score = Integer()

        async def run() -> None:
            await Experiment.create_table(if_not_exists=True).run()
            await Experiment.insert(
                Experiment(name="test", score=95),
                Experiment(name="control", score=70),
            ).run()
            results = await Experiment.select().order_by(Experiment.score, ascending=False).run()
            print(f"Programmatic playground (SQLite file {db_path}):")
            print(f"  after INSERT: {results}")
            await Experiment.update({Experiment.score: 100}).where(Experiment.name == "test").run()
            after_update = await Experiment.select(Experiment.name, Experiment.score).run()
            print(f"  after UPDATE: {after_update}")
            await Experiment.delete().where(Experiment.name == "control").run()
            final = await Experiment.select().run()
            print(f"  after DELETE: {final}")

        try:
            asyncio.run(run())
        except Exception as exc:
            print(f"Playground run error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("(Install piccolo to run the in-memory playground snippet.)")


if __name__ == "__main__":
    demo_playground()
