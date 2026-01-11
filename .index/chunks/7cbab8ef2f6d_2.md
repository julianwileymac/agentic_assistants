# Chunk: 7cbab8ef2f6d_2

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 161-238
- chunk: 3/6

```
count = sum(word_counts) / len(word_counts) if word_counts else 0
        
        # Vocabulary
        all_words = set()
        for text in all_texts:
            all_words.update(text.lower().split())
        metrics.vocabulary_size = len(all_words)
        
        return metrics
    
    def check_preference_dataset(
        self,
        samples: List[Dict[str, Any]],
        prompt_field: str = "prompt",
        chosen_field: str = "chosen",
        rejected_field: str = "rejected",
    ) -> DataQualityMetrics:
        """
        Check quality of a preference/DPO dataset.
        
        Args:
            samples: List of sample dictionaries
            prompt_field: Field name for prompt
            chosen_field: Field name for chosen response
            rejected_field: Field name for rejected response
        
        Returns:
            DataQualityMetrics
        """
        if not samples:
            return DataQualityMetrics()
        
        metrics = DataQualityMetrics()
        
        # Check completeness
        required_fields = [prompt_field, chosen_field, rejected_field]
        missing_counts = {f: 0 for f in required_fields}
        
        all_texts = []
        chosen_lengths = []
        rejected_lengths = []
        
        for sample in samples:
            for field in required_fields:
                if not sample.get(field):
                    missing_counts[field] += 1
            
            prompt = sample.get(prompt_field, "")
            chosen = sample.get(chosen_field, "")
            rejected = sample.get(rejected_field, "")
            
            all_texts.append(f"{prompt} {chosen} {rejected}")
            chosen_lengths.append(len(chosen))
            rejected_lengths.append(len(rejected))
        
        # Completeness
        total_required = len(samples) * len(required_fields)
        total_missing = sum(missing_counts.values())
        metrics.completeness_score = 1.0 - (total_missing / total_required) if total_required > 0 else 0.0
        metrics.missing_fields = [f for f, c in missing_counts.items() if c > 0]
        
        # Length metrics
        lengths = [len(t) for t in all_texts]
        if lengths:
            metrics.avg_length = sum(lengths) / len(lengths)
            metrics.min_length = min(lengths)
            metrics.max_length = max(lengths)
        
        # Custom metrics for preference data
        if chosen_lengths and rejected_lengths:
            avg_chosen = sum(chosen_lengths) / len(chosen_lengths)
            avg_rejected = sum(rejected_lengths) / len(rejected_lengths)
            metrics.custom_metrics["avg_chosen_length"] = avg_chosen
            metrics.custom_metrics["avg_rejected_length"] = avg_rejected
            metrics.custom_metrics["length_ratio"] = avg_chosen / avg_rejected if avg_rejected > 0 else 1.0
        
        # Uniqueness
```
