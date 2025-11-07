from apps.forum_agent import TaskAwareForumHost


def test_plan_sequence_defaults_to_base_order():
    host = TaskAwareForumHost()
    assert host.plan_agent_sequence([]) == list(host.default_agent_order)


def test_black_friday_tag_overrides_order():
    host = TaskAwareForumHost()
    sequence = host.plan_agent_sequence(["黑五爆款"])
    assert sequence[:3] == list(host.tag_agent_priority["黑五爆款"])
    assert set(sequence) == {"INSIGHT", "MEDIA", "QUERY"}


def test_custom_tag_priority_and_execution():
    host = TaskAwareForumHost()
    host.update_tag_priority("供应链抓取", ["QUERY", "INSIGHT"])

    calls = []

    def _make_handler(name):
        def _handler(task_desc: str, tags):
            calls.append((name, task_desc, tuple(tags)))
            return f"{name}-done"

        return _handler

    host.register_agent("INSIGHT", _make_handler("INSIGHT"))
    host.register_agent("MEDIA", _make_handler("MEDIA"))
    host.register_agent("QUERY", _make_handler("QUERY"))

    results = host.execute_agents("测试任务", ["供应链抓取", "黑五爆款"])

    planned = host.plan_agent_sequence(["供应链抓取", "黑五爆款"])
    assert [name for name, _ in results] == planned[: len(results)]
    assert [name for name, *_ in calls] == [name for name, _ in results]
    assert all(result.endswith("-done") for _, result in results)



