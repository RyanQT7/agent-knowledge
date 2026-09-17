# smolagents 核心源码中文教学注释版

> **固定版本**：`huggingface/smolagents` @ `30bb1161095dbae2271e6bc3cc4c219cc3897a57`。
>
> 这是从原始 `src/smolagents/agents.py` 选取的教学摘录，不是可替换的完整模块；原始语句保持不变，只加入 `# 【中文教学注释】`。原文件仍在被忽略的 `sources/code/` 中。

### 1. `MultiStepAgent.run()` — 初始化一次任务（原始 `agents.py:436–538`）

`run()` 不是模型调用本身：它建立 task、state、memory 和 executor 上下文，再把控制权交给 `_run_stream()`。下面保留原始可执行语句，只插入教学注释。

~~~python
    # 【中文教学注释】`run()` 是公开入口；调用者从这里把用户任务交给运行时。
    def run(
        self,
        task: str,
        stream: bool = False,
        reset: bool = True,
        images: list["PIL.Image.Image"] | None = None,
        additional_args: dict | None = None,
        max_steps: int | None = None,
        return_full_result: bool | None = None,
    ) -> Any | RunResult:
        """
        Run the agent for the given task.

        Args:
            task (`str`): Task to perform.
            stream (`bool`): Whether to run in streaming mode.
                If `True`, returns a generator that yields each step as it is executed. You must iterate over this generator to process the individual steps (e.g., using a for loop or `next()`).
                If `False`, executes all steps internally and returns only the final answer after completion.
            reset (`bool`): Whether to reset the conversation or keep it going from previous run.
            images (`list[PIL.Image.Image]`, *optional*): Image(s) objects.
            additional_args (`dict`, *optional*): Any other variables that you want to pass to the agent run, for instance images or dataframes. Give them clear names!
            max_steps (`int`, *optional*): Maximum number of steps the agent can take to solve the task. if not provided, will use the agent's default value.
            return_full_result (`bool`, *optional*): Whether to return the full [`RunResult`] object or just the final answer output.
                If `None` (default), the agent's `self.return_full_result` setting is used.

        Example:
        ```py
        from smolagents import CodeAgent
        agent = CodeAgent(tools=[])
        agent.run("What is the result of 2 power 3.7384?")
        ```
        """
        # 【中文教学注释】先确定本次运行的步数上限，防止后续循环无限持续。
        max_steps = max_steps or self.max_steps
        self.task = task
        self.interrupt_switch = False
        if additional_args:
            # 【中文教学注释】`additional_args` 进入运行时 state；它是任务内共享值，不自动等于长期记忆。
            self.state.update(additional_args)
            self.task += f"""
You have been provided with these additional arguments, that you can access directly using the keys as variables:
{str(additional_args)}."""

        # 【中文教学注释】把当前 system prompt 写入 memory，保证后续模型消息有一致的指令上下文。
        self.memory.system_prompt = SystemPromptStep(system_prompt=self.system_prompt)
        if reset:
            self.memory.reset()
            self.monitor.reset()

        self.logger.log_task(
            content=self.task.strip(),
            subtitle=f"{type(self.model).__name__} - {(self.model.model_id if hasattr(self.model, 'model_id') else '')}",
            level=LogLevel.INFO,
            title=self.name if hasattr(self, "name") else None,
        )
        # 【中文教学注释】先记录用户任务，后续 action/observation 会追加到同一条 trajectory。
        self.memory.steps.append(TaskStep(task=self.task, task_images=images))

        if getattr(self, "python_executor", None):
            self.python_executor.send_variables(variables=self.state)
            self.python_executor.send_tools({**self.tools, **self.managed_agents})

        if stream:
            # The steps are returned as they are executed through a generator to iterate on.
            # 【中文教学注释】真正的多步执行从 `_run_stream()` 开始，而不是在这里一次完成。
            return self._run_stream(task=self.task, max_steps=max_steps, images=images)

        run_start_time = time.time()
        # 【中文教学注释】非流式模式只是把同一条生成器路径消费完，再取最终答案。
        steps = list(self._run_stream(task=self.task, max_steps=max_steps, images=images))

        # Outputs are returned only at the end. We only look at the last step.
        assert isinstance(steps[-1], FinalAnswerStep)
        output = steps[-1].output

        return_full_result = return_full_result if return_full_result is not None else self.return_full_result
        if return_full_result:
            total_input_tokens = 0
            total_output_tokens = 0
            correct_token_usage = True
            for step in self.memory.steps:
                if isinstance(step, (ActionStep, PlanningStep)):
                    if step.token_usage is None:
                        correct_token_usage = False
                        break
                    else:
                        total_input_tokens += step.token_usage.input_tokens
                        total_output_tokens += step.token_usage.output_tokens
            if correct_token_usage:
                token_usage = TokenUsage(input_tokens=total_input_tokens, output_tokens=total_output_tokens)
            else:
                token_usage = None

            if self.memory.steps and isinstance(getattr(self.memory.steps[-1], "error", None), AgentMaxStepsError):
                state = "max_steps_error"
            else:
                state = "success"

            step_dicts = self.memory.get_full_steps()

            return RunResult(
                output=output,
                token_usage=token_usage,
                steps=step_dicts,
                timing=Timing(start_time=run_start_time, end_time=time.time()),
                state=state,
            )

        # 【中文教学注释】返回最终答案；完整轨迹可通过 `RunResult` 暴露。
        return output
~~~

### 2. `MultiStepAgent._run_stream()` — Agent 主循环（原始 `agents.py:540–611`）

这里是最小完整 Agent loop：可选计划 → 一个 action step → 保存结果 → 继续或结束。`max_steps` 是明确的停止边界。

~~~python
    # 【中文教学注释】这是 runtime 的主控制循环；子类只负责实现单步如何解释模型输出。
    def _run_stream(
        self, task: str, max_steps: int, images: list["PIL.Image.Image"] | None = None
    ) -> Generator[ActionStep | PlanningStep | FinalAnswerStep | ChatMessageStreamDelta]:
        # 【中文教学注释】每次 `run()` 的 action step 从 1 开始编号。
        self.step_number = 1
        returned_final_answer = False
        # 【中文教学注释】循环同时受最终答案和 `max_steps` 约束，避免只依赖模型自觉停止。
        while not returned_final_answer and self.step_number <= max_steps:
            # 【中文教学注释】外部 interrupt 可以在下一次循环检查时中止运行。
            if self.interrupt_switch:
                raise AgentError("Agent interrupted.", self.logger)

            # Run a planning step if scheduled
            # 【中文教学注释】planning 是可选、按间隔插入的步骤，不是独立强制 Planner 架构。
            if self.planning_interval is not None and (
                self.step_number == 1 or (self.step_number - 1) % self.planning_interval == 0
            ):
                planning_start_time = time.time()
                planning_step = None
                for element in self._generate_planning_step(
                    task, is_first_step=len(self.memory.steps) == 1, step=self.step_number
                ):  # Don't use the attribute step_number here, because there can be steps from previous runs
                    yield element
                    planning_step = element
                assert isinstance(planning_step, PlanningStep)  # Last yielded element should be a PlanningStep
                planning_end_time = time.time()
                planning_step.timing = Timing(
                    start_time=planning_start_time,
                    end_time=planning_end_time,
                )
                self._finalize_step(planning_step)
                self.memory.steps.append(planning_step)

            # Start action step!
            action_step_start_time = time.time()
            # 【中文教学注释】为本轮创建结构化记录，供模型输出、tool call、observation 和错误写入。
            action_step = ActionStep(
                step_number=self.step_number,
                timing=Timing(start_time=action_step_start_time),
                observations_images=images,
            )
            self.logger.log_rule(f"Step {self.step_number}", level=LogLevel.INFO)
            try:
                # 【中文教学注释】把一步的具体实现交给 `ToolCallingAgent` 或 `CodeAgent`。
                for output in self._step_stream(action_step):
                    # Yield all
                    yield output

                    # 【中文教学注释】只有 action 实现明确产出 final answer，runtime 才把 loop 标记为完成。
                    if isinstance(output, ActionOutput) and output.is_final_answer:
                        final_answer = output.output
                        self.logger.log(
                            Text(f"Final answer: {final_answer}", style=f"bold {YELLOW_HEX}"),
                            level=LogLevel.INFO,
                        )

                        if self.final_answer_checks:
                            self._validate_final_answer(final_answer)
                        returned_final_answer = True
                        action_step.is_final_answer = True

            except AgentGenerationError as e:
                # Agent generation errors are not caused by a Model error but an implementation error: so we should raise them and exit.
                raise e
            except AgentError as e:
                # Other AgentError types are caused by the Model, so we should log them and iterate.
                action_step.error = e
            # 【中文教学注释】无论成功还是可恢复 AgentError，都要结束本步并写入 memory。
            finally:
                self._finalize_step(action_step)
                self.memory.steps.append(action_step)
                yield action_step
                self.step_number += 1

        # 【中文教学注释】达到上限后走专门的 max-step 处理，而不是静默无限重试。
        if not returned_final_answer and self.step_number == max_steps + 1:
            final_answer = self._handle_max_steps_reached(task)
            yield action_step
        # 【中文教学注释】统一包装最后输出，给 `run()` 一个稳定的最终结果节点。
        final_answer_step = FinalAnswerStep(handle_agent_output_types(final_answer))
        self._finalize_step(final_answer_step)
        yield final_answer_step
~~~

### 3. `write_memory_to_messages()` / `step()` — 把轨迹重新送回模型（原始 `agents.py:758–787`）

smolagents 的 memory 在这条路径上主要是运行时 trajectory/context：它把过去步骤序列化成下一次模型输入。

~~~python
    # 【中文教学注释】把已有 system prompt 和步骤转换成模型能够消费的消息列表。
    def write_memory_to_messages(
        self,
        summary_mode: bool = False,
    ) -> list[ChatMessage]:
        """
        Reads past llm_outputs, actions, and observations or errors from the memory into a series of messages
        that can be used as input to the LLM. Adds a number of keywords (such as PLAN, error, etc) to help
        the LLM.
        """
        # 【中文教学注释】system prompt 是上下文的第一部分。
        messages = self.memory.system_prompt.to_messages(summary_mode=summary_mode)
        # 【中文教学注释】按时间顺序重放 task、plan、action、tool call、observation 和 error。
        for memory_step in self.memory.steps:
            messages.extend(memory_step.to_messages(summary_mode=summary_mode))
        # 【中文教学注释】返回的是当前运行上下文，不是自动持久化到外部数据库的长期记忆。
        return messages

    # 【中文教学注释】单步协议由子类实现：这里定义接口，不决定具体是 structured tool call 还是代码动作。
    def _step_stream(
        self, memory_step: ActionStep
    ) -> Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput]:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Yields ChatMessageStreamDelta during the run if streaming is enabled.
        At the end, yields either None if the step is not final, or the final answer.
        """
        raise NotImplementedError("This method should be implemented in child classes")

    # 【中文教学注释】同步辅助入口消费单步生成器的最后一个结果。
    def step(self, memory_step: ActionStep) -> Any:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Returns either None if the step is not final, or the final answer.
        """
        return list(self._step_stream(memory_step))[-1]
~~~

### 4. `ToolCallingAgent._step_stream()` — LLM 决策与 ReAct 单步（原始 `agents.py:1276–1359`）

这一段把模型输出接到 tool protocol：先提供完整历史，模型生成 tool call，再交给 `process_tool_calls()`；工具返回后，本轮 observation 写入 `ActionStep`，下一轮再读回。

~~~python
    # 【中文教学注释】ToolCallingAgent 的单步实现：模型决定调用哪些工具，或调用 `final_answer`。
    def _step_stream(
        self, memory_step: ActionStep
    ) -> Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput]:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Yields ChatMessageStreamDelta during the run if streaming is enabled.
        At the end, yields either None if the step is not final, or the final answer.
        """
        # 【中文教学注释】每一轮先重建上下文，因此 observation 能影响下一次决策。
        memory_messages = self.write_memory_to_messages()

        input_messages = memory_messages.copy()

        # Add new step in logs
        memory_step.model_input_messages = input_messages

        try:
            if self.stream_outputs and hasattr(self.model, "generate_stream"):
                output_stream = self.model.generate_stream(
                    input_messages,
                    stop_sequences=["Observation:", "Calling tools:"],
                    tools_to_call_from=self.tools_and_managed_agents,
                )

                chat_message_stream_deltas: list[ChatMessageStreamDelta] = []
                with Live("", console=self.logger.console, vertical_overflow="visible") as live:
                    for event in output_stream:
                        chat_message_stream_deltas.append(event)
                        live.update(
                            Markdown(agglomerate_stream_deltas(chat_message_stream_deltas).render_as_markdown())
                        )
                        yield event
                chat_message = agglomerate_stream_deltas(chat_message_stream_deltas)
            else:
                chat_message: ChatMessage = self.model.generate(
                    input_messages,
                    stop_sequences=["Observation:", "Calling tools:"],
                    tools_to_call_from=self.tools_and_managed_agents,
                )
                self.logger.log_markdown(
                    content=str(chat_message.content or chat_message.raw or ""),
                    title="Output message of the LLM:",
                    level=LogLevel.DEBUG,
                )

            # Record model output
            # 【中文教学注释】保留原始模型输出，便于调试、审计和下一步消息构建。
            memory_step.model_output_message = chat_message
            memory_step.model_output = chat_message.content
            memory_step.token_usage = chat_message.token_usage
        except Exception as e:
            raise AgentGenerationError(f"Error while generating output:\n{e}", self.logger) from e

        if chat_message.tool_calls is None or len(chat_message.tool_calls) == 0:
            try:
                chat_message = self.model.parse_tool_calls(chat_message)
            except Exception as e:
                raise AgentParsingError(f"Error while parsing tool call from model output: {e}", self.logger)
        else:
            for tool_call in chat_message.tool_calls:
                tool_call.function.arguments = parse_json_if_needed(tool_call.function.arguments)
        final_answer, got_final_answer = None, False
        # 【中文教学注释】模型的 action 被交给真实工具执行器；返回值会以 `ToolOutput` 流回。
        for output in self.process_tool_calls(chat_message, memory_step):
            yield output
            if isinstance(output, ToolOutput):
                # 【中文教学注释】`final_answer` 是显式终止动作；普通 tool output 不会结束 loop。
                if output.is_final_answer:
                    if len(chat_message.tool_calls) > 1:
                        raise AgentExecutionError(
                            "If you want to return an answer, please do not perform any other tool calls than the final answer tool call!",
                            self.logger,
                        )
                    if got_final_answer:
                        raise AgentToolExecutionError(
                            "You returned multiple final answers. Please return only one single final answer!",
                            self.logger,
                        )
                    final_answer = output.output
                    got_final_answer = True

                    # Manage state variables
                    if isinstance(final_answer, str) and final_answer in self.state.keys():
                        final_answer = self.state[final_answer]
        # 【中文教学注释】本步向上层报告“是否完成”和答案，但 observation 已由工具处理逻辑写入 memory step。
        yield ActionOutput(
            output=final_answer,
            is_final_answer=got_final_answer,
        )
~~~

### 5. `process_tool_calls()` / `execute_tool_call()` — 工具、观察与错误（原始 `agents.py:1361–1502`）

这里是从模型 action 到环境结果的边界。参数校验、执行、异常包装和 observation 记录都发生在这层。

~~~python
    # 【中文教学注释】把模型返回的每个 tool call 转为 runtime 对象，并安排执行。
    def process_tool_calls(
        self, chat_message: ChatMessage, memory_step: ActionStep
    ) -> Generator[ToolCall | ToolOutput]:
        """Process tool calls from the model output and update agent memory.

        Args:
            chat_message (`ChatMessage`): Chat message containing tool calls from the model.
            memory_step (`ActionStep)`: Memory ActionStep to update with results.

        Yields:
            `ToolCall | ToolOutput`: The tool call or tool output.
        """
        parallel_calls: dict[str, ToolCall] = {}
        assert chat_message.tool_calls is not None
        for chat_tool_call in chat_message.tool_calls:
            tool_call = ToolCall(
                name=chat_tool_call.function.name, arguments=chat_tool_call.function.arguments, id=chat_tool_call.id
            )
            yield tool_call
            parallel_calls[tool_call.id] = tool_call

        # Helper function to process a single tool call
        # 【中文教学注释】单个工具调用在这里生成日志、执行结果和可供模型阅读的 observation。
        def process_single_tool_call(tool_call: ToolCall) -> ToolOutput:
            tool_name = tool_call.name
            tool_arguments = tool_call.arguments or {}
            self.logger.log(
                Panel(Text(f"Calling tool: '{tool_name}' with arguments: {tool_arguments}")),
                level=LogLevel.INFO,
            )
            # 【中文教学注释】真正的工具/managed agent 调用集中经过 `execute_tool_call()`。
            tool_call_result = self.execute_tool_call(tool_name, tool_arguments)
            tool_call_result_type = type(tool_call_result)
            if tool_call_result_type in [AgentImage, AgentAudio]:
                if tool_call_result_type == AgentImage:
                    observation_name = "image.png"
                elif tool_call_result_type == AgentAudio:
                    observation_name = "audio.mp3"
                # TODO: tool_call_result naming could allow for different names of same type
                self.state[observation_name] = tool_call_result
                observation = f"Stored '{observation_name}' in memory."
            else:
                # 【中文教学注释】工具返回值被规范成文本 observation；多模态结果可能先放入 state。
                observation = str(tool_call_result).strip()
            self.logger.log(
                f"Observations: {observation.replace('[', '|')}",  # escape potential rich-tag-like components
                level=LogLevel.INFO,
            )
            is_final_answer = tool_name == "final_answer"

            return ToolOutput(
                id=tool_call.id,
                output=tool_call_result,
                is_final_answer=is_final_answer,
                observation=observation,
                tool_call=tool_call,
            )

        # Process tool calls in parallel
        outputs = {}
        # 【中文教学注释】单个调用直接执行；多个调用可能并行执行，说明 action 层不必总是严格串行。
        if len(parallel_calls) == 1:
            # If there's only one call, process it directly
            tool_call = list(parallel_calls.values())[0]
            tool_output = process_single_tool_call(tool_call)
            outputs[tool_output.id] = tool_output
            yield tool_output
        else:
            # If multiple tool calls, process them in parallel
            with ThreadPoolExecutor(self.max_tool_threads) as executor:
                futures = []
                for tool_call in parallel_calls.values():
                    ctx = copy_context()
                    futures.append(executor.submit(ctx.run, process_single_tool_call, tool_call))
                for future in as_completed(futures):
                    tool_output = future.result()
                    outputs[tool_output.id] = tool_output
                    yield tool_output

        # 【中文教学注释】保存本轮 action，后续 `ActionStep.to_messages()` 会把它重放给模型。
        memory_step.tool_calls = [parallel_calls[k] for k in sorted(parallel_calls.keys())]
        memory_step.observations = memory_step.observations or ""
        for tool_output in [outputs[k] for k in sorted(outputs.keys())]:
            # 【中文教学注释】将工具结果合并成该步的 observation。
            memory_step.observations += tool_output.observation + "\n"
        memory_step.observations = (
            memory_step.observations.rstrip("\n") if memory_step.observations else memory_step.observations
        )

    def _substitute_state_variables(self, arguments: dict[str, str] | str) -> dict[str, Any] | str:
        """Replace string values in arguments with their corresponding state values if they exist."""
        if isinstance(arguments, dict):
            return {
                key: self.state.get(value, value) if isinstance(value, str) else value
                for key, value in arguments.items()
            }
        return arguments

    # 【中文教学注释】执行边界：检查名称、替换 state 引用、校验参数，再调用工具。
    def execute_tool_call(self, tool_name: str, arguments: dict[str, str] | str) -> Any:
        """
        Execute a tool or managed agent with the provided arguments.

        The arguments are replaced with the actual values from the state if they refer to state variables.

        Args:
            tool_name (`str`): Name of the tool or managed agent to execute.
            arguments (dict[str, str] | str): Arguments passed to the tool call.
        """
        # Check if the tool exists
        # 【中文教学注释】可调用集合由注册 tools 与 managed agents 构成；模型不能调用未注册名称。
        available_tools = {**self.tools, **self.managed_agents}
        if tool_name not in available_tools:
            # 【中文教学注释】异常被包装为 AgentError，外层 loop 可记录为 error 并把可恢复错误交回模型。
            raise AgentToolExecutionError(
                f"Unknown tool {tool_name}, should be one of: {', '.join(available_tools)}.", self.logger
            )

        # Get the tool and substitute state variables in arguments
        tool = available_tools[tool_name]
        arguments = self._substitute_state_variables(arguments)
        is_managed_agent = tool_name in self.managed_agents

        try:
            # 【中文教学注释】先做 schema/参数校验，把模型生成的错误与工具内部失败区分开。
            validate_tool_arguments(tool, arguments)
        except (ValueError, TypeError) as e:
            raise AgentToolCallError(str(e), self.logger) from e
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}' with arguments {str(arguments)}: {type(e).__name__}: {e}"
            # 【中文教学注释】异常被包装为 AgentError，外层 loop 可记录为 error 并把可恢复错误交回模型。
            raise AgentToolExecutionError(error_msg, self.logger) from e

        try:
            # Call tool with appropriate arguments
            if isinstance(arguments, dict):
                # 【中文教学注释】通过统一 callable 接口执行工具或 managed agent。
                return tool(**arguments) if is_managed_agent else tool(**arguments, sanitize_inputs_outputs=True)
            else:
                return tool(arguments) if is_managed_agent else tool(arguments, sanitize_inputs_outputs=True)

        except Exception as e:
            # Handle execution errors
            if is_managed_agent:
                error_msg = (
                    f"Error executing request to team member '{tool_name}' with arguments {str(arguments)}: {e}\n"
                    "Please try again or request to another team member"
                )
            else:
                error_msg = (
                    f"Error executing tool '{tool_name}' with arguments {str(arguments)}: {type(e).__name__}: {e}\n"
                    "Please try again or use another tool"
                )
            # 【中文教学注释】异常被包装为 AgentError，外层 loop 可记录为 error 并把可恢复错误交回模型。
            raise AgentToolExecutionError(error_msg, self.logger) from e
~~~

### 6. `CodeAgent._step_stream()` — Code-as-action 分支（原始 `agents.py:1638–1764`）

CodeAgent 复用同一 `MultiStepAgent` 主循环，但把模型输出解析成 Python 代码，再交给 Python executor；这不是普通函数式 tool calling。

~~~python
    # 【中文教学注释】CodeAgent 仍然实现同一个单步协议，但 action 表示为代码。
    def _step_stream(
        self, memory_step: ActionStep
    ) -> Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput]:
        """
        Perform one step in the ReAct framework: the agent thinks, acts, and observes the result.
        Yields ChatMessageStreamDelta during the run if streaming is enabled.
        At the end, yields either None if the step is not final, or the final answer.
        """
        # 【中文教学注释】代码动作也基于完整 trajectory 生成。
        memory_messages = self.write_memory_to_messages()

        input_messages = memory_messages.copy()
        ### Generate model output ###
        memory_step.model_input_messages = input_messages
        stop_sequences = ["Observation:", "Calling tools:"]
        if self.code_block_tags[1] not in self.code_block_tags[0]:
            # If the closing tag is contained in the opening tag, adding it as a stop sequence would cut short any code generation
            stop_sequences.append(self.code_block_tags[1])
        try:
            additional_args: dict[str, Any] = {}
            if self._use_structured_outputs_internally:
                additional_args["response_format"] = CODEAGENT_RESPONSE_FORMAT
            if self.stream_outputs:
                output_stream = self.model.generate_stream(
                    input_messages,
                    stop_sequences=stop_sequences,
                    **additional_args,
                )
                chat_message_stream_deltas: list[ChatMessageStreamDelta] = []
                with Live("", console=self.logger.console, vertical_overflow="visible") as live:
                    for event in output_stream:
                        chat_message_stream_deltas.append(event)
                        live.update(
                            Markdown(agglomerate_stream_deltas(chat_message_stream_deltas).render_as_markdown())
                        )
                        yield event
                chat_message = agglomerate_stream_deltas(chat_message_stream_deltas)
                memory_step.model_output_message = chat_message
                output_text = chat_message.content
            else:
                chat_message: ChatMessage = self.model.generate(
                    input_messages,
                    stop_sequences=stop_sequences,
                    **additional_args,
                )
                memory_step.model_output_message = chat_message
                output_text = chat_message.content
                self.logger.log_markdown(
                    content=output_text or "",
                    title="Output message of the LLM:",
                    level=LogLevel.DEBUG,
                )

            if not self._use_structured_outputs_internally:
                # This adds the end code sequence (i.e. the closing code block tag) to the history.
                # This will nudge subsequent LLM calls to finish with this end code sequence, thus efficiently stopping generation.
                if output_text and not output_text.strip().endswith(self.code_block_tags[1]):
                    output_text += self.code_block_tags[1]
                    memory_step.model_output_message.content = output_text

            memory_step.token_usage = chat_message.token_usage
            memory_step.model_output = output_text
        except Exception as e:
            raise AgentGenerationError(f"Error in generating model output:\n{e}", self.logger) from e

        ### Parse output ###
        try:
            if self._use_structured_outputs_internally:
                code_action = json.loads(output_text)["code"]
                code_action = extract_code_from_text(code_action, self.code_block_tags) or code_action
            else:
                # 【中文教学注释】runtime 解析并规范化模型生成的代码动作。
                code_action = parse_code_blobs(output_text, self.code_block_tags)
            code_action = fix_final_answer_code(code_action)
            memory_step.code_action = code_action
        except Exception as e:
            error_msg = f"Error in code parsing:\n{e}\nMake sure to provide correct code blobs."
            raise AgentParsingError(error_msg, self.logger)

        # 【中文教学注释】代码执行被包装为一个名为 `python_interpreter` 的内部 action/tool 记录。
        tool_call = ToolCall(
            name="python_interpreter",
            arguments=code_action,
            id=f"call_{len(self.memory.steps)}",
        )
        yield tool_call
        memory_step.tool_calls = [tool_call]

        ### Execute action ###
        self.logger.log_code(title="Executing parsed code:", content=code_action, level=LogLevel.INFO)
        try:
            # 【中文教学注释】真正执行发生在 executor 边界；生产环境必须把它视为高风险能力。
            code_output = self.python_executor(code_action)
            execution_outputs_console = []
            if len(code_output.logs) > 0:
                execution_outputs_console += [
                    Text("Execution logs:", style="bold"),
                    Text(code_output.logs),
                ]
            observation = "Execution logs:\n" + code_output.logs
        except Exception as e:
            if hasattr(self.python_executor, "state") and "_print_outputs" in self.python_executor.state:
                execution_logs = str(self.python_executor.state["_print_outputs"])
                if len(execution_logs) > 0:
                    execution_outputs_console = [
                        Text("Execution logs:", style="bold"),
                        Text(execution_logs),
                    ]
                    memory_step.observations = "Execution logs:\n" + execution_logs
                    self.logger.log(Group(*execution_outputs_console), level=LogLevel.INFO)
            error_msg = str(e)
            if "Import of " in error_msg and " is not allowed" in error_msg:
                self.logger.log(
                    "[bold red]Warning to user: Code execution failed due to an unauthorized import - Consider passing said import under `additional_authorized_imports` when initializing your CodeAgent.",
                    level=LogLevel.INFO,
                )
            raise AgentExecutionError(error_msg, self.logger)

        truncated_output = truncate_content(str(code_output.output))
        observation += "Last output from code snippet:\n" + truncated_output
        # 【中文教学注释】执行日志和截断后的输出成为下一轮模型可见的 observation。
        memory_step.observations = observation

        if not code_output.is_final_answer:
            execution_outputs_console += [
                Text(
                    f"Out: {truncated_output}",
                ),
            ]
        self.logger.log(Group(*execution_outputs_console), level=LogLevel.INFO)
        memory_step.action_output = code_output.output
        # 【中文教学注释】executor 是否产生 final answer 决定 runtime 是否结束本轮 Agent loop。
        yield ActionOutput(output=code_output.output, is_final_answer=code_output.is_final_answer)
~~~

## 阅读提醒

- `MultiStepAgent._run_stream()` 是共享 runtime loop；`ToolCallingAgent` 和 `CodeAgent` 只替换单步 action 解释方式。
- `AgentMemory` 保存的是当前进程中的 step trajectory；是否跨会话持久化不由这些核心函数自动保证。
- 代码摘录刻意省略 imports、类外辅助函数和非主路径；先用 `CODE_GUIDE.md` 的顺序阅读完整原文件。
