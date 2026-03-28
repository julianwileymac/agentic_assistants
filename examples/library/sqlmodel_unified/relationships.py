# requires: sqlmodel sqlalchemy
"""SQLModel relationships: one-to-many, many-to-many with link tables.

Demonstrates:
- Relationship() for foreign keys
- Link table for many-to-many
"""

import tempfile
from pathlib import Path
from typing import List, Optional


def demo_relationships():
    try:
        from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select

        class Team(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(index=True)
            headquarters: str = ""
            heroes: List["Hero"] = Relationship(back_populates="team")

        class HeroSkillLink(SQLModel, table=True):
            """Link table for many-to-many."""

            hero_id: Optional[int] = Field(
                default=None, foreign_key="hero.id", primary_key=True
            )
            skill_id: Optional[int] = Field(
                default=None, foreign_key="skill.id", primary_key=True
            )

        class Hero(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(index=True)
            team_id: Optional[int] = Field(default=None, foreign_key="team.id")
            team: Optional["Team"] = Relationship(back_populates="heroes")
            skills: List["Skill"] = Relationship(
                back_populates="heroes", link_model=HeroSkillLink
            )

        class Skill(SQLModel, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            name: str = Field(index=True, unique=True)
            heroes: List["Hero"] = Relationship(
                back_populates="skills", link_model=HeroSkillLink
            )

        print("SQLModel Relationships:")
        print("  One-to-many: Team -> Heroes (via team_id FK)")
        print("  Many-to-many: Hero <-> Skill (via HeroSkillLink)")

        db_path = Path(tempfile.gettempdir()) / "sqlmodel_library_relationships.sqlite"
        engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(engine)

        try:
            with Session(engine) as session:
                team = Team(name="Justice League", headquarters="DC")
                hero = Hero(name="Batman", team=team)
                skill = Skill(name="Detective work")
                session.add(hero)
                session.add(skill)
                session.commit()
                session.refresh(hero)
                session.refresh(skill)
                link = HeroSkillLink(hero_id=hero.id, skill_id=skill.id)
                session.add(link)
                session.commit()
                loaded = session.exec(select(Hero).where(Hero.name == "Batman")).first()
                session.refresh(loaded, ["team", "skills"])
                print()
                print(f"SQLite on {db_path}:")
                print(f"  Hero {loaded.name!r} team={loaded.team.name if loaded.team else None}")
                print(f"  skills={[s.name for s in (loaded.skills or [])]}")
        except Exception as exc:
            print(f"SQLite demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install sqlmodel")


if __name__ == "__main__":
    demo_relationships()
