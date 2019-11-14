import json
from json import JSONDecodeError

from flask import Response, request
from fluidly.flask.api_exception import APIException
from fluidly.sqlalchemy.db import db_session
from sqlalchemy.inspection import inspect

DEFAULT_PAGE_SIZE = 10


def get_model_by_tablename(base, table_name):
    for c in base._decl_class_registry.values():
        if hasattr(c, "__tablename__") and c.__tablename__ == table_name:
            return c


def get_model_dict(model):
    return {
        column.name: getattr(model, column.name) for column in model.__table__.columns
    }


def is_valid_query(model, query):
    if not query:
        return False

    inspected_model = inspect(model)
    columns = [c.name for c in inspected_model.columns]

    for var in query:
        if var not in columns:
            return False
    return True


def post_model_by_connection_id_query(base, table_name):
    model = get_model_by_tablename(base, table_name)
    if not model:
        return Response(status=404)

    try:
        payload = request.get_json(force=True)
    except JSONDecodeError:
        raise APIException(status=422, title="Request body has invalid json")

    query = payload.get("query")

    if not is_valid_query(model, query):
        return Response(response="Query is invalid", status=400)

    page = payload.get("page", 1)
    page_size = payload.get("page_size", DEFAULT_PAGE_SIZE)

    if page < 1:
        return Response(response="Pages start at 1", status=400)

    with db_session() as session:
        session.execute("set local statement_timeout = 10000")

        results = (
            session.query(model)
            .filter_by(**query)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        result_values = []

        if results:
            for m in results:
                result_values.append(get_model_dict(m))

    return Response(
        response=json.dumps(
            {"meta": {"query": query}, "data": result_values}, default=str
        ),
        status=200,
        mimetype="application/json",
    )
