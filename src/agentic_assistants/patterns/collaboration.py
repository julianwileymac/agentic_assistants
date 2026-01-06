"""
Multi-Agent Collaboration Pattern implementation.

This module provides patterns for coordinating multiple agents:
- Sequential collaboration
- Parallel collaboration
- Debate/critique patterns
- Consensus building

Example:
    >>> from agentic_assistants.patterns import CollaborationPattern
    >>> 
    >>> collab = CollaborationPattern(agents=[agent1, agent2])
    >>> result = collab.execute("Solve this problem together")
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from agentic_assistants.config import AgenticConfig
from agentic_assistants.core.telemetry import trace_function
from agentic_assistants.patterns.base import AgenticPattern, PatternConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class CollaborationMode(str, Enum):
    """Collaboration modes."""
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"  # Agents work simultaneously
    DEBATE = "debate"  # Agents debate and critique
    CONSENSUS = "consensus"  # Agents work toward agreement


@dataclass
class CollaborationConfig(PatternConfig):
    """
    Configuration for Collaboration pattern.
    
    Attributes:
        mode: Collaboration mode
        max_rounds: Maximum collaboration rounds
        require_consensus: Require agreement for completion
        mediator_enabled: Use a mediator agent
        share_context: Share context between agents
    """
    
    name: str = "collaboration"
    description: str = "Multi-agent collaboration pattern"
    mode: CollaborationMode = CollaborationMode.SEQUENTIAL
    max_rounds: int = 3
    require_consensus: bool = False
    mediator_enabled: bool = False
    share_context: bool = True


class CollaborationPattern(AgenticPattern):
    """
    Multi-agent collaboration pattern.
    
    This pattern coordinates multiple agents to work together
    on a problem. Supports various collaboration modes:
    
    - Sequential: Agents contribute in order, building on each other
    - Parallel: Agents work independently, results combined
    - Debate: Agents critique and improve each other's work
    - Consensus: Agents iterate until agreement
    
    Attributes:
        agents: List of agent callables
        collab_config: Collaboration configuration
    
    Example:
        >>> # Sequential collaboration
        >>> collab = CollaborationPattern(
        ...     agents=[researcher, writer, editor],
        ...     mode=CollaborationMode.SEQUENTIAL
        ... )
        >>> result = collab.execute("Write an article about AI")
        
        >>> # Debate mode
        >>> debate = CollaborationPattern(
        ...     agents=[optimist, skeptic],
        ...     mode=CollaborationMode.DEBATE
        ... )
        >>> result = debate.execute("Should we use AI in healthcare?")
    """
    
    def __init__(
        self,
        agents: Optional[list[Callable]] = None,
        mode: CollaborationMode = CollaborationMode.SEQUENTIAL,
        config: Optional[AgenticConfig] = None,
        collab_config: Optional[CollaborationConfig] = None,
    ):
        """
        Initialize Collaboration pattern.
        
        Args:
            agents: List of agent callables or agent configurations
            mode: Collaboration mode
            config: Framework configuration
            collab_config: Collaboration configuration
        """
        collab_config = collab_config or CollaborationConfig(mode=mode)
        super().__init__(config=config, pattern_config=collab_config)
        
        self.collab_config = collab_config
        self.agents = agents or []
    
    def add_agent(
        self,
        agent: Callable,
        name: Optional[str] = None,
        role: Optional[str] = None,
    ) -> None:
        """
        Add an agent to the collaboration.
        
        Args:
            agent: Agent callable
            name: Agent name
            role: Agent role
        """
        self.agents.append({
            "agent": agent,
            "name": name or f"agent_{len(self.agents)}",
            "role": role or "collaborator",
        })
    
    def _get_agent_callable(self, agent: Any) -> Callable:
        """Get callable from agent specification."""
        if callable(agent):
            return agent
        if isinstance(agent, dict):
            return agent.get("agent", agent.get("func"))
        raise ValueError(f"Cannot get callable from: {type(agent)}")
    
    def _get_agent_name(self, agent: Any, index: int) -> str:
        """Get name for an agent."""
        if isinstance(agent, dict):
            return agent.get("name", f"agent_{index}")
        return f"agent_{index}"
    
    @trace_function(attributes={"pattern": "collaboration", "step": "sequential"})
    def _execute_sequential(self, input_data: Any) -> Any:
        """Execute sequential collaboration."""
        current_output = input_data
        results = []
        
        for i, agent in enumerate(self.agents):
            agent_fn = self._get_agent_callable(agent)
            agent_name = self._get_agent_name(agent, i)
            
            start_time = time.time()
            
            try:
                # Pass previous output as input
                if self.collab_config.share_context:
                    agent_input = {
                        "original_input": input_data,
                        "previous_output": current_output if i > 0 else None,
                        "context": results,
                    }
                else:
                    agent_input = current_output
                
                output = agent_fn(agent_input)
                current_output = output
                
                results.append({
                    "agent": agent_name,
                    "output": output,
                })
                
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results.append({
                    "agent": agent_name,
                    "error": str(e),
                })
            
            duration_ms = (time.time() - start_time) * 1000
            self.record_step(
                action=f"agent_{agent_name}",
                input_data={"agent": agent_name},
                output_data={"success": "error" not in results[-1]},
                duration_ms=duration_ms,
            )
        
        return {
            "final_output": current_output,
            "agent_outputs": results,
            "mode": "sequential",
        }
    
    @trace_function(attributes={"pattern": "collaboration", "step": "parallel"})
    def _execute_parallel(self, input_data: Any) -> Any:
        """Execute parallel collaboration."""
        results = []
        
        # In a real implementation, this would use concurrent execution
        # For simplicity, we execute sequentially but treat as independent
        for i, agent in enumerate(self.agents):
            agent_fn = self._get_agent_callable(agent)
            agent_name = self._get_agent_name(agent, i)
            
            start_time = time.time()
            
            try:
                output = agent_fn(input_data)
                results.append({
                    "agent": agent_name,
                    "output": output,
                })
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results.append({
                    "agent": agent_name,
                    "error": str(e),
                })
            
            duration_ms = (time.time() - start_time) * 1000
            self.record_step(
                action=f"agent_{agent_name}",
                input_data={"agent": agent_name},
                output_data={"success": "error" not in results[-1]},
                duration_ms=duration_ms,
            )
        
        # Combine results
        combined = self._combine_parallel_results(results)
        
        return {
            "combined_output": combined,
            "agent_outputs": results,
            "mode": "parallel",
        }
    
    def _combine_parallel_results(self, results: list[dict]) -> Any:
        """Combine parallel results."""
        # Simple combination - can be overridden
        outputs = [r["output"] for r in results if "output" in r]
        
        if not outputs:
            return None
        
        if len(outputs) == 1:
            return outputs[0]
        
        # Return all outputs if they're different
        return outputs
    
    @trace_function(attributes={"pattern": "collaboration", "step": "debate"})
    def _execute_debate(self, input_data: Any) -> Any:
        """Execute debate collaboration."""
        if len(self.agents) < 2:
            raise ValueError("Debate mode requires at least 2 agents")
        
        rounds = []
        current_topic = input_data
        
        for round_num in range(self.collab_config.max_rounds):
            round_results = []
            
            for i, agent in enumerate(self.agents):
                agent_fn = self._get_agent_callable(agent)
                agent_name = self._get_agent_name(agent, i)
                
                start_time = time.time()
                
                # Include previous arguments in context
                debate_input = {
                    "topic": current_topic,
                    "round": round_num + 1,
                    "previous_arguments": round_results,
                    "instruction": "Present your argument or respond to previous arguments.",
                }
                
                try:
                    output = agent_fn(debate_input)
                    round_results.append({
                        "agent": agent_name,
                        "argument": output,
                    })
                except Exception as e:
                    logger.error(f"Agent {agent_name} failed in debate: {e}")
                
                duration_ms = (time.time() - start_time) * 1000
                self.record_step(
                    action=f"debate_round_{round_num + 1}_{agent_name}",
                    input_data={"round": round_num + 1, "agent": agent_name},
                    duration_ms=duration_ms,
                )
            
            rounds.append(round_results)
        
        return {
            "debate_rounds": rounds,
            "mode": "debate",
            "total_rounds": len(rounds),
        }
    
    @trace_function(attributes={"pattern": "collaboration", "step": "consensus"})
    def _execute_consensus(self, input_data: Any) -> Any:
        """Execute consensus collaboration."""
        proposals = []
        
        # Initial proposals
        for i, agent in enumerate(self.agents):
            agent_fn = self._get_agent_callable(agent)
            agent_name = self._get_agent_name(agent, i)
            
            try:
                output = agent_fn(input_data)
                proposals.append({
                    "agent": agent_name,
                    "proposal": output,
                })
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
        
        # Check for consensus (simplified)
        consensus_reached = len(set(str(p["proposal"]) for p in proposals)) == 1
        
        if consensus_reached:
            return {
                "consensus": proposals[0]["proposal"],
                "proposals": proposals,
                "consensus_reached": True,
                "mode": "consensus",
            }
        
        # Iterate toward consensus
        for round_num in range(self.collab_config.max_rounds):
            # Share all proposals and ask for revised proposals
            revised = []
            for i, agent in enumerate(self.agents):
                agent_fn = self._get_agent_callable(agent)
                agent_name = self._get_agent_name(agent, i)
                
                consensus_input = {
                    "original_input": input_data,
                    "all_proposals": proposals,
                    "instruction": "Review all proposals and provide a revised proposal that could achieve consensus.",
                }
                
                try:
                    output = agent_fn(consensus_input)
                    revised.append({
                        "agent": agent_name,
                        "proposal": output,
                    })
                except Exception:
                    pass
            
            proposals = revised
            
            # Check consensus
            if len(set(str(p["proposal"]) for p in proposals)) == 1:
                return {
                    "consensus": proposals[0]["proposal"],
                    "proposals": proposals,
                    "consensus_reached": True,
                    "rounds": round_num + 1,
                    "mode": "consensus",
                }
            
            self.record_step(
                action=f"consensus_round_{round_num + 1}",
                output_data={"consensus_reached": False},
            )
        
        return {
            "consensus": None,
            "proposals": proposals,
            "consensus_reached": False,
            "mode": "consensus",
        }
    
    def _execute(self, input_data: Any) -> Any:
        """Execute collaboration based on mode."""
        mode = self.collab_config.mode
        
        if mode == CollaborationMode.SEQUENTIAL:
            return self._execute_sequential(input_data)
        elif mode == CollaborationMode.PARALLEL:
            return self._execute_parallel(input_data)
        elif mode == CollaborationMode.DEBATE:
            return self._execute_debate(input_data)
        elif mode == CollaborationMode.CONSENSUS:
            return self._execute_consensus(input_data)
        else:
            raise ValueError(f"Unknown collaboration mode: {mode}")
    
    def collaborate(
        self,
        task: str,
        experiment_name: Optional[str] = None,
    ):
        """
        Convenience method for collaboration.
        
        Args:
            task: Task for agents to collaborate on
            experiment_name: MLFlow experiment name
        
        Returns:
            PatternResult with collaboration output
        """
        return self.execute(
            input_data=task,
            experiment_name=experiment_name,
            run_name=f"collab-{self.collab_config.mode.value}",
        )

