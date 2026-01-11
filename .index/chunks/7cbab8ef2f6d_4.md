# Chunk: 7cbab8ef2f6d_4

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 310-388
- chunk: 5/6

```
not in sample:
                    format_errors.append(f"Sample {i}: Missing required field '{field}'")
                elif sample[field] is None:
                    format_errors.append(f"Sample {i}: Field '{field}' is null")
        
        metrics.format_valid = len(format_errors) == 0
        metrics.format_errors = format_errors[:100]  # Limit errors
        
        return metrics
    
    def compute_dataset_metrics(
        self,
        samples: List[Dict[str, Any]],
        text_fields: Optional[List[str]] = None,
    ) -> DataQualityMetrics:
        """
        Compute comprehensive metrics for a dataset.
        
        Args:
            samples: List of samples
            text_fields: Fields containing text (auto-detected if None)
        
        Returns:
            DataQualityMetrics
        """
        if not samples:
            return DataQualityMetrics()
        
        # Auto-detect text fields
        if text_fields is None:
            text_fields = []
            sample = samples[0]
            for key, value in sample.items():
                if isinstance(value, str) and len(value) > 10:
                    text_fields.append(key)
        
        # Determine dataset type and use appropriate checker
        sample = samples[0]
        
        if "instruction" in sample and "output" in sample:
            return self.check_instruct_dataset(samples)
        elif "chosen" in sample and "rejected" in sample:
            return self.check_preference_dataset(samples)
        else:
            # Generic check
            metrics = DataQualityMetrics()
            
            # Completeness
            all_fields = set()
            for s in samples:
                all_fields.update(s.keys())
            
            missing = 0
            for s in samples:
                missing += len(all_fields - set(s.keys()))
            
            total = len(samples) * len(all_fields)
            metrics.completeness_score = 1.0 - (missing / total) if total > 0 else 1.0
            
            # Uniqueness
            unique = set(json.dumps(s, sort_keys=True) for s in samples)
            metrics.unique_ratio = len(unique) / len(samples)
            metrics.duplicate_count = len(samples) - len(unique)
            
            # Text metrics
            if text_fields:
                all_text = []
                for s in samples:
                    for field in text_fields:
                        if field in s and isinstance(s[field], str):
                            all_text.append(s[field])
                
                if all_text:
                    lengths = [len(t) for t in all_text]
                    metrics.avg_length = sum(lengths) / len(lengths)
                    metrics.min_length = min(lengths)
                    metrics.max_length = max(lengths)
                    
```
