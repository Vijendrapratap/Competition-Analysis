from uuid import UUID
from sqlalchemy import Select


def scope_to_account(stmt: Select, account_id: UUID, *, column_name: str = "account_id") -> Select:
    """Apply account-level row filtering to a SQLAlchemy select statement."""
    entity = stmt.columns_clause_froms[0] if stmt.columns_clause_froms else None
    if entity is not None and hasattr(entity, column_name):
        return stmt.where(getattr(entity, column_name) == account_id)
    return stmt
