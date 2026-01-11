# Chunk: 7cbab8ef2f6d_3

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 232-316
- chunk: 4/6

```
cted_lengths)
            metrics.custom_metrics["avg_chosen_length"] = avg_chosen
            metrics.custom_metrics["avg_rejected_length"] = avg_rejected
            metrics.custom_metrics["length_ratio"] = avg_chosen / avg_rejected if avg_rejected > 0 else 1.0
        
        # Uniqueness
        unique_samples = set(json.dumps(s, sort_keys=True) for s in samples)
        metrics.unique_ratio = len(unique_samples) / len(samples) if samples else 1.0
        metrics.duplicate_count = len(samples) - len(unique_samples)
        
        return metrics
    
    def check_text_quality(self, text: str) -> Dict[str, Any]:
        """
        Check quality of a single text.
        
        Args:
            text: Text to check
        
        Returns:
            Dictionary of quality metrics
        """
        metrics = {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "has_content": len(text.strip()) > 0,
        }
        
        # Check for common issues
        issues = []
        
        if len(text.strip()) < 10:
            issues.append("too_short")
        
        if text.count('\n') > text.count(' ') * 0.5:
            issues.append("excessive_newlines")
        
        if re.search(r'(.)\1{10,}', text):
            issues.append("repeated_characters")
        
        if re.search(r'(https?://|www\.)\S+', text):
            metrics["has_urls"] = True
        
        if re.search(r'<[^>]+>', text):
            issues.append("html_tags")
        
        metrics["issues"] = issues
        metrics["quality_score"] = 1.0 - (len(issues) * 0.2)
        
        return metrics
    
    def validate_format(
        self,
        samples: List[Dict[str, Any]],
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None,
    ) -> DataQualityMetrics:
        """
        Validate dataset format.
        
        Args:
            samples: List of samples
            required_fields: Required field names
            optional_fields: Optional field names
        
        Returns:
            DataQualityMetrics focused on format validation
        """
        metrics = DataQualityMetrics()
        format_errors = []
        
        for i, sample in enumerate(samples):
            if not isinstance(sample, dict):
                format_errors.append(f"Sample {i}: Not a dictionary")
                continue
            
            for field in required_fields:
                if field not in sample:
                    format_errors.append(f"Sample {i}: Missing required field '{field}'")
                elif sample[field] is None:
                    format_errors.append(f"Sample {i}: Field '{field}' is null")
        
        metrics.format_valid = len(format_errors) == 0
```
