from sqlalchemy import select

from app.models import ContactMessage

VALID = {
    "name": "Nidhi Choudhary",
    "email": "nidhi@example.com",
    "phone": "9876543210",
    "subject": "wholesale",
    "message": "Do you supply 5kg bags for a cafe in Bengaluru?",
}


async def test_message_is_stored(client, session_factory):
    r = await client.post("/api/v1/contact", json=VALID)
    assert r.status_code == 201
    assert r.json()["ok"] is True
    assert r.json()["reference"].startswith("MSG")

    async with session_factory() as session:
        msg = await session.scalar(select(ContactMessage))
        assert msg.name == "Nidhi Choudhary"
        assert msg.message.startswith("Do you supply")
        assert msg.handled is False   # lands in the unhandled queue


async def test_phone_is_optional(client):
    r = await client.post("/api/v1/contact", json={**VALID, "phone": ""})
    assert r.status_code == 201


async def test_bad_phone_is_rejected(client):
    r = await client.post("/api/v1/contact", json={**VALID, "phone": "12345"})
    assert r.status_code == 422


async def test_bad_email_is_rejected(client):
    r = await client.post("/api/v1/contact", json={**VALID, "email": "not-an-email"})
    assert r.status_code == 422


async def test_short_message_is_rejected(client):
    r = await client.post("/api/v1/contact", json={**VALID, "message": "hi"})
    assert r.status_code == 422


async def test_whitespace_only_name_is_rejected(client):
    r = await client.post("/api/v1/contact", json={**VALID, "name": "   "})
    assert r.status_code == 422


async def test_flood_from_one_address_is_throttled(client):
    """The queue is only useful if a script can't bury it."""
    for _ in range(5):
        assert (await client.post("/api/v1/contact", json=VALID)).status_code == 201

    sixth = await client.post("/api/v1/contact", json=VALID)
    assert sixth.status_code == 429

    # A different person is unaffected.
    other = await client.post(
        "/api/v1/contact", json={**VALID, "email": "someone.else@example.com"}
    )
    assert other.status_code == 201
