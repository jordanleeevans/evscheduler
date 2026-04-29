import os
from fastapi import FastAPI
from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from starlette.requests import Request
from app.resolvers.query import query, vehicle_type, charging_session_type, charging_slot_type, datetime_scalar
from app.resolvers.mutation import mutation
from app.database import engine, Base, SessionLocal

app = FastAPI(title="EV Scheduler API")

schema_path = os.path.join(os.path.dirname(__file__), "schema.graphql")
type_defs = load_schema_from_path(schema_path)
schema = make_executable_schema(type_defs, query, mutation, vehicle_type, charging_session_type, charging_slot_type, datetime_scalar, convert_names_case=True)


async def get_context(request: Request, data):
    """Provide DB session in GraphQL context."""
    return {"request": request, "db": SessionLocal()}


graphql_app = GraphQL(schema, debug=True, context_value=get_context)
app.mount("/graphql", graphql_app)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
