import subprocess
from pathlib import Path
import shutil
import tomllib

REPLACE_STRING = "<!--CONTENT_HERE-->"
OUTPUT_DIR = Path("./website_build")
TEMPLATE = ""
with open("template.html", encoding ="utf-8") as f:
    TEMPLATE = f.read()
    
MD_SCRIPT_PATH = Path("~/Projects/common_mark_rust/target/release/common_mark_rust").expanduser()

def main():
    index_html = subprocess.run([str(MD_SCRIPT_PATH), "-f", "./index.md"], capture_output=True, text=True).stdout.strip()
    result = TEMPLATE.replace(REPLACE_STRING, index_html)

    # print(result)
    shutil.copy("./style.css", OUTPUT_DIR)
    index_path = OUTPUT_DIR / "index.html"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding = "utf-8") as f:
        f.write(result)
    print("INDEX WRITTEN!")
    create_blog_posts()

# class blog_post:
#     def __init__(self, title, date) -> None:
#         self.

def create_blog_posts():
    blog_titles_and_dates = []
    blogpost_dir = Path("./blog/")
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
            shutil.copytree(folder, output_dir, dirs_exist_ok=True)
            
            blog_html = subprocess.run([str(MD_SCRIPT_PATH), "-f", str(folder) + "/blog_content.md"], capture_output=True, text=True).stdout.strip()

            blog_html = f"<h1>{data.get("title")}</h1>\n<h4>{data.get("date")}</h4>\n<hr />\n" + blog_html
            blog_html = TEMPLATE.replace(REPLACE_STRING, blog_html)
            post_html_path = output_dir / "index.html"
            with open(post_html_path, "w", encoding = "utf-8") as f:
                f.write(blog_html)

    blog_titles_and_dates.sort(key= lambda x: x.get("date"))
    blog_page_html = "<h1>Blog Posts</h1>\n<hr />\n <ul>\n"
    for btad in blog_titles_and_dates:
        blog_page_html += f"<li><h3><a href = \"{btad["folder"]}\">{btad["title"]}</a></h3><p>{btad["date"]}</p></li>"
    blog_page_html += "</ul>"
    blog_page_html = TEMPLATE.replace(REPLACE_STRING, blog_page_html)
    blog_page_path = OUTPUT_DIR / "blog" / "index.html"
    print(blog_page_path)
    blog_page_path.parent.mkdir(parents=True, exist_ok=True)
    with open(blog_page_path, "w", encoding = "utf-8") as f:
        f.write(blog_page_html)






            




if __name__ == "__main__":
    main()
