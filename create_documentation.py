from os.path import join, exists, isfile, isdir, abspath
from os import walk, listdir
import os
from pathlib import Path
import re

s_template: str = """
::: ((MODULE_NAME))
    options:
        show_root_heading: true
        show_source: true
"""
s_template_replace = "((MODULE_NAME))"
s_nav_replace = "((NAV))"
s_python_class_def_regex = "class\s+([a-zA-Z0-9()]+)\s*:"
s_nav_indent: str = "  "


class NavNode:
    def __init__(self, name: str, parent=None) -> None:
        self.name: str = name
        self.parent = parent
        self.absolute_file_path = ""
        self.relative_file_path = ""
        self.children: list[NavNode] = []

    def get_fq_name(self) -> str:
        if self.parent is None:
            return self.name
        return self.parent.get_fq_name() + "." + self.name

    def get_display_name(self) -> str:
        if self.name == "index":
            return "Overview"
        return self.name

    def get_doc_path(self) -> str:
        return self.get_fq_name().replace(".", "/") + ".md\n"

    def get_nav(self) -> str:
        nav = "- " + self.get_display_name() + ":"
        if len(self.children) > 0:
            # counter for proper indentation
            parent_count: int = 0
            current_parent = self.parent
            while current_parent != None:
                parent_count += 1
                current_parent = current_parent.parent
            nav += "\n"
            # make index be the first entry
            has_index: bool = False
            for child in self.children:
                if child.name == "index":
                    has_index = True
                    nav += s_nav_indent * parent_count + child.get_nav()
            for child in self.children:
                if has_index and child.name == "index":
                    continue
                nav += s_nav_indent * parent_count + child.get_nav()
        else:
            nav += " " + self.get_doc_path()
        return nav


def get_python_files(folder: Path):
    for root, dirs, files in walk(folder):
        for file in files:
            file_path = str(Path(root, file))
            if file_path.endswith(".py"):
                yield abspath(file_path)
        for dir in dirs:
            yield from get_python_files(Path(root, dir))


def build_nav(folder: Path, base_folder: Path) -> NavNode:
    root = NavNode(Path(folder).name)
    if folder == base_folder:
        root.name = "nav"
    for name in listdir(folder):
        path = join(folder, name)
        if isdir(path):
            dir_node: NavNode = build_nav(path, base_folder)
            root.children.append(dir_node)
            dir_node.parent = root
        elif isfile(path) and path.endswith(".md"):
            file_node: NavNode = NavNode(name.replace(".md", ""))
            root.children.append(file_node)
            file_node.parent = root
            file_node.absolute_file_path = path
            file_node.relative_file_path = path.replace(str(base_folder), "")
    return root


base_folder: Path = Path(abspath(Path(__file__).parent))
docs_folder: Path = Path(abspath(join(base_folder, "docs")))
chessapp_folder: Path = Path(abspath(join(base_folder, "chessapp")))
mkdocs_yml_file: Path = Path(abspath(join(base_folder, "mkdocs.yml")))
mkdocs_template_file: Path = Path(
    abspath(join(base_folder, "mkdocs-template.yml")))
python_class_regex = re.compile(s_python_class_def_regex)

# create a markdown file for each python file
python_files = get_python_files(chessapp_folder)
for python_file in python_files:
    sub_path = str(python_file)[len(str(base_folder)) + 1:]
    doc_file: Path = Path(join(docs_folder, sub_path.replace(".py", ".md")))
    if not exists(doc_file):
        print("creating " + str(doc_file))
        Path(doc_file.parent).mkdir(parents=True, exist_ok=True)
        doc_file.touch()
    file_name_reduced: str = sub_path.replace(".py", "").split(os.sep)[-1]
    with open(doc_file, "w") as f:
        f.write("# " + file_name_reduced + "\n")
        with open(python_file, "r") as pf:
            lines = pf.readlines()
            for line in lines:
                if python_class_regex.match(line):
                    class_name: str = line.replace("class", "").strip()
                    if "(" in class_name:
                        class_name = class_name.split("(")[0].strip()
                    else:
                        class_name = class_name.split(":")[0].strip()
                    fq_class_name: str = sub_path.replace(".py", "").replace(
                        os.sep, ".") + "." + class_name
                    f.write(s_template.replace(
                        s_template_replace, fq_class_name))
        f.write("\n# Source\n")
        f.write("```python\n")
        with open(python_file, "r") as pf:
            f.write(pf.read())
        f.write("```\n")

# for each doc folder check if there is a index.md file and if not create one
for root, dirs, files in walk(docs_folder):
    for dir in dirs:
        index_file: Path = Path(join(root, dir, "index.md"))
        if not exists(index_file):
            print("creating " + str(index_file))
            index_file.touch()
            with open(index_file, "w") as f:
                f.write("# " + dir + "\n")

# create the navigation in the mkdocs.yml file
nav: NavNode = build_nav(docs_folder, docs_folder)
template: str = Path(mkdocs_template_file).read_text()
template = template.replace(s_nav_replace, nav.get_nav()).replace(
    "nav/", "").replace("- nav", "nav")
with open(mkdocs_yml_file, "w") as f:
    f.write(template)


# build mkdocs
os.system("pipenv run mkdocs build")
