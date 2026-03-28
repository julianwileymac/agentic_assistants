from __future__ import annotations

from agentic_assistants.core.foundation import AgenticEntity, BaseDTO, DTOConfig, PaginatedResponse


class Project(AgenticEntity):
    name: str
    description: str = ""
    secret_token: str = ""


class ProjectReadDTO(BaseDTO[Project]):
    class Config(DTOConfig):
        exclude = {"secret_token"}
        rename_strategy = "camel"


def main() -> None:
    project = Project(name="core-foundation", description="demo", secret_token="hidden")
    dto = ProjectReadDTO.from_model(project)
    round_tripped = ProjectReadDTO.to_model(dto)

    page = PaginatedResponse[Project](items=[project], total=1, page=1, page_size=10)

    print("DTO:", dto)
    print("Round-trip model:", round_tripped)
    print("Page has_next:", page.has_next)


if __name__ == "__main__":
    main()

