from typing import Any

from sqlalchemy.sql import Insert as Insert

def get_on_conflict_stmt(stmt: Insert, index: Any, args: Any, where: Any) -> Insert: ...
def update_required(normalised_table: Any, stmt: Any, refresh_data: Any): ...
