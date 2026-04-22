# SKILL BIBLE — Python API Development
# Knight: Sir Forge | Layer: L2_KINETIC | v400.1.0
# LOAD: PY_DATA / PY_API — instilled on Python/FastAPI/Pydantic tasks

## TITANIUM LAW #1 CHECK
Before writing Python: does a compiled Rust/Go binary already exist for this task?
YES → use the binary. NO → proceed with Python.

## STACK
- **Python**: 3.11+ (CAMELOT venv: `.venv_camelot` managed by `uv`)
- **Framework**: FastAPI with async handlers only
- **Validation**: Pydantic v2 (`model_validator`, `field_validator`, `model_config`)
- **ORM**: SQLAlchemy 2.0 async sessions + Alembic migrations
- **HTTP Client**: httpx (async) — never requests in async context
- **Logging**: structlog (structured) — never bare print() in production
- **Testing**: pytest + pytest-asyncio — mandatory coverage for edge/failure
- **Linting**: ruff (replaces black + flake8 + isort)
- **Type checking**: mypy strict — `--strict` flag mandatory

## CONVENTIONS
```python
# Correct: async handler, typed, structured logging
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)) -> ItemResponse:
    repo = ItemRepository(db)
    result = await repo.create(item)
    logger.info("item_created", id=result.id)
    return ItemResponse.model_validate(result)

# Correct: Pydantic v2 model
class ItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=255)
    tags: list[str] = Field(default_factory=list)
```

## CAMELOT-SPECIFIC PATTERNS
- **Agent orchestration**: Pydantic AI (`control_plane/`)
- **A2A transport**: JSON-RPC over HTTP — see `swarm-colony.md`
- **MCP delegation**: kinetic_edge client at :3001
- **State persistence**: `ouroboros.db` (SQLite WAL mode)
- **Package manager**: `uv` — never pip directly in CAMELOT venv

## ANTI-PATTERNS (Sir Gideon will STING)
- Python scripts at L2 edge where compiled binary exists → KINETIC_PURITY
- Synchronous DB calls inside `async def` → event loop blocking
- Business logic in route handlers → repository pattern required
- Raw SQL without parameterization → SQL injection vector
- Global mutable state → concurrency bug
- `import *` at module level → namespace pollution
- Missing type hints at function boundaries → mypy will fail
- `print()` in production code → use structlog
