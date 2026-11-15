"""Build-time validation and rendering for topic-filtered explanations."""

from html import escape
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
from mkdocs.exceptions import PluginError


KNOWLEDGE = re.compile(
    r'^:::[ \t]*knowledge[ \t]+tags="(?P<tags>[a-z0-9, -]+)"[ \t]*\n'
    r'(?P<content>.*?)^:::[ \t]*$', re.MULTILINE | re.DOTALL,
)
ROOT = Path(__file__).resolve().parents[1]


def load_topics():
    try:
        topics = json.loads((ROOT / "topics.json").read_text(encoding="utf-8"))
        ids = [topic["id"] for topic in topics]
        if (not isinstance(topics, list) or len(ids) != len(set(ids)) or
            any(not re.fullmatch(r"[a-z][a-z0-9-]*", t["id"]) or
                not isinstance(t["label"], str) or not t["label"].strip() for t in topics)):
            raise ValueError("topics must have unique IDs and non-empty labels")
        return topics
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise PluginError(f"Invalid topics.json: {error}") from error


def on_page_markdown(markdown, *, page, config, files):
    allowed = {topic["id"] for topic in load_topics()}

    def knowledge(match):
        tags = [tag.strip() for tag in match.group("tags").split(",")]
        if not all(tags) or len(tags) != len(set(tags)) or set(tags) - allowed:
            raise PluginError(f"{page.file.src_uri}: invalid knowledge tags: {match.group('tags')}")
        if re.search(r'^:::\s*(?:knowledge|proof-ref)\b', match.group("content"), re.MULTILINE):
            raise PluginError(f"{page.file.src_uri}: knowledge blocks cannot contain other directive blocks")
        return (f'<section class="knowledge-block" data-knowledge-tags="{escape(",".join(tags))}" markdown="1">\n\n'
                f'{match.group("content").strip()}\n\n</section>')

    markdown = KNOWLEDGE.sub(knowledge, markdown)
    if re.search(r'^:::\s*knowledge\b', markdown, re.MULTILINE):
        raise PluginError(f"{page.file.src_uri}: malformed knowledge block")
    return markdown


def on_post_page(output, *, page, config):
    soup = BeautifulSoup(output, "html.parser")
    article = soup.select_one(".md-content__inner")
    if article is None:
        return output

    selector = soup.new_tag("section")
    selector["class"] = ["knowledge-selector"]
    selector["hidden"] = ""
    selector["aria-label"] = "Topics you understand"
    title = soup.new_tag("strong")
    title.string = "Topics I understand"
    selector.append(title)
    for topic in load_topics():
        label = soup.new_tag("label")
        checkbox = soup.new_tag("input", type="checkbox")
        checkbox["data-knowledge-topic"] = topic["id"]
        label.append(checkbox)
        label.append(" " + topic["label"])
        selector.append(label)
    article.insert(0, selector)
    return str(soup)
