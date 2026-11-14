import asyncio
import random
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from nanobot.bus.delivery import ChannelNotReadyError
from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels import manager as manager_module
from nanobot.channels.manager import ChannelManager
from nanobot.config.schema import Config


def make_manager(tmp_path):
    config = Config.model_validate({"channels": {"websocket": {"enabled": False}}})
    return ChannelManager(config, MessageBus(), config_path=tmp_path / "config.json")


async def test_manager_equal_jitter_uses_capped_retry_delays(tmp_path, monkeypatch):
    manager = make_manager(tmp_path)
    manager.config.channels.send_max_retries = 6
    channel = SimpleNamespace(send=AsyncMock(side_effect=OSError("offline")),
                              should_retry_send_error=Mock(return_value=True))
    uniform = Mock(side_effect=lambda lower, upper: (lower + upper) / 2)
    monkeypatch.setattr(random, "uniform", uniform)
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    await manager._send_with_retry(channel, OutboundMessage("test", "1", "result"))
    assert [call.args for call in uniform.call_args_list] == [(0.5, 1), (1.0, 2), (2.0, 4), (2.0, 4), (2.0, 4)]
    assert [call.args[0] for call in sleep.await_args_list] == [0.75, 1.5, 3, 3, 3]


async def test_manager_deadline_clamps_jitter_and_keeps_pre_submit_retry(tmp_path, monkeypatch):
    manager = make_manager(tmp_path)
    manager.config.channels.send_max_retries = 1
    channel = SimpleNamespace(send=AsyncMock(side_effect=[ChannelNotReadyError("starting"), None]),
                              should_retry_send_error=Mock(return_value=True))
    monkeypatch.setattr(manager_module, "_SEND_RETRY_DELAYS", (4,))
    monkeypatch.setattr(random, "uniform", lambda lower, upper: upper)
    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    await manager._send_with_retry(channel, OutboundMessage("test", "1", "result"),
                                   deadline=asyncio.get_running_loop().time() + 2)
    assert channel.send.await_count == 2
    assert 0 < sleep.await_args.args[0] <= 2
