"""Document augmentation starter."""

from agentic_assistants.data.rag.chunkers import TextChunker
from agentic_assistants.data.rag.augmenters import (
    ChainedAugmenter,
    EntityAugmenter,
    KeywordAugmenter,
    MetadataAugmenter,
    SummaryAugmenter,
)


def main() -> None:
    text = "Augmenting document chunks improves recall and contextual relevance."
    chunks = TextChunker(chunk_size=80, chunk_overlap=10).chunk(text)
    augment = ChainedAugmenter(
        [MetadataAugmenter(), KeywordAugmenter(), SummaryAugmenter(), EntityAugmenter()]
    )
    out = [augment.augment(c, {"source": "inline"}) for c in chunks]
    print(out[0].to_dict())


if __name__ == "__main__":
    main()

