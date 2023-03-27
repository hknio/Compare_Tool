# Compare Tool

This Python script compares two directories containing source code files by calculating the similarity and difference between them. It supports Solidity, Rust, Python, and Vyper.

The comparison can be done using two methods: Levenshtein distance or Levenshtein ratio. You can also exclude specific file patterns from the comparison.

Levenshtein.distance and Levenshtein.ratio are two different methods to compare the similarity between two strings using the Levenshtein distance algorithm. Here's the difference between them:

- Levenshtein.distance: This function computes the Levenshtein distance between two strings, which is  
     the minimum number of single-character edits (insertions, deletions, or substitutions) required to  
     transform one string into the other. The higher the distance, the more different the strings are.

- Levenshtein.ratio: This function computes the similarity ratio between two strings. It is calculated  
    as:
    ```
    (1 - Levenshtein.distance(s1, s2) / max(len(s1), len(s2)))
    ```
    The ratio ranges between 0 and 1, with 1 meaning the strings are identical and 0 meaning they are  
    completely different. You can also express the ratio as a percentage, with values closer to 100%  
    indicating a higher similarity.

In summary, Levenshtein.distance gives you the absolute number of edits required to transform one string into the other, while Levenshtein.ratio provides a normalized similarity score between the two strings.

## Use Case

This tool can help to identify and analyze the changes made between the two versions and provide a quantitative measure of their differences.

## Prerequisites

- Python 3.6 or higher
- Levenshtein and tabulate libraries installed:
    ```
    pip3 install -r requirements.txt
    ```
- Docker (optional):
    ```
    pip3 install -r requirements.txt
    ```

## Usage

You can run the script directly using Python or use the Docker image.

### Command line

Run the script from the command line with the following arguments:

- `dir1`: The first directory to compare.
- `dir2`: The second directory to compare.
- `--exclude`: (optional) A list of filename patterns to exclude from the comparison. For example: `*.sol folder1 folder2` (default: `None`).
- `--method`: (optional) The comparison method to use: `ratio` or `distance` (default: `ratio`).

Exclude:
To exclude multiple file extensions and folders, you need to provide a list of exclusion patterns to the --exclude argument. For example, if you want to exclude .bak and .tmp files and the folders named build and test, you would use the following command:

- `python compare_directories.py dir1 dir2 --exclude "*.bak" "*.tmp" "*/build/*" "*/test/*"`

Here's a breakdown of the exclusion patterns used:

- `"*.bak"`: Exclude all files with the .bak extension.
- `"*.tmp"`: Exclude all files with the .tmp extension.
- `"*/build/*"`: Exclude all files within folders named build. The asterisks before and after build are used to match any parent or child directories.
- `"*/test/*"`: Exclude all files within folders named test. The asterisks before and after test are used to match any parent or child directories.

Please note that the patterns should be enclosed in double quotes to prevent shell expansions.

Examples :
- `python compare_tool.py dir1 dir2` - no options
- `python compare_directories.py dir1 dir2 --exclude "*.bak" "*.tmp" "*/build/*" "*/test/*"` - with exclude argument
- `python compare_tool.py dir1 dir2 --method distance` - using Levenshtein.distance

### Docker

Build the Docker image by running the following command in the same directory as the Dockerfile:
- `docker build -t compare-tool .`

To run the script using Docker, use the following command:
- `docker run -v <path-to-dir1>:/dir1 -v <path-to-dir2>:/dir2 compare-tool /dir1 /dir2`

Replace `<path-to-dir1>` and `<path-to-dir2>` with the actual paths to the directories you want to compare. For example:
- `docker run -v e:\project\1:/dir1 -v e:\project\:/dir2 compare-tool /dir1 /dir2`

## Example Output

| Name of the file | Similarity (Ratio) | Difference (Ratio) | Lines of code | Lines Difference |
|------------------|--------------------|--------------------|---------------|------------------|
| token.sol        |              96.46 |               3.54 |            41 |               -3 |
| staking.sol      |              93.21 |               6.79 |           631 |              -25 |
| vesting.sol      |             100.00 |               0.00 |           102 |                0 |
|------------------|--------------------|--------------------|---------------|------------------|
| Total            |              94.28 |               5.72 |           774 |              -28 |

## Notes

- When running the script using Docker, it is recommended to use Command Prompt or PowerShell on Windows, as Git Bash may have issues handling Windows paths correctly.