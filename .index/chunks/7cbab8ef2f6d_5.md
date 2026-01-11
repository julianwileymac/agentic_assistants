# Chunk: 7cbab8ef2f6d_5

- source: `src/agentic_assistants/data/training/quality.py`
- lines: 381-392
- chunk: 6/6

```
        
                if all_text:
                    lengths = [len(t) for t in all_text]
                    metrics.avg_length = sum(lengths) / len(lengths)
                    metrics.min_length = min(lengths)
                    metrics.max_length = max(lengths)
                    
                    word_counts = [len(t.split()) for t in all_text]
                    metrics.avg_word_count = sum(word_counts) / len(word_counts)
            
            return metrics
```
