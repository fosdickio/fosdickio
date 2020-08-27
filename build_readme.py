import feedparser
import pathlib
import re
import requests


ROOT_PATH = pathlib.Path(__file__).parent.resolve()
FEED_URL = "https://www.fosdick.io/feed.xml"
TIL_URL = "https://raw.githubusercontent.com/fosdickio/til/main/README.md"


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} start \-\->.*<!\-\- {} end \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} start -->{}<!-- {} end -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_blog_entries(url):
    entries = feedparser.parse(url)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]


def fetch_til_entries(url):
    response = requests.get(url, timeout=60)
    tils = []
    if response.status_code == 200:
        response_text = str(response.text)
        lines = response_text.replace("\n\n", "\n").split("<!-- TILs start -->")[1].split("<!-- TILs end -->")[0].split("\n")
        for line in lines:
            if line.startswith("- ["):
                til = {
                    'markdown': line,
                    'title': line.strip('- [').split('])')[0].split('](')[0],
                    'url': line.strip('- [').split('])')[0].split('](')[1].split(') (')[0],
                    'date': line.strip(')').split(' (')[1]
                }
                tils.append(til)
    else:
        raise RuntimeError("TIL request return status was not 200.")

    sorted_tils = sorted(tils, key=lambda k: k['date'], reverse=True)

    return sorted_tils


if __name__ == "__main__":
    readme = ROOT_PATH / "README.md"
    readme_contents = readme.open().read()

    blog_entries = fetch_blog_entries(FEED_URL)[:5]
    blog_entries_md = "\n\n".join(
        ["- [{title}]({url}) ({published})".format(**entry) for entry in blog_entries]
    )

    til_entries = fetch_til_entries(TIL_URL)[:5]
    til_entries_md = "\n\n".join(
        ["- [{title}]({url}) ({date})".format(**entry) for entry in til_entries]
    )

    readme_contents = replace_chunk(readme_contents, "Blog entries", blog_entries_md)
    readme_contents = replace_chunk(readme_contents, "TILs", til_entries_md)

    readme.open("w").write(readme_contents)
