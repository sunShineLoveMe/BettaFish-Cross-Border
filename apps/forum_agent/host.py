"""Task-aware forum host orchestration utilities.

This module augments the existing :mod:`ForumEngine.llm_host` helpers with
orchestration logic that can re-order sub-agent execution based on task tags
(e.g. "黑五爆款").
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

try:
    from ForumEngine.llm_host import ForumHost
except Exception:  # pragma: no cover - optional dependency for orchestration only
    ForumHost = None  # type: ignore

AgentHandler = Callable[[str, Sequence[str]], Any]


class TaskAwareForumHost:
    """Coordinate forum sub-agents according to task tags.

    Parameters
    ----------
    host:
        Optional ``ForumHost`` instance from :mod:`ForumEngine.llm_host`. If
        provided, the instance is made available through :pyattr:`base_host`
        so downstream code can still access the LLM-powered hosting features.
    default_agent_order:
        Fallback order to apply when no tag-specific overrides are found.
    tag_agent_priority:
        Mapping from tag name to a preferred execution order. Keys are treated
        case-sensitively to honour Chinese task labels such as ``"黑五爆款"``.
    """

    DEFAULT_AGENT_ORDER: Tuple[str, ...] = ("INSIGHT", "MEDIA", "QUERY")
    DEFAULT_TAG_AGENT_PRIORITY: Mapping[str, Sequence[str]] = {
        "黑五爆款": ("MEDIA", "QUERY", "INSIGHT"),
        "黑五选品": ("INSIGHT", "MEDIA", "QUERY"),
        "供应链抓取": ("QUERY", "INSIGHT", "MEDIA"),
        "渠道可行性": ("QUERY", "MEDIA", "INSIGHT"),
    }

    def __init__(
        self,
        host: Optional[ForumHost] = None,
        *,
        default_agent_order: Optional[Sequence[str]] = None,
        tag_agent_priority: Optional[Mapping[str, Sequence[str]]] = None,
    ) -> None:
        self.base_host = host
        self._agent_handlers: Dict[str, AgentHandler] = {}

        order = default_agent_order or self.DEFAULT_AGENT_ORDER
        self.default_agent_order: Tuple[str, ...] = tuple(agent.upper() for agent in order)

        combined_priority: MutableMapping[str, Tuple[str, ...]] = {
            tag: tuple(agent.upper() for agent in agents)
            for tag, agents in self.DEFAULT_TAG_AGENT_PRIORITY.items()
        }
        if tag_agent_priority:
            for tag, agents in tag_agent_priority.items():
                combined_priority[tag] = tuple(agent.upper() for agent in agents)
        self.tag_agent_priority: Dict[str, Tuple[str, ...]] = dict(combined_priority)

    # ------------------------------------------------------------------
    # Agent registration helpers
    # ------------------------------------------------------------------
    def register_agent(self, name: str, handler: AgentHandler) -> None:
        """Register a callable to handle execution for ``name``.

        The handler receives the task description and the sequence of active
        tags. Agent names are normalised to upper-case to match log labels.
        """

        self._agent_handlers[name.upper()] = handler

    def unregister_agent(self, name: str) -> None:
        """Remove a previously registered agent handler if it exists."""

        self._agent_handlers.pop(name.upper(), None)

    # ------------------------------------------------------------------
    # Tag configuration
    # ------------------------------------------------------------------
    def update_tag_priority(self, tag: str, agent_order: Sequence[str]) -> None:
        """Override or define the execution order for ``tag``.

        Parameters
        ----------
        tag:
            Task label (e.g. ``"黑五爆款"``).
        agent_order:
            Sequence of agent identifiers in desired execution order.
        """

        self.tag_agent_priority[tag] = tuple(agent.upper() for agent in agent_order)

    # ------------------------------------------------------------------
    # Planning utilities
    # ------------------------------------------------------------------
    def plan_agent_sequence(self, task_tags: Sequence[str]) -> List[str]:
        """Produce the agent execution order for the supplied ``task_tags``."""

        planned: "OrderedDict[str, None]" = OrderedDict()
        for raw_tag in task_tags:
            tag = raw_tag.strip()
            if not tag:
                continue
            order = self._match_tag_order(tag)
            if not order:
                continue
            for agent in order:
                planned.setdefault(agent, None)

        for agent in self.default_agent_order:
            planned.setdefault(agent, None)

        return list(planned.keys())

    def _match_tag_order(self, tag: str) -> Optional[Tuple[str, ...]]:
        """Return the configured order for ``tag`` using fuzzy matching."""

        if tag in self.tag_agent_priority:
            return self.tag_agent_priority[tag]

        for candidate, order in self.tag_agent_priority.items():
            if tag in candidate or candidate in tag:
                return order
        return None

    # ------------------------------------------------------------------
    # Execution helper
    # ------------------------------------------------------------------
    def execute_agents(self, task_description: str, task_tags: Sequence[str]) -> List[Tuple[str, Any]]:
        """Execute registered agents following the computed task order.

        Returns a list of ``(agent_name, result)`` tuples for successful calls.
        Unregistered agents in the computed order are skipped gracefully.
        """

        execution_order = self.plan_agent_sequence(task_tags)
        results: List[Tuple[str, Any]] = []
        for agent_name in execution_order:
            handler = self._agent_handlers.get(agent_name)
            if not handler:
                continue
            result = handler(task_description, task_tags)
            results.append((agent_name, result))
        return results

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def describe_execution(self, task_tags: Sequence[str]) -> str:
        """Return a human-readable summary of the execution order."""

        order = self.plan_agent_sequence(task_tags)
        if not order:
            return "未找到可执行的 Agent 顺序。"
        tags_display = ", ".join(task_tags) if task_tags else "默认"
        agents_display = " → ".join(order)
        return f"任务标签：{tags_display}\n调用顺序：{agents_display}"

    def available_agents(self) -> List[str]:
        """List registered agent identifiers."""

        return sorted(self._agent_handlers.keys())


__all__ = ["TaskAwareForumHost", "AgentHandler"]
