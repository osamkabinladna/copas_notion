import subprocess


def link2id(link):
    """
    Converts a notion page link to an id
    ex.
    turns "https://www.notion.so/GRE-Quant-Hard-380c78c0e0f54565bdbdc4ccb079050d?pvs=4"
    into "380c78c0-e0f5-4565-bdbd-c4ccb079050d"
    :param link: notion link
    :return: page id
    """
    li = link.split("-")[-1].split("?")[0]

    indices = [8, 12, 16, 20]
    parts = [li[i:j] for i, j in zip([0] + indices, indices + [None])]
    return "-".join(parts)


def clean_latex(text, copy: bool = False):
    """
    :param text: text containing latex notations (backslash parentheses or square brackets)
    :param copy: whether to copy the cleaned text into the clipboard
    :return: clean text compatible with katex
    """
    invalid_strs = [r"\(", r"\[", r"\)", r"\]"]
    for invalid in invalid_strs:
        text = text.replace(invalid, "")
    if copy:
        subprocess.run("pbcopy", text=True, input=text)
    else:
        return text

