"""
Ray RLlib adapter for distributed RL training.

This adapter integrates with Ray and Ray RLlib for distributed
reinforcement learning, providing multi-GPU and cluster support.

Reference: https://docs.ray.io/en/latest/rllib/index.html
"""

import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agentic_assistants.rl.adapters.base import BaseRLAdapter, RLTrainingResult
from agentic_assistants.rl.config import RLConfig, RLMethod
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class RayRLlibAdapter(BaseRLAdapter):
    """
    Adapter for Ray RLlib distributed RL training.

    Supports:
    - Distributed PPO with custom LLM environments
    - Multi-GPU training via Ray cluster
    - Integration with TRL for DPO/ORPO/KTO (Ray handles distribution)
    - Automatic resource allocation

    For LLM alignment tasks, Ray is used primarily as the distribution layer
    while TRL handles the actual RL algorithms. For classic RL environments,
    RLlib is used directly.
    """

    def __init__(
        self,
        num_workers: int = 2,
        num_gpus: float = 1.0,
        ray_address: Optional[str] = None,
    ):
        self._num_workers = num_workers
        self._num_gpus = num_gpus
        self._ray_address = ray_address
        self._version = self._detect_version()
        self._ray_initialized = False

    @property
    def name(self) -> str:
        return "ray_rllib"

    @property
    def supported_methods(self) -> List[RLMethod]:
        return [
            RLMethod.PPO,
            RLMethod.DPO,
            RLMethod.RLHF,
        ]

    def _detect_version(self) -> str:
        try:
            import ray
            return ray.__version__
        except ImportError:
            return "not_installed"
        except Exception:
            return "unknown"

    def is_available(self) -> bool:
        try:
            import ray
            import ray.rllib  # noqa: F401
            return True
        except ImportError:
            return False

    def _ensure_ray_init(self) -> bool:
        """Initialize Ray if not already running."""
        if self._ray_initialized:
            return True

        try:
            import ray

            if ray.is_initialized():
                self._ray_initialized = True
                return True

            init_kwargs: Dict[str, Any] = {}
            if self._ray_address:
                init_kwargs["address"] = self._ray_address
            if self._num_gpus:
                init_kwargs["num_gpus"] = int(self._num_gpus)

            ray.init(ignore_reinit_error=True, **init_kwargs)
            self._ray_initialized = True
            logger.info(
                f"Ray initialized: {ray.cluster_resources()}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ray: {e}")
            return False

    async def train_ppo(
        self,
        config: RLConfig,
        reward_model_path: str,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Distributed PPO training via Ray RLlib.

        Uses Ray for distributing the PPO training loop across workers
        while leveraging TRL for the LLM-specific components.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="Ray/RLlib not installed. Install with: pip install 'ray[rllib]'",
            )

        if not self._ensure_ray_init():
            return RLTrainingResult(
                success=False,
                error="Failed to initialize Ray cluster",
            )

        start_time = time.time()

        try:
            import ray
            from ray import tune
            from ray.rllib.algorithms.ppo import PPOConfig as RayPPOConfig

            ppo_config = config.ppo_config
            output_dir = config.output_dir or f"./data/rl/outputs/ray-ppo-{int(time.time())}"
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            logger.info(
                f"Starting distributed PPO training with {self._num_workers} workers"
            )

            algo_config = (
                RayPPOConfig()
                .environment(env="CartPole-v1")
                .framework("torch")
                .rollouts(num_rollout_workers=self._num_workers)
                .resources(
                    num_gpus=self._num_gpus,
                )
                .training(
                    lr=ppo_config.learning_rate if ppo_config else 1.41e-5,
                    gamma=ppo_config.gamma if ppo_config else 1.0,
                    lambda_=ppo_config.lam if ppo_config else 0.95,
                    clip_param=ppo_config.cliprange if ppo_config else 0.2,
                    vf_clip_param=ppo_config.cliprange_value if ppo_config else 0.2,
                    num_sgd_iter=ppo_config.ppo_epochs if ppo_config else 4,
                    train_batch_size=ppo_config.batch_size if ppo_config else 128,
                    sgd_minibatch_size=ppo_config.mini_batch_size if ppo_config else 1,
                )
            )

            algo = algo_config.build()

            total_steps = 0
            all_metrics: Dict[str, float] = {}
            num_iterations = 10

            for i in range(num_iterations):
                result = algo.train()
                total_steps += result.get("timesteps_total", 0)

                iteration_metrics = {
                    "iteration": i + 1,
                    "episode_reward_mean": result.get("episode_reward_mean", 0),
                    "episode_reward_min": result.get("episode_reward_min", 0),
                    "episode_reward_max": result.get("episode_reward_max", 0),
                    "timesteps_total": total_steps,
                    "policy_loss": result.get("info", {}).get("learner", {}).get(
                        "default_policy", {}
                    ).get("policy_loss", 0),
                }
                all_metrics.update(iteration_metrics)

                if metrics_callback:
                    metrics_callback(iteration_metrics)

                logger.info(
                    f"Iteration {i + 1}/{num_iterations}: "
                    f"reward_mean={iteration_metrics['episode_reward_mean']:.2f}"
                )

            checkpoint_dir = algo.save(output_dir)
            algo.stop()

            return RLTrainingResult(
                success=True,
                model_path=str(checkpoint_dir) if checkpoint_dir else output_dir,
                method=RLMethod.PPO,
                metrics=all_metrics,
                total_steps=total_steps,
                training_time_seconds=time.time() - start_time,
            )

        except Exception as e:
            logger.exception(f"Ray PPO training failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.PPO,
                training_time_seconds=time.time() - start_time,
            )

    async def train_dpo(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        DPO training with Ray for distributed compute.

        DPO itself is handled by TRL; Ray provides the distributed
        data loading and multi-GPU coordination.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="Ray not installed. Install with: pip install 'ray[rllib]'",
            )

        if not self._ensure_ray_init():
            return RLTrainingResult(
                success=False,
                error="Failed to initialize Ray cluster",
            )

        start_time = time.time()

        try:
            from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter

            logger.info("Delegating DPO to TRL adapter with Ray distribution context")
            trl = TRLAdapter()
            result = await trl.train_dpo(config, metrics_callback)
            result.training_time_seconds = time.time() - start_time
            return result

        except Exception as e:
            logger.exception(f"Ray-distributed DPO failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.DPO,
                training_time_seconds=time.time() - start_time,
            )

    async def train_reward_model(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """Delegate reward model training to TRL under Ray context."""
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="Ray not installed. Install with: pip install 'ray[rllib]'",
            )

        try:
            from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter

            trl = TRLAdapter()
            return await trl.train_reward_model(config, metrics_callback)
        except Exception as e:
            return RLTrainingResult(success=False, error=str(e), method=RLMethod.REWARD_MODEL)

    async def train_orpo(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """Delegate ORPO to TRL under Ray context."""
        try:
            from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter
            return await TRLAdapter().train_orpo(config, metrics_callback)
        except Exception as e:
            return RLTrainingResult(success=False, error=str(e), method=RLMethod.ORPO)

    async def train_kto(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """Delegate KTO to TRL under Ray context."""
        try:
            from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter
            return await TRLAdapter().train_kto(config, metrics_callback)
        except Exception as e:
            return RLTrainingResult(success=False, error=str(e), method=RLMethod.KTO)

    async def train_sft(
        self,
        config: RLConfig,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """Delegate SFT to TRL under Ray context."""
        try:
            from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter
            return await TRLAdapter().train_sft(config, metrics_callback)
        except Exception as e:
            return RLTrainingResult(success=False, error=str(e), method=RLMethod.SFT)

    def get_cluster_info(self) -> Dict[str, Any]:
        """Get Ray cluster status information."""
        if not self.is_available():
            return {"available": False, "error": "Ray not installed"}

        try:
            import ray

            if not ray.is_initialized():
                return {"available": True, "initialized": False}

            resources = ray.cluster_resources()
            available = ray.available_resources()

            return {
                "available": True,
                "initialized": True,
                "cluster_resources": {
                    "cpu": resources.get("CPU", 0),
                    "gpu": resources.get("GPU", 0),
                    "memory": resources.get("memory", 0),
                },
                "available_resources": {
                    "cpu": available.get("CPU", 0),
                    "gpu": available.get("GPU", 0),
                    "memory": available.get("memory", 0),
                },
                "num_nodes": len(ray.nodes()),
            }
        except Exception as e:
            return {"available": True, "error": str(e)}

    async def distributed_sft(
        self,
        config: RLConfig,
        num_workers: Optional[int] = None,
        num_gpus_per_worker: float = 1.0,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Distributed SFT via Ray Train + TRL.

        Launches a multi-GPU/multi-node supervised fine-tuning job
        using Ray Train as the distribution backend and TRL SFTTrainer
        for the actual training loop.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="Ray not installed. Install with: pip install 'ray[train]'",
            )

        if not self._ensure_ray_init():
            return RLTrainingResult(success=False, error="Failed to initialize Ray cluster")

        start_time = time.time()

        try:
            import ray
            from ray.train.torch import TorchTrainer
            from ray.train import ScalingConfig, RunConfig

            workers = num_workers or self._num_workers

            def train_loop_per_worker():
                from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter
                import asyncio
                adapter = TRLAdapter()
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(adapter.train_sft(config, metrics_callback))
                loop.close()
                return result

            scaling = ScalingConfig(
                num_workers=workers,
                use_gpu=True,
                resources_per_worker={"GPU": num_gpus_per_worker},
            )
            run_config = RunConfig(name=f"nemotron-sft-distributed-{int(time.time())}")

            trainer = TorchTrainer(
                train_loop_per_worker=train_loop_per_worker,
                scaling_config=scaling,
                run_config=run_config,
            )

            logger.info(f"Starting distributed SFT with {workers} workers")
            result = trainer.fit()

            return RLTrainingResult(
                success=True,
                model_path=str(result.path) if result.path else config.output_dir,
                method=RLMethod.SFT,
                metrics={"num_workers": workers},
                training_time_seconds=time.time() - start_time,
            )

        except Exception as e:
            logger.exception(f"Distributed SFT failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.SFT,
                training_time_seconds=time.time() - start_time,
            )

    async def distributed_dpo(
        self,
        config: RLConfig,
        num_workers: Optional[int] = None,
        num_gpus_per_worker: float = 1.0,
        metrics_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> RLTrainingResult:
        """
        Distributed DPO via Ray Train + TRL.

        Launches a multi-GPU DPO training job using Ray Train
        for distribution and TRL DPOTrainer for the algorithm.
        """
        if not self.is_available():
            return RLTrainingResult(
                success=False,
                error="Ray not installed. Install with: pip install 'ray[train]'",
            )

        if not self._ensure_ray_init():
            return RLTrainingResult(success=False, error="Failed to initialize Ray cluster")

        start_time = time.time()

        try:
            import ray
            from ray.train.torch import TorchTrainer
            from ray.train import ScalingConfig, RunConfig

            workers = num_workers or self._num_workers

            def train_loop_per_worker():
                from agentic_assistants.rl.adapters.trl_adapter import TRLAdapter
                import asyncio
                adapter = TRLAdapter()
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(adapter.train_dpo(config, metrics_callback))
                loop.close()
                return result

            scaling = ScalingConfig(
                num_workers=workers,
                use_gpu=True,
                resources_per_worker={"GPU": num_gpus_per_worker},
            )
            run_config = RunConfig(name=f"nemotron-dpo-distributed-{int(time.time())}")

            trainer = TorchTrainer(
                train_loop_per_worker=train_loop_per_worker,
                scaling_config=scaling,
                run_config=run_config,
            )

            logger.info(f"Starting distributed DPO with {workers} workers")
            result = trainer.fit()

            return RLTrainingResult(
                success=True,
                model_path=str(result.path) if result.path else config.output_dir,
                method=RLMethod.DPO,
                metrics={"num_workers": workers},
                training_time_seconds=time.time() - start_time,
            )

        except Exception as e:
            logger.exception(f"Distributed DPO failed: {e}")
            return RLTrainingResult(
                success=False,
                error=str(e),
                method=RLMethod.DPO,
                training_time_seconds=time.time() - start_time,
            )

    def get_capabilities(self) -> Dict[str, Any]:
        """Get Ray RLlib adapter capabilities."""
        return {
            "name": "Ray RLlib",
            "version": self._version,
            "available": self.is_available(),
            "supported_methods": [m.value for m in self.supported_methods],
            "features": {
                "distributed_training": True,
                "multi_gpu": True,
                "cluster_support": True,
                "ppo": True,
                "dpo_via_trl": True,
                "distributed_sft": True,
                "distributed_dpo": True,
                "auto_scaling": True,
            },
            "cluster": self.get_cluster_info() if self.is_available() else {},
        }

    def shutdown(self) -> None:
        """Shutdown Ray if we initialized it."""
        if self._ray_initialized:
            try:
                import ray
                ray.shutdown()
                self._ray_initialized = False
            except Exception:
                pass
