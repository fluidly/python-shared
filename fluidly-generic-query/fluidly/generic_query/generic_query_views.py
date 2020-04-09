import json
import re
from json.decoder import JSONDecodeError

from flask import Blueprint, Response, request
from marshmallow import INCLUDE, Schema, ValidationError, fields
from sqlalchemy.inspection import inspect

from fluidly.flask.api_exception import APIException
from fluidly.sqlalchemy.db import db_session

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
    if not query or "connection_id" not in query:
        return False

    inspected_model = inspect(model)
    columns = [c.name for c in inspected_model.columns]

    for var in query:
        if var not in columns:
            return False
    return True


first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


def snakecase(name):
    s1 = first_cap_re.sub(r"\1_\2", name)
    return all_cap_re.sub(r"\1_\2", s1).lower()


def snakify(data):
    return {snakecase(key): value for key, value in data.items()}


class QuerySchema(Schema):
    class Meta:
        unknown = INCLUDE


class RequestSchema(Schema):
    query = fields.Nested(QuerySchema, required=True)
    page = fields.Integer()
    page_size = fields.Integer(data_key="pageSize")


def debug_connection_views(base):
    view = Blueprint("debug_connection_views", __name__)

    @view.route("/debug/connection-views/<table_name>", methods=["POST"])
    def post_model_by_connection_id_query(table_name):
        model = get_model_by_tablename(base, table_name)
        if not model:
            return Response(status=404)
        try:
            payload = RequestSchema().loads(request.data)
        except (ValidationError, JSONDecodeError):
            raise APIException(status=422, title="Request body has invalid json")

        raw_query = payload.get("query")
        query = snakify(raw_query)

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
                {"meta": {"query": raw_query}, "data": result_values}, default=str
            ),
            status=200,
            mimetype="application/json",
        )

    return view
