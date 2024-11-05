import logging
from pathlib import Path
import re

# Logging
logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")
logging.info("#=== Start program ===#")


def fix_docstring() -> None:
    """
    関数に変数が含まれるとdocstring生成の際に無限ループとなる場合があるため、修正する関数
    * class_gcalendar.pyのget関数の引数にdatetime.datetime.now()があり、無限ループを引き起こしている。
    docstring出力後に修正する前提の関数とする
    """
    # class_gcalendar.md の修正
    target_file = Path('docs/docstring/class_gcalendar.md')
    if not target_file.is_file():
        logging.info(f"File not found: {target_file}")
        return
    target_sentence_ptrn = r"start_date:.*, prior_days"
    replace_sentence = "start_date: datetime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9), 'JST')), prior_days"
    change_string(target_sentence_ptrn, replace_sentence, target_file)


def change_string(pattern: str, replace_str: str, file_path: Path) -> None:
    """
    Args:
        pattern (str): input pattern. raw string is preferable.
        replace_str (str): string to be.
        file_path (Path): target file path.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        docfile = f.read()
    new_docfile = re.sub(pattern, replace_str, docfile)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_docfile)
        logging.info(f"File is replaced: {file_path}")

# Main ---


if __name__ == "__main__":
    fix_docstring()
