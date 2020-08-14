import feedparser
import pathlib
import re


ROOT_PATH = pathlib.Path(__file__).parent.resolve()
FEED_URL = "https://www.fosdick.io/feed.xml"


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} start \-\->.*<!\-\- {} end \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} start -->{}<!-- {} end -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_blog_entries():
    entries = feedparser.parse(FEED_URL)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]


if __name__ == "__main__":
    readme = ROOT_PATH / "README.md"
    readme_contents = readme.open().read()

    entries = fetch_blog_entries()[:5]
    entries_md = "\n\n".join(
        ["- [{title}]({url}) - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(readme_contents, "Blog entries", entries_md)

    readme.open("w").write(rewritten)
