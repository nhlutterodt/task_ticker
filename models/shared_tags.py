from typing import List

class SharedTags:
    _tags = set()

    @classmethod
    def add_tags(cls, tags: list[str]):
        cls._tags.update(tags)

    @classmethod
    def remove_tag(cls, tag: str):
        cls._tags.discard(tag)

    @classmethod
    def get_all_tags(cls) -> list[str]:
        return sorted(cls._tags)