from collections.abc import Callable, Mapping
from typing import Self

from langgraph.graph.state import CompiledStateGraph

START: str
END: str

class StateGraph[StateT, ContextT, InputT, OutputT]:
    def __init__(self, *, state_schema: type[StateT]) -> None: ...
    def add_node(
        self,
        name: str,
        action: Callable[[StateT], Mapping[str, object]],
    ) -> Self: ...
    def add_edge(self, start_key: str, end_key: str) -> Self: ...
    def add_conditional_edges(
        self,
        source: str,
        path: Callable[[StateT], str],
    ) -> Self: ...
    def compile(self) -> CompiledStateGraph[StateT, ContextT, InputT, OutputT]: ...
