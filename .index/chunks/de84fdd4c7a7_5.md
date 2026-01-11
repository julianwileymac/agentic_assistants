# Chunk: de84fdd4c7a7_5

- source: `src/agentic_assistants/training/frameworks/llama_factory.py`
- lines: 363-447
- chunk: 6/8

```

    ) -> Dict[str, Any]:
        """Run the training process."""
        
        # Build command
        cmd = [
            sys.executable, "-m", "llamafactory.cli", "train",
            config_file,
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=self._llama_factory_path,
        )
        
        metrics = {}
        total_steps = 0
        
        # Stream output and parse metrics
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_str = line.decode("utf-8", errors="ignore").strip()
            logger.debug(line_str)
            
            # Parse metrics from output
            parsed = self._parse_training_output(line_str)
            if parsed:
                metrics.update(parsed)
                total_steps = parsed.get("step", total_steps)
                
                if metrics_callback:
                    metrics_callback(parsed)
        
        await process.wait()
        
        if process.returncode == 0:
            return {
                "success": True,
                "metrics": metrics,
                "total_steps": total_steps,
            }
        else:
            return {
                "success": False,
                "error": f"Training process exited with code {process.returncode}",
            }
    
    def _parse_training_output(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse training output line for metrics."""
        metrics = {}
        
        # Look for loss values
        if "loss" in line.lower():
            try:
                # Try to parse JSON-style output
                if "{" in line and "}" in line:
                    json_str = line[line.index("{"):line.rindex("}")+1]
                    data = json.loads(json_str)
                    return data
                
                # Parse "loss: X.XXX" style
                import re
                loss_match = re.search(r"loss[:\s]+([0-9.]+)", line, re.IGNORECASE)
                if loss_match:
                    metrics["loss"] = float(loss_match.group(1))
                
                # Parse step information
                step_match = re.search(r"step[:\s]+(\d+)", line, re.IGNORECASE)
                if step_match:
                    metrics["step"] = int(step_match.group(1))
                
                # Parse learning rate
                lr_match = re.search(r"lr[:\s]+([0-9.e-]+)", line, re.IGNORECASE)
                if lr_match:
                    metrics["learning_rate"] = float(lr_match.group(1))
                
                # Parse epoch
```
