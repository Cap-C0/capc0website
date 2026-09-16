import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import tomllib
import xml.etree.ElementTree as ET
import os
import argparse
from dotenv import load_dotenv

load_dotenv()


parser = argparse.ArgumentParser(description="Build da website")
parser.add_argument("-r", "--release", action="store_true", help="To go to https site")
parser.add_argument("-u", "--resume", type=str,default="", help="just render a resume pdf to output file")
args = parser.parse_args()


CONTENT_STRING = "<!--CONTENT_HERE-->"
PAGE_TITLE_STRING = "<!--PAGE_TITLE_HERE-->"
TEMPLATE = ""
with open("template.html", encoding ="utf-8") as f:
    TEMPLATE = f.read()

JP_TEMPLATE = ""
with open("template_jp.html", encoding ="utf-8") as f:
    JP_TEMPLATE = f.read()

MD_SCRIPT_PATH = Path(os.getenv("MD_SCRIPT_PATH")).expanduser()
SITE_URL = os.getenv("SITE_URL")
if args.release:
    SITE_URL = "https://www.capc0.com"
OUTPUT_DIR = Path("./website_build")
if args.release:
    OUTPUT_DIR = Path("./dist")
CHROME_PATH = os.getenv("CHROME_PATH")

def main():
    if len(args.resume) > 0: 
        create_resume(Path("./resume.md"), Path("."), args.resume)
        return
    index_path = OUTPUT_DIR / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy("./style.css", OUTPUT_DIR)
    if source_changed(Path("./index.md"), index_path) or source_changed(Path("./template.html"), index_path):
        index_html = subprocess.run([str(MD_SCRIPT_PATH), "-f", "./index.md"], capture_output=True, text=True).stdout.strip()
        index_html = TEMPLATE.replace(CONTENT_STRING, index_html)
        index_html = index_html.replace(PAGE_TITLE_STRING, "Simon's Site")
        with open(index_path, "w", encoding = "utf-8") as f:
            f.write(index_html)
        print("INDEX WRITTEN!")
    create_jp_index()
    create_blog_posts_and_rss_feed()
    create_resume("./resume.md", OUTPUT_DIR, "resume")
    create_resume("./resume_jp.md", OUTPUT_DIR/ "jp", "resume_jp")

def create_jp_index():
    jp_index_path = OUTPUT_DIR / "jp" / "index.html"
    jp_index_path.parent.mkdir(parents=True, exist_ok=True)
    if not source_changed(Path("./index_jp.md"), jp_index_path):
        return
    jp_index_html = subprocess.run([str(MD_SCRIPT_PATH), "-f", "./index_jp.md"], capture_output=True, text=True).stdout.strip()
    jp_index_html = JP_TEMPLATE.replace(CONTENT_STRING, jp_index_html)
    jp_index_html = jp_index_html.replace(PAGE_TITLE_STRING, "サイモンのサイト")
    with open(jp_index_path, "w", encoding = "utf-8") as f:
        f.write(jp_index_html)
    print("JP INDEX WRITTEN!")

def create_blog_posts_and_rss_feed():
    blog_titles_and_dates = []
    blogpost_dir = Path("./blog/")
    blog_changed = False
    for folder in blogpost_dir.iterdir():
        if not folder.is_dir() or folder.name == "template":
            continue
        with open(folder / "post_info.toml", "rb") as f:
            data = tomllib.load(f)
            blog_titles_and_dates.append({
                "title": data.get("title"),
                "date": data.get("date"),
                "folder": folder.name
            })
            
            output_dir = OUTPUT_DIR / "blog" / folder.name
            post_html_path = output_dir / "index.html"
            if not source_changed(folder / "post_info.toml", post_html_path) and not source_changed(folder / "blog_content.md", post_html_path) and not source_changed(Path("./template.html"), post_html_path):
                continue
            blog_changed = True
            print("writing to: " + str(folder))

            shutil.copytree(folder, output_dir, dirs_exist_ok=True)
            
            blog_html = subprocess.run([str(MD_SCRIPT_PATH), "-f", str(folder) + "/blog_content.md"], capture_output=True, text=True).stdout.strip()

            blog_html = f"<h1>{data.get("title")}</h1>\n<h4>{data.get("date")}</h4>\n<hr />\n" + blog_html
            blog_html = TEMPLATE.replace(CONTENT_STRING, blog_html)
            blog_html = blog_html.replace(PAGE_TITLE_STRING, data.get("title"))
            post_html_path = output_dir / "index.html"
            with open(post_html_path, "w", encoding = "utf-8") as f:
                f.write(blog_html)

    if not blog_changed:
        return
    print("Writing blog home page")


    blog_titles_and_dates.sort(key= lambda x: x.get("date"), reverse=True)
    
    rss_root = ET.Element("rss", version="2.0")
    rss_channel = ET.SubElement(rss_root, "channel")
    # required
    rss_title = ET.SubElement(rss_channel, "title")
    rss_title.text = "Simon Martin's Blog"
    rss_link = ET.SubElement(rss_channel, "link")
    rss_link.text = SITE_URL + "/blog"
    rss_description = ET.SubElement(rss_channel, "description")
    rss_description.text = "Simon Martin's ramblings for the world."
    # optional
    rss_lbd = ET.SubElement(rss_channel, "lastBuildDate")
    rss_lbd.text = datetime.now().isoformat()


    blog_page_html = f"""<h1>Blog Posts</h1>\n
    <p><a href=\"{SITE_URL}/blog/capc0-rss.xml\">rss</a></p>\n
    \n<hr />\n <ul class=\"post-list\">\n"""
    for btad in blog_titles_and_dates:
        rss_item = ET.SubElement(rss_channel, "item")
        post_title =ET.SubElement(rss_item, "title")
        post_title.text = btad["title"]
        post_link =ET.SubElement(rss_item, "link")
        post_link.text = SITE_URL + "/blog/" + btad["folder"]
        post_date =ET.SubElement(rss_item, "pubDate")
        post_date.text = btad["date"].isoformat()

        blog_page_html += f"""<li><h3><a href = \"{btad["folder"]}\">{btad["title"]}</a></h3>
        <p>{btad["date"]}</p></li>"""
    blog_page_html += "</ul>"
    blog_page_html = TEMPLATE.replace(CONTENT_STRING, blog_page_html)
    blog_page_html = blog_page_html.replace(PAGE_TITLE_STRING, "Simon's Blog")
    
    blog_page_path = OUTPUT_DIR / "blog" / "index.html"
    blog_page_path.parent.mkdir(parents=True, exist_ok=True)
    with open(blog_page_path, "w", encoding = "utf-8") as f:
        f.write(blog_page_html)

    rss_path = OUTPUT_DIR / "blog" / "capc0-rss.xml"
    with open(rss_path, "wb") as f:
        f.write(ET.tostring(rss_root))

def create_resume(input_md_path: Path, output_dir: Path, output_name: str):
    resume_html_path = output_dir / (output_name + ".html")
    if not source_changed(Path(input_md_path), resume_html_path) and not source_changed(Path("./resume_style.css"), resume_html_path) and not source_changed(Path("./resume_template.html"), resume_html_path):
        return
    print(f"writing resume stuff from {input_md_path} to {output_dir} / {output_name}.")
    resume_template = ""
    with open("resume_template.html", encoding ="utf-8") as f:
        resume_template = f.read()
    resume_html =  subprocess.run([str(MD_SCRIPT_PATH), "-f", input_md_path], capture_output=True, text=True).stdout.strip()
    resume_html = resume_template.replace(CONTENT_STRING, resume_html)
    shutil.copy("./resume_style.css", output_dir)
    with open(resume_html_path, "w", encoding = "utf-8") as f:
        f.write(resume_html)
    subprocess.run(
        [CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={output_dir}/{output_name}.pdf",
        "--no-pdf-header-footer",
         f"{output_dir}/resume.html"
         ]
    )

def source_changed(source_file, out_file):
    source_timestamp = source_file.stat().st_mtime
    source_mod_time = datetime.fromtimestamp(source_timestamp)
    if not out_file.is_file():
        return True
    out_timestamp = out_file.stat().st_mtime
    out_mod_time = datetime.fromtimestamp(out_timestamp)
    return source_mod_time > out_mod_time

if __name__ == "__main__":
    main()
