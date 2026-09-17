# smolagents memory / tool 中文教学注释版

> **固定版本**：`huggingface/smolagents` @ `30bb1161095dbae2271e6bc3cc4c219cc3897a57`。以下是与主 Agent loop 直接相关的教学摘录；原始语句保持不变，只添加注释。

## 1. `ActionStep.to_messages()` — 把动作和观察变成下一轮上下文（原始 `memory.py:92–150`）

这段是 Agent loop 的信息回流点：模型输出、tool call、工具 observation 和错误被编码成消息，下一次 `write_memory_to_messages()` 会再次读取它们。

~~~python
    # 【中文教学注释】将结构化的 action step 转换为下一轮 LLM 输入；这里决定哪些历史会被模型看见。
    def to_messages(self, summary_mode: bool = False) -> list[ChatMessage]:
        messages = []
        # 【中文教学注释】保留模型上一轮的文字输出，作为后续决策的上下文。
        if self.model_output is not None and not summary_mode:
            messages.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=[{"type": "text", "text": self.model_output.strip()}])
            )

        # 【中文教学注释】显式记录模型请求了哪些工具和参数。
        if self.tool_calls is not None:
            messages.append(
                ChatMessage(
                    role=MessageRole.TOOL_CALL,
                    content=[
                        {
                            "type": "text",
                            "text": "Calling tools:\n" + str([tc.dict() for tc in self.tool_calls]),
                        }
                    ],
                )
            )

        if self.observations_images:
            messages.append(
                ChatMessage(
                    role=MessageRole.USER,
                    content=[
                        {
                            "type": "image",
                            "image": image,
                        }
                        for image in self.observations_images
                    ],
                )
            )

        # 【中文教学注释】把外部工具结果标记为 `Observation:`，形成 ReAct 的观察输入。
        if self.observations is not None:
            messages.append(
                ChatMessage(
                    role=MessageRole.TOOL_RESPONSE,
                    content=[
                        {
                            "type": "text",
                            "text": f"Observation:\n{self.observations}",
                        }
                    ],
                )
            )
        # 【中文教学注释】错误也进入模型上下文，并提示重试时避免重复错误。
        if self.error is not None:
            error_message = (
                "Error:\n"
                + str(self.error)
                + "\nNow let's retry: take care not to repeat previous errors! If you have retried several times, try a completely different approach.\n"
            )
            message_content = f"Call id: {self.tool_calls[0].id}\n" if self.tool_calls else ""
            message_content += error_message
            messages.append(
                ChatMessage(role=MessageRole.TOOL_RESPONSE, content=[{"type": "text", "text": message_content}])
            )

        # 【中文教学注释】返回一组消息；这是 working context 的构造，不是长期记忆检索系统。
        return messages
~~~

## 2. `AgentMemory` — 运行时轨迹容器（原始 `memory.py:214–246`）

`AgentMemory` 本身很简单：一个 system prompt 加一个有序 steps 列表。它提供序列化与 replay，但没有自动的跨会话持久化或语义检索。

~~~python
# 【中文教学注释】运行时 memory 的职责是保留本次 Agent trajectory，供上下文重建和调试。
class AgentMemory:
    """Memory for the agent, containing the system prompt and all steps taken by the agent.

    This class is used to store the agent's steps, including tasks, actions, and planning steps.
    It allows for resetting the memory, retrieving succinct or full step information, and replaying the agent's steps.

    Args:
        system_prompt (`str`): System prompt for the agent, which sets the context and instructions for the agent's behavior.

    **Attributes**:
        - **system_prompt** (`SystemPromptStep`) -- System prompt step for the agent.
        - **steps** (`list[TaskStep | ActionStep | PlanningStep]`) -- List of steps taken by the agent, which can include tasks, actions, and planning steps.
    """

    # 【中文教学注释】初始化 system prompt 与空的 steps 列表。
    def __init__(self, system_prompt: str):
        self.system_prompt: SystemPromptStep = SystemPromptStep(system_prompt=system_prompt)
        self.steps: list[TaskStep | ActionStep | PlanningStep] = []

    # 【中文教学注释】清空历史步骤；调用者可以在新任务前选择重置。
    def reset(self):
        """Reset the agent's memory, clearing all steps and keeping the system prompt."""
        self.steps = []

    # 【中文教学注释】提供去掉模型输入消息的紧凑表示，便于记录或展示。
    def get_succinct_steps(self) -> list[dict]:
        """Return a succinct representation of the agent's steps, excluding model input messages."""
        return [
            {key: value for key, value in step.dict().items() if key != "model_input_messages"} for step in self.steps
        ]

    # 【中文教学注释】提供完整 step 结构，包含模型输入消息。
    def get_full_steps(self) -> list[dict]:
        """Return a full representation of the agent's steps, including model input messages."""
        if len(self.steps) == 0:
            return []
        return [step.dict() for step in self.steps]
~~~

## 3. `Tool` 的声明边界（原始 `tools.py:106–178`）

工具不是提示词里的一个名字，而是带有描述、输入 schema、输出类型和 callable 行为的 runtime 对象。模型只能请求已注册的工具，真正执行仍由 Agent runtime 负责。

~~~python
# 【中文教学注释】`Tool` 是可被 Agent 调用的能力声明与执行对象。
class Tool(BaseTool):
    """
    A base class for the functions used by the agent. Subclass this and implement the `forward` method as well as the
    following class attributes:

    - **description** (`str`) -- A short description of what your tool does, the inputs it expects and the output(s) it
      will return. For instance 'This is a tool that downloads a file from a `url`. It takes the `url` as input, and
      returns the text contained in the file'.
    - **name** (`str`) -- A performative name that will be used for your tool in the prompt to the agent. For instance
      `"text-classifier"` or `"image_generator"`.
    - **inputs** (`Dict[str, Dict[str, Union[str, type, bool]]]`) -- The dict of modalities expected for the inputs.
      It has one `type`key and a `description`key.
      This is used by `launch_gradio_demo` or to make a nice space from your tool, and also can be used in the generated
      description for your tool.
    - **output_type** (`type`) -- The type of the tool output. This is used by `launch_gradio_demo`
      or to make a nice space from your tool, and also can be used in the generated description for your tool.
    - **output_schema** (`Dict[str, Any]`, *optional*) -- The JSON schema defining the expected structure of the tool output.
      This can be included in system prompts to help agents understand the expected output format. Note: This is currently
      used for informational purposes only and does not perform actual output validation.

    You can also override the method [`~Tool.setup`] if your tool has an expensive operation to perform before being
    usable (such as loading a model). [`~Tool.setup`] will be called the first time you use your tool, but not at
    instantiation.
    """

    # 【中文教学注释】名称既用于注册/查找，也会暴露给模型作为调用目标。
    name: str
    # 【中文教学注释】描述帮助模型理解何时使用工具；它是协议的一部分，不是执行器本身。
    description: str
    # 【中文教学注释】输入 schema 为参数校验和模型工具描述提供边界。
    inputs: dict[str, dict[str, str | type | bool]]
    output_type: str
    output_schema: dict[str, Any] | None = None

    # 【中文教学注释】初始化工具但不立即执行昂贵 setup；执行生命周期由 runtime 管理。
    def __init__(self, *args, **kwargs):
        self.is_initialized = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        validate_after_init(cls)

    # 【中文教学注释】在工具真正运行前校验声明、输入和 forward 签名，减少模型生成的非法调用。
    def validate_arguments(self):
        required_attributes = {
            "description": str,
            "name": str,
            "inputs": dict,
            "output_type": str,
        }
        # Validate class attributes
        for attr, expected_type in required_attributes.items():
            attr_value = getattr(self, attr, None)
            if attr_value is None:
                raise TypeError(f"You must set an attribute {attr}.")
            if not isinstance(attr_value, expected_type):
                raise TypeError(
                    f"Attribute {attr} should have type {expected_type.__name__}, got {type(attr_value)} instead."
                )

        # Validate optional output_schema attribute
        output_schema = getattr(self, "output_schema", None)
        if output_schema is not None and not isinstance(output_schema, dict):
            raise TypeError(f"Attribute output_schema should have type dict, got {type(output_schema)} instead.")

        # - Validate name
        if not is_valid_name(self.name):
            raise Exception(
                f"Invalid Tool name '{self.name}': must be a valid Python identifier and not a reserved keyword"
            )
        # Validate inputs
        for input_name, input_content in self.inputs.items():
            assert isinstance(input_content, dict), f"Input '{input_name}' should be a dictionary."
            assert "type" in input_content and "description" in input_content, (
                f"Input '{input_name}' should have keys 'type' and 'description', has only {list(input_content.keys())}."
            )
            # Get input_types as a list, whether from a string or list
            if isinstance(input_content["type"], str):
~~~

## 与主循环的关系

`agents.py` 负责决定何时调用模型和工具；本文件展示 `ActionStep` 如何把结果变成下一轮上下文，以及 `AgentMemory` 如何保存步骤。`tools.py` 展示工具声明与验证边界。
