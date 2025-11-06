from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re

STYLE_ENUM = {"chapter", "blog", "post", "snippet", "tweet"}


@dataclass
class ContentNode:
    id: str
    type: str = "content"
    title: Optional[str] = None
    date: str = ""
    style: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    authors: List[str] = field(default_factory=list)
    relates: List[str] = field(default_factory=list)
    content: str = ""


@dataclass
class TagNode:
    id: str
    type: str = "tag"
    name: str = ""


@dataclass
class StyleNode:
    id: str
    type: str = "style"
    name: str = ""


@dataclass
class AuthorNode:
    id: str
    type: str = "author"
    name: str = ""
    linkedin_username: str = ""
    twitter_username: str = ""
    substack_username: str = ""
    reddit_username: str = ""


@dataclass
class LinkNode:
    id: str
    type: str = "link"
    url: str = ""
    title: Optional[str] = None
    description: Optional[str] = None


def slugify(s: str) -> str:
    """
    Normalize text to strict slug format:
    - Converts to lowercase
    - Replaces spaces and special characters with dashes
    - Removes all punctuation except dashes and underscores
    - Collapses multiple dashes into single dash
    - Strips leading/trailing dashes

    Examples:
        "Machine Learning" -> "machine-learning"
        "AI & ML!" -> "ai-ml"
        "Python_3.11" -> "python-3-11"
    """
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9_\-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def ensure_style(name: str) -> str:
    if name not in STYLE_ENUM:
        raise ValueError(f"Invalid style '{name}'. Allowed: {sorted(STYLE_ENUM)}")
    return name
