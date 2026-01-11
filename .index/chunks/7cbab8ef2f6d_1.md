# Chunk: 7cbab8ef2f6d_1

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 87-171
- chunk: 2/6

```
prompt, chosen, rejected)
    - General text datasets
    """
    
    def __init__(self):
        """Initialize the quality checker."""
        pass
    
    def check_instruct_dataset(
        self,
        samples: List[Dict[str, Any]],
        instruction_field: str = "instruction",
        input_field: str = "input",
        output_field: str = "output",
    ) -> DataQualityMetrics:
        """
        Check quality of an instruction dataset.
        
        Args:
            samples: List of sample dictionaries
            instruction_field: Field name for instruction
            input_field: Field name for input
            output_field: Field name for output
        
        Returns:
            DataQualityMetrics
        """
        if not samples:
            return DataQualityMetrics()
        
        metrics = DataQualityMetrics()
        
        # Check completeness
        required_fields = [instruction_field, output_field]
        missing_counts = {f: 0 for f in required_fields}
        
        instructions = []
        outputs = []
        all_texts = []
        
        for sample in samples:
            for field in required_fields:
                if not sample.get(field):
                    missing_counts[field] += 1
            
            inst = sample.get(instruction_field, "")
            out = sample.get(output_field, "")
            
            instructions.append(inst)
            outputs.append(out)
            all_texts.append(f"{inst} {out}")
        
        # Completeness score
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
            mean = metrics.avg_length
            metrics.length_variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        
        # Uniqueness
        unique_samples = set(json.dumps(s, sort_keys=True) for s in samples)
        metrics.unique_ratio = len(unique_samples) / len(samples) if samples else 1.0
        metrics.duplicate_count = len(samples) - len(unique_samples)
        
        # Word count
        word_counts = [len(t.split()) for t in all_texts]
        metrics.avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
        
        # Vocabulary
        all_words = set()
        for text in all_texts:
            all_words.update(text.lower().split())
        metrics.vocabulary_size = len(all_words)
        
        return metrics
    
```
