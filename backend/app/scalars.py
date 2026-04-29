from datetime import datetime

from graphql.language import ast as graphql_ast
from ariadne import ScalarType

# ---------------------------------------------------------------------------
# DateTime scalar
# ---------------------------------------------------------------------------
datetime_scalar = ScalarType("DateTime")


@datetime_scalar.serializer
def serialize_datetime(value: datetime) -> str:
    return value.isoformat()


@datetime_scalar.value_parser
def parse_datetime(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid DateTime: {value!r}. Expected ISO 8601 string.")
    if dt.tzinfo is None:
        raise ValueError(
            f"DateTime must include timezone info (e.g. 2026-05-01T08:00:00+00:00), got: {value!r}"
        )
    return dt


@datetime_scalar.literal_parser
def parse_datetime_literal(ast_value, variable_values=None) -> datetime:
    if isinstance(ast_value, graphql_ast.StringValueNode):
        return parse_datetime(ast_value.value)
    raise ValueError(f"DateTime must be a string literal, got: {ast_value!r}")


# ---------------------------------------------------------------------------
# Percentage scalar  (0 – 100 inclusive)
# ---------------------------------------------------------------------------
percentage_scalar = ScalarType("Percentage")


@percentage_scalar.value_parser
def parse_percentage(value) -> float:
    try:
        pct = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Percentage must be a number, got: {value!r}")
    if not 0.0 <= pct <= 100.0:
        raise ValueError(f"Percentage must be between 0 and 100, got: {pct}")
    return pct


@percentage_scalar.literal_parser
def parse_percentage_literal(ast_value, variable_values=None) -> float:
    if isinstance(ast_value, (graphql_ast.IntValueNode, graphql_ast.FloatValueNode)):
        return parse_percentage(float(ast_value.value))
    raise ValueError(f"Percentage must be a numeric literal, got: {ast_value!r}")


@percentage_scalar.serializer
def serialize_percentage(value) -> float:
    return float(value)
