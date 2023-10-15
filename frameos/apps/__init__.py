import re
from dataclasses import dataclass
from typing import Dict, Optional, Any, Callable, List
from PIL.Image import Image

# NOTE: This file is read by both the frame and the controller. Don't import anything too funky.

@dataclass
class ConfigField:
    name: str
    type: str
    required: Optional[bool] = False
    secret: Optional[bool] = False
    options: Optional[List[str]] = None
    value: Optional[Any] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None

@dataclass
class AppConfig:
    keyword: str
    name: Optional[str]
    config: Optional[Dict]
    description: Optional[str]
    version: Optional[str]
    fields: Optional[List[ConfigField]]

@dataclass
class Edge:
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

@dataclass
class Node:
    id: str
    type: str
    data: Dict
    # skipping less relevant fields


@dataclass
class FrameConfigScene:
    id: str
    nodes: List[Node]
    edges: List[Edge]


@dataclass
class FrameConfig:
    status: str
    version: str
    width: int
    height: int
    device: str
    color: str
    interval: float
    scaling_mode: str
    background_color: str
    rotate: int
    scenes: List[FrameConfigScene]

@dataclass
class ExecutionContext:
    event: str
    payload: Dict
    image: Optional[Image]
    state: Dict
    apps_ran: List[str]
    apps_errored: List[str]

class App:
    def __init__(
            self,
            keyword: str,
            config: Dict,
            frame_config: FrameConfig,
            log_function: Callable[[Dict], Any],
            rerender_function: Callable[[str], None],
            node: Node,
    ) -> None:
        self.frame_config = frame_config
        self.config = config
        self.keyword = keyword
        self.log_function = log_function
        self.rerender_function = rerender_function
        self.node: Node = node
        self.__post_init__()

    def __post_init__(self):
        pass

    def rerender(self, trigger = None):
        self.rerender_function(self.keyword if trigger is None else trigger)

    def log(self, message: str):
        if self.log_function:
            self.log_function({ "event": f"{self.keyword}:log", "message": message })
        
    def error(self, message: str):
        if self.log_function:
            self.log_function({ "event": f"{self.keyword}:error", "message": message })

    def run(self, payload: ExecutionContext):
        pass

    def get_config(self, state: Dict, key: str, default = None):
        text = self.config.get(key, default)
        # self.log(f"get_config: {key} --> {text}")
        return self.parse_str(text, state)

    def parse_str(self, text: str, state: Dict):
        def replace_with_state_value(match):
            keys = match.group(1).split('.')
            value = state
            for key in keys:
                try:
                    value = value[key]
                except (KeyError, TypeError):
                    return ''
            return str(value)
        return re.sub(r'{([^}]+)}', replace_with_state_value, text)

