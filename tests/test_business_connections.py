from safe_bot.db.repositories.business_connections import BusinessConnectionRepository


async def test_upsert_stores_and_updates_connection(
    connections: BusinessConnectionRepository,
) -> None:
    created = await connections.upsert(
        connection_id="conn-1",
        user_id=15,
        user_chat_id=15,
        is_enabled=True,
        can_delete_all_messages=True,
        can_delete_sent_messages=False,
    )

    assert created.id == "conn-1"
    assert created.user_chat_id == 15
    assert created.is_enabled is True
    assert created.can_delete_all_messages is True
    assert await connections.get("conn-1") == created

    updated = await connections.upsert(
        connection_id="conn-1",
        user_id=15,
        user_chat_id=20,
        is_enabled=False,
        can_delete_all_messages=False,
        can_delete_sent_messages=True,
    )

    assert updated.user_chat_id == 20
    assert updated.is_enabled is False
    assert updated.can_delete_sent_messages is True
    assert updated.updated_at >= created.updated_at


async def test_get_returns_none_for_unknown_connection(
    connections: BusinessConnectionRepository,
) -> None:
    assert await connections.get("missing") is None
