import argparse
import fnmatch
import re
from pathlib import Path
from typing import List, Tuple, Optional

import Levenshtein
from tabulate import tabulate


def matches(file_path: str, patterns: List[str], relative_to: Optional[str | Path] = None) -> bool:
    """
    Check if a given file path matches a list of patterns.

    :param file_path: The file path to be checked.
    :param patterns: A list of patterns (wildcards).
    :param relative_to: a parent path to omit before matching against the patterns. OPTIONAL
    :return: True if the file matches the patterns, False otherwise.
    """
    assert patterns, "`patterns` must be given to avoid confusion depending on what the patterns mean"
    if relative_to:
        file_path = str(Path(file_path).relative_to(relative_to))
    return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns)


def is_excluded(file_path: str,
                exclude_patterns: Optional[List[str]] = None,
                include_patterns: Optional[List[str]] = None,
                relative_to: Optional[str | Path] = None) -> bool:
    """
    Check if a given file path is excluded based on a list of exclusion and inclusion patterns.

    :param file_path: The file path to be checked.
    :param include_patterns: A list of inclusion patterns (wildcards). OPTIONAL
    :param exclude_patterns: A list of exclusion patterns (wildcards). OPTIONAL
    :param relative_to: a parent path to omit before matching against the patterns. OPTIONAL
    :return: True if the file is excluded, False otherwise.
    """
    excluded = exclude_patterns and matches(file_path, exclude_patterns, relative_to=relative_to)
    if not include_patterns:
        return excluded
    included = matches(file_path, include_patterns, relative_to=relative_to)
    assert not excluded or not included, (f"conflicting patterns for file path: {file_path}.\n"
                                          f"include_patterns: {include_patterns}.\n"
                                          f"exclude patterns: {exclude_patterns}.")
    return not included


# fixme: unused
def get_files(directory: str, exclude: List[str], include: List[str]) -> List[str]:
    """
    Get all the file paths in a directory, excluding the ones that match the given exclusion patterns.

    :param directory: The directory to search for files.
    :param exclude: A list of exclusion patterns (wildcards).
    :param include: A list of inclusion patterns (wildcards).
    :return: A list of file paths in the given directory, excluding the ones that match the exclusion patterns.
    """
    all_files = [str(file) for file in Path(directory).rglob('*') if
                 file.is_file() and not is_excluded(str(file),
                                                    exclude_patterns=exclude,
                                                    include_patterns=include,
                                                    relative_to=directory)]
    return all_files

def get_language_from_extension(extension: str) -> str:
    """
    Get the programming language based on a given file extension.

    :param extension: The file extension.
    :return: The programming language associated with the given file extension.
    :raises ValueError: If the given file extension is not supported.
    """
    languages = {
        '.sol': 'Solidity',
        '.rs': 'Rust',
        '.py': 'Python',
        '.vy': 'Vyper',
        '.scilla': 'Scilla',
    }
    language = languages.get(extension)
    if language is None:
        raise ValueError(f"Unsupported file extension: {extension}")
    return language

def count_lines(file_path: str) -> Tuple[int, str]:
    """
    Count the non-empty lines of code in a file, excluding comments.

    :param file_path: The file path.
    :return: A tuple containing the number of non-empty lines and the programming language.
    """
    file_extension = Path(file_path).suffix.lower()

    language = get_language_from_extension(file_extension)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content_no_comments = remove_comments(language, content)
    lines = content_no_comments.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    return len(non_empty_lines), language

def read_file_contents(file_path: str) -> str:
    """
    Read the contents of a file and return it as a string.

    :param file_path: The file path.
    :return: The contents of the file as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    :param s1: The first string.
    :param s2: The second string.
    :return: The Levenshtein distance between the two strings.
    """
    distance = Levenshtein.distance(s1, s2)
    return distance


def levenshtein_ratio(s1: str, s2: str) -> float:
    """
    Calculate the Levenshtein ratio between two strings.

    :param s1: The first input string.
    :param s2: The second input string.
    :return: The Levenshtein ratio (0.0 to 1.0) between the two input strings.
    """
    ratio = Levenshtein.ratio(s1, s2)
    return ratio


def remove_rust_solidity_comments(code: str) -> str:
    """
    Remove comments from Rust or Solidity code.

    :param code: The input code as a string.
    :return: The input code with comments removed.
    """
    code = re.sub(r"/\*[\s\S]*?\*/|//.*", "", code)
    return code


def remove_python_comments(code: str) -> str:
    """
    Remove comments from Python code.

    :param code: The input code as a string.
    :return: The input code with comments removed.
    """
    code = re.sub(r"(?:#.*$|'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\")", "", code, flags=re.MULTILINE)
    return code

def remove_vyper_comments(code: str) -> str:
    """
    Remove comments from Vyper code.

    :param code: The input code as a string.
    :return: The input code with comments removed.
    """
    code = re.sub(r"#[^\n]*", "", code)
    return code

def remove_scilla_comments(code: str) -> str:
    """
    Remove comments from Scilla code.

    :param code: The input code as a string.
    :return: The input code with comments removed.
    """
    code = re.sub(r"\(\*.*?\*\)", "", code)
    return code

def remove_comments(language: str, code: str) -> str:
    """
    Remove comments from code in a given language.

    :param language: The programming language of the input code.
    :param code: The input code as a string.
    :return: The input code with comments removed.
    """
    if language in ['Rust', 'Solidity']:
        return remove_rust_solidity_comments(code)
    elif language == 'Python':
        return remove_python_comments(code)
    elif language == 'Vyper':
        return remove_vyper_comments(code)
    elif language == 'Scilla':
        return remove_scilla_comments(code)
    else:
        raise NotImplementedError(f"Unsupported language: {language}")

def compare_files(file1: str, file2: str, language1: str, language2: str, method: str = 'ratio') -> Tuple[float, float, float, float, int]:
    """
    Compare two source code files of the same language.

    :param file1: The first input file path.
    :param file2: The second input file path.
    :param language1: The programming language of the first file.
    :param language2: The programming language of the second file.
    :param method: The comparison method to use ('ratio' or 'distance').
    :return: A tuple with the similarity and difference (distance or ratio), and the lines of code of updated file.
    """
    file1_abs_path = str(Path(file1).resolve())
    file2_abs_path = str(Path(file2).resolve())

    content1 = read_file_contents(file1_abs_path)
    content2 = read_file_contents(file2_abs_path)

    if language1 != language2:
        raise ValueError("Files have different languages, cannot compare.")

    content1_no_comments = remove_comments(language1, content1)
    content2_no_comments = remove_comments(language2, content2)

    lines1 = [line for line in content1_no_comments.splitlines() if line.strip()]
    lines2 = [line for line in content2_no_comments.splitlines() if line.strip()]

    content1_filtered = "\n".join(lines1)
    content2_filtered = "\n".join(lines2)

    loc2 = len(lines2)

    if method == 'distance':
        distance = levenshtein_distance(content1_filtered, content2_filtered)
        max_distance = max(len(content1_filtered), len(content2_filtered))
        similarity_distance = (1 - (distance / max_distance)) * 100
        difference_distance = 100 - similarity_distance
        return similarity_distance, difference_distance, None, None, loc2
    else:  # method == 'ratio'
        ratio = levenshtein_ratio(content1_filtered, content2_filtered)
        similarity_ratio = ratio * 100
        difference_ratio = 100 - similarity_ratio
        return None, None, similarity_ratio, difference_ratio, loc2


def compare_directory_contents(dir1: str, dir2: str,
                               exclude: List[str],
                               include: List[str],
                               method: str) -> List[Tuple[str, float, float, float, float, int]]:
    """
    Compare the contents of two directories, excluding specified files.

    :param dir1: The first input directory path.
    :param dir2: The second input directory path.
    :param exclude: A list of filename patterns to exclude from the comparison.
    :param include: A list of filename patterns to include in the comparison.
    :param method: The comparison method to use ('ratio' or 'distance').
    :return: A list of tuples containing comparison results for each pair of matched files.
    """
    files1 = {f.name: f for f in Path(dir1).rglob('*') if f.is_file()}
    files2 = {f.name: f for f in Path(dir2).rglob('*') if f.is_file()}
    comparison_results = []
    # Files present in both directories
    common_files = files1.keys() & files2.keys()

    for file_name in common_files:
        file1 = files1[file_name]
        file2 = files2[file_name]

        # filter files
        if any(is_excluded(str(f), exclude_patterns=exclude, include_patterns=include, relative_to=d)
               for f, d in [(file1, dir1), (file2, dir2)]):
            continue

        file1 = files1[file_name]
        file2 = files2[file_name]
        lines1, language1 = count_lines(str(file1))
        lines2, language2 = count_lines(str(file2))
        sim_dist, diff_dist, sim_ratio, diff_ratio, lines_of_code = compare_files(str(file1), str(file2), language1, language2, method)
        lines_difference = lines2 - lines1
        comparison_results.append((file_name, sim_dist, diff_dist, sim_ratio, diff_ratio, lines_of_code, lines_difference))

    removed_files = files1.keys() - files2.keys()
    added_files = files2.keys() - files1.keys()
    
    for file_name in removed_files | added_files:
        lines_difference = 0
        is_removed_file = file_name in removed_files
        (file_path, file_dir) = (files1[file_name], dir1) if is_removed_file else (files2[file_name], dir2)

        # filter files
        if is_excluded(str(file_path), exclude=exclude, include=include, relative_to=file_dir):
            continue

        if is_removed_file:
            print(f"{file_name} removed in the updated version.")
            lines_of_code, _ = count_lines(file_path)
            lines_difference = -lines_of_code
        else:  # file_name in added_files
            print(f"{file_name} is a new file in the updated version.")
            lines_of_code, _ = count_lines(file_path)
            lines_difference = lines_of_code

        comparison_results.extend([(file_name, 0.0, 100.0, 0.0, 100.0, lines_of_code, lines_difference)])

    return comparison_results


def main(dir1: str, dir2: str,
         exclude: List[str] = None,
         include: List[str] = None,
         method: str = 'ratio') -> List[Tuple[str, float, float, float, float, int, int]]:
    """
    Compare two directories containing source code files.

    :param dir1: The first input directory path.
    :param dir2: The second input directory path.
    :param exclude: A list of filename patterns to exclude from the comparison (default: empty list).
    :param method: The comparison method to use ('ratio' or 'distance', default: 'ratio').
    :return: A list of tuples containing comparison results for each pair of matched files.
    """
    if exclude is None:
        exclude = []
    if include is None:
        include = []
    results = compare_directory_contents(dir1, dir2, exclude, include, method)
    return results

# Main function and argparse code ...
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare two directories containing source code files.')
    parser.add_argument('dir1', help='First directory')
    parser.add_argument('dir2', help='Second directory')
    parser.add_argument('--exclude', nargs='+', default=[], help='List of filename patterns to exclude')
    parser.add_argument('--include', nargs='+', default=[], help='List of filename patterns to include')
    parser.add_argument('--method', choices=['ratio', 'distance'], default='ratio', help='Comparison method: ratio or distance')
    args = parser.parse_args()

    results = main(args.dir1, args.dir2, args.exclude, args.include, args.method)

    if len(results) > 0:
        total_lines_of_code = sum(r[-2] for r in results)

        if args.method == 'distance':
            headers = ["Name of the file", "Similarity (Distance)", "Difference (Distance)", "Lines of code"]
            total_similarity = sum(r[1] * r[5] / 100 for r in results) / total_lines_of_code * 100
            total_difference = 100 - total_similarity
            results = [(r[0], format(r[1], '.2f'), format(r[2], '.2f'), r[5]) for r in results]
        else:  # method == 'ratio'
            headers = ["Name of the file", "Similarity (Ratio)", "Difference (Ratio)", "Lines of code"]
            total_similarity = sum(r[3] * r[5] / 100 for r in results) / total_lines_of_code * 100
            total_difference = 100 - total_similarity
            results = [(r[0], format(r[3], '.2f'), format(r[4], '.2f'), r[5]) for r in results]

        total_lines_difference = sum(r[-1] for r in results)

        footer = ["Total", format(total_similarity, '.2f'), format(total_difference, '.2f'), total_lines_of_code]

        # Modify the results to include the footer and a separator line
        results.append(["-" * len(header) for header in headers])
        results.append(footer)

        # Print the modified results table
        print(tabulate(results, headers=headers, tablefmt="pretty", numalign="right"))
    else:
        print("No matching files found.")
