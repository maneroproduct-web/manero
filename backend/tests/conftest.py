import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Product, ProductVariant
from app.models.enums import BeanType, Flavour, Grind, RoastLevel

# In-memory SQLite keeps the suite fast and independent of a running Postgres.
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    # StaticPool is essential, not an optimisation: every new connection to
    # ':memory:' gets its own private database. Without it, each request in a
    # test would talk to a different empty DB and writes would vanish.
    eng = create_async_engine(
        TEST_DB_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def catalog(session_factory):
    """Three products spanning the filter dimensions, with known prices."""
    specs = [
        ("dark-arabica", "Dark Arabica", BeanType.ARABICA, RoastLevel.DARK,
         Grind.FILTER, Flavour.ORIGINAL, True, [(250, 40000, 5)]),
        ("light-arabica", "Light Arabica", BeanType.ARABICA, RoastLevel.LIGHT,
         Grind.FILTER, Flavour.ORIGINAL, False, [(250, 50000, 5)]),
        ("hazelnut-instant", "Hazelnut Instant", BeanType.BLEND, RoastLevel.MEDIUM,
         Grind.INSTANT, Flavour.HAZELNUT, True, [(50, 20000, 2)]),
    ]

    async with session_factory() as session:
        for slug, name, bean, roast, grind, flavour, best, variants in specs:
            product = Product(
                slug=slug, name=name, description="", bean_type=bean,
                roast_level=roast, grind=grind, flavour=flavour,
                origin="Test", tasting_notes="", image_url="",
                is_active=True, is_bestseller=best,
            )
            session.add(product)
            await session.flush()
            for grams, price, stock in variants:
                session.add(
                    ProductVariant(
                        product_id=product.id,
                        # Uppercase, matching both the seed script and the
                        # admin API's SKU normalisation.
                        sku=f"{slug}-{grams}".upper(),
                        size_grams=grams, price_paise=price,
                        compare_at_price_paise=None, stock_qty=stock,
                    )
                )
        await session.commit()


@pytest.fixture
def anyio_backend():
    return "asyncio"
