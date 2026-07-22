import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.etl.core.sync_models import ResolverStrategy
from app.models.operational import Client, Engineer, Team, Technology


class MasterDataResolver:
    """Resolves and caches master dimension entities with strategies."""

    def __init__(self) -> None:
        self._clients: dict[str, uuid.UUID] = {}
        self._engineers: dict[str, uuid.UUID] = {}
        self._technologies: dict[str, uuid.UUID] = {}
        self._teams: dict[str, uuid.UUID] = {}

    async def resolve_team(
        self, session: AsyncSession, name: str | None, strategy: ResolverStrategy
    ) -> tuple[uuid.UUID | None, str | None]:
        """Resolves team reference."""
        if not name:
            return None, None
        norm_name = name.strip()
        key = norm_name.lower()

        if key in self._teams:
            return self._teams[key], None

        stmt = select(Team).where(Team.name == norm_name)
        result = await session.execute(stmt)
        team_obj = result.scalar_one_or_none()

        if team_obj:
            self._teams[key] = team_obj.id
            return team_obj.id, None

        if strategy == ResolverStrategy.CREATE_IF_MISSING:
            new_team = Team(id=uuid.uuid4(), name=norm_name)
            session.add(new_team)
            await session.flush()
            self._teams[key] = new_team.id
            return new_team.id, None

        if strategy == ResolverStrategy.REJECT_IF_MISSING:
            return None, f"Team '{norm_name}' rejected as missing."

        return None, f"Team '{norm_name}' missing reference warning."

    async def resolve_client(
        self, session: AsyncSession, name: str | None, strategy: ResolverStrategy
    ) -> tuple[uuid.UUID | None, str | None]:
        """Resolves client reference."""
        if not name:
            return None, None
        norm_name = name.strip()
        key = norm_name.lower()

        if key in self._clients:
            return self._clients[key], None

        stmt = select(Client).where(Client.name == norm_name)
        result = await session.execute(stmt)
        client_obj = result.scalar_one_or_none()

        if client_obj:
            self._clients[key] = client_obj.id
            return client_obj.id, None

        if strategy == ResolverStrategy.CREATE_IF_MISSING:
            new_client = Client(id=uuid.uuid4(), name=norm_name)
            session.add(new_client)
            await session.flush()
            self._clients[key] = new_client.id
            return new_client.id, None

        if strategy == ResolverStrategy.REJECT_IF_MISSING:
            return None, f"Client '{norm_name}' rejected as missing."

        return None, f"Client '{norm_name}' missing reference warning."

    async def resolve_engineer(
        self, session: AsyncSession, name: str | None, strategy: ResolverStrategy
    ) -> tuple[uuid.UUID | None, str | None]:
        """Resolves engineer reference."""
        if not name:
            return None, None
        norm_name = name.strip()
        key = norm_name.lower()

        if key in self._engineers:
            return self._engineers[key], None

        stmt = select(Engineer).where(Engineer.name == norm_name)
        result = await session.execute(stmt)
        eng_obj = result.scalar_one_or_none()

        if eng_obj:
            self._engineers[key] = eng_obj.id
            return eng_obj.id, None

        if strategy == ResolverStrategy.CREATE_IF_MISSING:
            new_eng = Engineer(id=uuid.uuid4(), name=norm_name)
            session.add(new_eng)
            await session.flush()
            self._engineers[key] = new_eng.id
            return new_eng.id, None

        if strategy == ResolverStrategy.REJECT_IF_MISSING:
            return None, f"Engineer '{norm_name}' rejected as missing."

        return None, f"Engineer '{norm_name}' missing reference warning."

    async def resolve_technology(
        self, session: AsyncSession, name: str | None, strategy: ResolverStrategy
    ) -> tuple[uuid.UUID | None, str | None]:
        """Resolves technology reference."""
        if not name:
            return None, None
        norm_name = name.strip()
        key = norm_name.lower()

        if key in self._technologies:
            return self._technologies[key], None

        stmt = select(Technology).where(Technology.name == norm_name)
        result = await session.execute(stmt)
        tech_obj = result.scalar_one_or_none()

        if tech_obj:
            self._technologies[key] = tech_obj.id
            return tech_obj.id, None

        if strategy == ResolverStrategy.CREATE_IF_MISSING:
            new_tech = Technology(id=uuid.uuid4(), name=norm_name)
            session.add(new_tech)
            await session.flush()
            self._technologies[key] = new_tech.id
            return new_tech.id, None

        if strategy == ResolverStrategy.REJECT_IF_MISSING:
            return None, f"Technology '{norm_name}' rejected as missing."

        return None, f"Technology '{norm_name}' missing reference warning."
