# Library examples

This directory collects small, runnable Python modules that demonstrate patterns for **data modeling**, **validation**, **persistence**, **HTTP service boundaries**, **machine learning**, **agent orchestration**, **evaluation**, **synthetic data**, and **design patterns**. Each script is self-contained: read the module docstring, install the packages named in the `# requires:` header, and run `python path/to/file.py`.

Optional dependencies for this corpus are grouped in several Poetry extras (see the root `pyproject.toml`). Install them with:

```bash
# All library examples
pip install "agentic-assistants[library]"

# Or specific categories
pip install "agentic-assistants[classical-ml]"      # scikit-learn, xgboost, lightgbm, catboost
pip install "agentic-assistants[streaming-ml]"       # river
pip install "agentic-assistants[evaluation]"          # ragas, deepeval, great-expectations
pip install "agentic-assistants[synthetic-data]"      # sdv, faker
pip install "agentic-assistants[durable]"             # temporalio
pip install "agentic-assistants[feature-store]"       # feast
pip install "agentic-assistants[jax]"                 # jax, flax, optax
pip install "agentic-assistants[pytorch]"             # torch, torchvision, torchaudio
pip install "agentic-assistants[huggingface]"         # transformers, datasets, etc.
pip install "agentic-assistants[tensorflow]"          # tensorflow
pip install "agentic-assistants[serving]"              # bentoml
pip install "agentic-assistants[airflow]"              # apache-airflow
pip install "agentic-assistants[versioning]"           # dvc
```

Or, in a Poetry workflow:

```bash
poetry install -E library
```

Some SQLAlchemy async examples use **`aiosqlite`** for in-memory SQLite. Install it alongside the extras when you run those demos:

```bash
pip install aiosqlite
```

---

## Forty-two topic areas

### Data Modeling and Validation (1-5)

1. **Pydantic advanced validation** — `pydantic_models/advanced_validation.py` — field and model validators, computed fields, `Annotated` constraints, before/after hooks, JSON Schema.
2. **Pydantic generics and unions** — `pydantic_models/generic_models.py` — `Generic` models, discriminated unions, `TypeAdapter` for non-model types.
3. **Layered application settings** — `pydantic_models/settings_management.py` — `BaseSettings`, `.env`, YAML bootstrap, `secrets_dir`, nested settings.
4. **Serialization and wire formats** — `pydantic_models/serialization_patterns.py` — aliases, `model_dump(mode="json")`, exclusions, `json_schema_extra`.
5. **LLM tool / function JSON Schema** — `pydantic_models/schema_generation.py` — OpenAI-style tool definitions from `model_json_schema()`.

### ORM and Persistence (6-10)

6. **Declarative ORM mapping** — `sqlalchemy_models/declarative_base.py` — SQLAlchemy 2.0 `Mapped`, relationships, `select()` / `scalars()`.
7. **Async SQLAlchemy sessions** — `sqlalchemy_models/async_session.py` — `async_sessionmaker`, async CRUD (SQLite + notes for `asyncpg`).
8. **Generic CRUD repository** — `sqlalchemy_models/repository_pattern.py` — typed repository over `Session`.
9. **ORM mixins** — `sqlalchemy_models/mixins_and_base_classes.py` — UUID, audit, soft delete, slug composition.
10. **Advanced SQLAlchemy queries** — `sqlalchemy_models/advanced_queries.py` — CTEs, window functions, `hybrid_property`, `TypeDecorator`, bulk updates.

### API and Service Boundaries (11-15)

11. **Litestar DTO boundaries** — `litestar_patterns/dto_boundaries.py` — `DataclassDTO`, `PydanticDTO`, include/exclude/rename strategies.
12. **Litestar layered APIs** — `litestar_patterns/layered_api.py` — controllers, guards, DI, `ASGIMiddleware`.
13. **Litestar + msgspec** — `litestar_patterns/msgspec_integration.py` — `MsgspecDTO` for request/response structs.
14. **Litestar + Advanced Alchemy** — `litestar_patterns/repository_service.py` — async repositories, services, startup hooks.
15. **Msgspec structs and integration** — `msgspec_structs/` — struct options, `Meta` validation, performance benchmarks, FastAPI + SQLAlchemy handoff.

### Agent Frameworks (16-24)

16. **PydanticAI agents** — `pydantic_ai_agents/` — structured agents, multi-tool agents, streaming, self-correction, Ollama integration.
17. **Advanced Alchemy patterns** — `advanced_alchemy_patterns/` — base models, generic repositories, service layers, DTO integration with real SQLite operations.
18. **CrewAI patterns** — `crewai_patterns/` — research, code review, data pipeline, and hierarchical crews with kickoff.
19. **LangGraph workflows** — `langgraph_workflows/` — state graphs, ReAct agent, multi-agent, persistence, human-in-the-loop, state reducers.
20. **Marvin AI utilities** — `marvin_ai/` — AI functions, classifiers, models, planning, integration patterns.
21. **AutoGen agents** — `autogen_agents/` — multi-agent conversations, code execution, group chat, tool use with Microsoft AutoGen.
22. **Agno agents** — `agno_agents/` — tool-centric agents, multi-tool setup, team coordination with Agno/Phidata.
23. **OpenAI Swarm** — `openai_swarm/` — minimalist handoffs, triage routing, context variables.
24. **Prefect workflows** — `prefect_workflows/` — flows, state management, data pipelines, deployments, observability.

### Classical ML and Data Science (25-28)

25. **Scikit-learn patterns** — `scikit_learn/` — supervised (linear, logistic, SVM, NaiveBayes), unsupervised (KMeans, DBSCAN), PCA/t-SNE, pipelines, evaluation metrics, advanced clustering (OPTICS, Spectral), advanced reduction (TruncatedSVD, KernelPCA).
26. **Gradient boosting trio** — `gradient_boosting/` — XGBoost, LightGBM, CatBoost with early stopping, feature importance, head-to-head benchmarks, distributed training, Optuna hyperparameter tuning.
27. **River streaming ML** — `river_streaming/` — online learning, concept drift detection, composable streaming pipelines.
28. **HDBSCAN + UMAP** — `hdbscan_umap/` — density-based clustering with HDBSCAN, UMAP dimensionality reduction, end-to-end clustering pipelines.

### Deep Learning (29-33)

29. **PyTorch foundations** — `pytorch_foundations/` — custom modules, training loops, datasets, transfer learning, distributed basics, transformer architecture from scratch, mixed precision training.
30. **JAX fundamentals** — `jax_fundamentals/` — autodiff, JIT, vmap, Flax modules, Optax optimizers.
31. **Transformers Hub** — `transformers_hub/` — model loading, text classification, generation, custom Trainer API, PEFT/LoRA fine-tuning, model evaluation and benchmarking.
32. **TensorFlow / Keras** — `tensorflow_keras/` — Sequential and Functional API, custom GradientTape training, transfer learning, model export (SavedModel, TFLite).
33. **Unsloth fine-tuning** — `unsloth_finetuning/` — QLoRA setup, SFTTrainer, synthetic QA pair generation, GGUF export and Ollama deployment.

### Agent Frameworks Extended (24a-24b)

24a. **LangChain chains** — `langchain_chains/` — LCEL composition, RAG retrieval chains, tool calling, memory patterns, output parsers.

### MLOps and Infrastructure (34-39)

34. **MLflow tracking** — `mlflow_tracking/` — experiment basics, model registry, autolog, custom pyfunc models.
35. **Feast feature store** — `feast_features/` — feature definitions, materialization, online/offline retrieval.
36. **Temporal workflows** — `temporal_workflows/` — durable workflows, saga patterns, child workflows, agentic orchestration.
37. **Airflow workflows** — `airflow_workflows/` — TaskFlow API, ML pipeline DAGs, branching, dynamic task mapping.
38. **BentoML serving** — `bentoml_serving/` — model packaging, API endpoints, containerization, adaptive batching.
39. **DVC versioning** — `dvc_versioning/` — pipeline versioning, data tracking, experiment comparison.

### ML Helpers (40-42)

40. **Mlxtend helpers** — `mlxtend_helpers/` — sequential feature selection, ensemble methods (stacking, voting), visualization tools.
41. **Phoenix / Arize** — `phoenix_arize/` — LLM tracing, RAG evaluation, embedding drift monitoring.
42. **ML design patterns** — `design_patterns/` — creational (Factory, Builder, Singleton), structural (Adapter, Decorator, Proxy), behavioral (Strategy, Observer, Command), agent skill patterns.

### Evaluation and Reliability (E1-E3)

- **RAGAS evaluation** — `ragas_evaluation/` — RAG metrics, synthetic test sets, agent metrics, custom rubrics.
- **DeepEval testing** — `deepeval_testing/` — LLM unit testing, hallucination checks, RAG evaluation.
- **Great Expectations validation** — `great_expectations_validation/` — expectation suites, data validation, pipeline gates.

### Synthetic Data (S1-S2)

- **Synthetic Data Vault** — `sdv_synthetic/` — GaussianCopula, CTGAN, relational HMA, quality metrics.
- **Faker data generation** — `faker_data/` — basic providers, bulk DataFrames, domain-specific factories.

### Observability and Patterns (O1-O2)

- **Logfire observability** — `logfire_observability/` — basic spans, Pydantic/FastAPI/SQLAlchemy/LLM instrumentation.
- **ML design patterns** — `design_patterns/` — creational (Factory, Builder, Singleton), structural (Adapter, Decorator, Proxy), behavioral (Strategy, Observer, Command), agent skill patterns.

### Additional ORM Topics (A1-A4)

- **Beanie ODM** — `beanie_odm/` — async MongoDB documents, CRUD, queries, relationships, multi-model.
- **Piccolo ORM** — `piccolo_orm/` — async tables, queries, migrations, playground with SQLite.
- **Strawberry GraphQL** — `strawberry_graphql/` — schema, resolvers, DataLoaders, FastAPI integration, federation.
- **SQLModel unified** — `sqlmodel_unified/` — unified Pydantic/SQL models, FastAPI CRUD, relationships.

---

## Layout

| Folder | Focus |
| --- | --- |
| `pydantic_models/` | Validation, settings, serialization, schema export |
| `sqlalchemy_models/` | ORM mapping, async IO, repositories, SQL techniques |
| `litestar_patterns/` | DTOs, HTTP layering, msgspec, Advanced Alchemy |
| `msgspec_structs/` | High-performance structs and integration patterns |
| `pydantic_ai_agents/` | PydanticAI structured agents and tools |
| `advanced_alchemy_patterns/` | SQLAlchemy 2 service layers and repositories |
| `crewai_patterns/` | Multi-agent crew orchestration |
| `langgraph_workflows/` | State graph workflows and multi-agent systems |
| `marvin_ai/` | AI-powered functions, classifiers, and planning |
| `prefect_workflows/` | Workflow orchestration with Prefect |
| `autogen_agents/` | Microsoft AutoGen multi-agent systems |
| `agno_agents/` | Agno/Phidata tool-centric agents |
| `openai_swarm/` | OpenAI Swarm agent handoffs |
| `scikit_learn/` | Classical ML with scikit-learn |
| `gradient_boosting/` | XGBoost, LightGBM, CatBoost |
| `river_streaming/` | Online/streaming machine learning |
| `pytorch_foundations/` | PyTorch deep learning foundations |
| `jax_fundamentals/` | JAX, Flax, and Optax |
| `transformers_hub/` | HuggingFace Transformers |
| `mlflow_tracking/` | MLflow experiment tracking and registry |
| `feast_features/` | Feast feature store patterns |
| `temporal_workflows/` | Temporal durable workflow orchestration |
| `ragas_evaluation/` | RAGAS RAG evaluation metrics |
| `deepeval_testing/` | DeepEval LLM testing |
| `great_expectations_validation/` | Great Expectations data quality |
| `sdv_synthetic/` | Synthetic Data Vault generation |
| `faker_data/` | Faker procedural mock data |
| `design_patterns/` | GoF design patterns for ML platforms |
| `tensorflow_keras/` | TensorFlow / Keras deep learning |
| `unsloth_finetuning/` | Accelerated LLM fine-tuning with Unsloth |
| `langchain_chains/` | LangChain LCEL chains and RAG |
| `airflow_workflows/` | Apache Airflow ML DAGs |
| `bentoml_serving/` | BentoML model serving |
| `dvc_versioning/` | DVC data and pipeline versioning |
| `mlxtend_helpers/` | Mlxtend ML helper utilities |
| `hdbscan_umap/` | HDBSCAN clustering + UMAP reduction |
| `phoenix_arize/` | Phoenix / Arize LLM observability |
| `beanie_odm/` | Beanie async MongoDB ODM |
| `piccolo_orm/` | Piccolo async ORM |
| `strawberry_graphql/` | Strawberry GraphQL API |
| `sqlmodel_unified/` | SQLModel unified Pydantic/SQL |
| `logfire_observability/` | Logfire/OpenTelemetry observability |

These examples are educational; copy patterns deliberately into production code rather than importing them as a package.
