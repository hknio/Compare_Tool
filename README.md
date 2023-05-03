# Compare Tool

This Python script compares two revisions of a git repo by calculating the similarity and difference between them. It supports Solidity, Rust, Python, and Vyper.

The comparison can be done using two methods: Levenshtein distance or Levenshtein ratio. You can also exclude specific file patterns from the comparison and/or narrow the comparison scope.

Levenshtein.distance and Levenshtein.ratio are two different methods to compare the similarity between two strings using the Levenshtein distance algorithm. Here's the difference between them:

- Levenshtein.distance: This function computes the Levenshtein distance between two strings, which is  
     the minimum number of single-character edits (insertions, deletions, or substitutions) required to  
     transform one string into the other. The higher the distance, the more different the strings are.

- Levenshtein.ratio (used by default and recommended): This function computes the similarity ratio between two strings. It is calculated  
    as:
    ```
    (1 - Levenshtein.distance(s1, s2) / max(len(s1), len(s2)))
    ```
    The ratio ranges between 0 and 1, with 1 meaning the strings are identical and 0 meaning they are  
    completely different. You can also express the ratio as a percentage, with values closer to 100%  
    indicating a higher similarity.

In summary, Levenshtein.distance gives you the absolute number of edits required to transform one string into the other, while Levenshtein.ratio provides a normalized similarity score between the two strings.

## Implementation notes
The tool maintains predefined directories `<OS_TMPDIR>/hknio_compare_tool/dir1` and `<OS_TMPDIR>/hknio_compare_tool/dir2`, where `OS_TMPDIR` is the OS base directory for temporary files; for example, on Mac or Linux it is usually `/tmp`; see [documentation of the function that is used to obtain it](https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir).
The two directories contain two clones for the repo, each check-outed at the respective revision to compare.
Each tool run purges the directories, and does clone/checkout from scratch (in the directories). 

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

- `repo`: The git repo url.
- `commit1`: The first revision to compare (commit or branch; tags are not supported).
- `commit2`: The second revision to compare (commit or branch; tags are not supported).
- `--exclude`: (optional) A list of filename patterns to exclude from the comparison. For example: `*.sol folder1 folder2` (default: `None`).
- `--include`: (optional) A list of filename patterns to include in the comparison. This is effectively a narrowing-down of the comparison scope. For example: `*.sol folder1 folder2`. (default: `*` (all files)).
- `--method`: (optional) The comparison method to use: `ratio` or `distance` (default: `ratio`).

Exclude:
To exclude multiple file extensions and folders, you need to provide a list of exclusion patterns to the --exclude argument. For example, if you want to exclude .bak and .tmp files and the folders named build and test, you would use the following command:

- `python compare_directories.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 main --exclude "*.bak" "*.tmp" "*/build/*" "*/test/*"`

Inclusions:
The comparison scope can also be narrowed down via providing inclusion patterns. Example:
- `python compare_directories.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4 --include "*/build/*" "*/test/*" --exclude "*.bak" "*.tmp"`

Here's a breakdown of the patterns used:

- `"*.bak"`: Match all files with the .bak extension.
- `"*.tmp"`: Match all files with the .tmp extension.
- `"*/build/*"`: Match all files within folders named build. The asterisks before and after build are used to match any parent or child directories.
- `"*/test/*"`: Match all files within folders named test. The asterisks before and after test are used to match any parent or child directories.

All file paths are relative to the repo root, without the leading "./".
Please note that the patterns should be enclosed in double quotes to prevent shell expansions.

Examples :
- `python compare_directories.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4` - no options
- `python compare_directories.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4 --exclude "*.bak" "*.tmp" "*/build/*" "*/test/*"` - with exclude argument
- `python compare_directories.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4 --include "*.bak" "*.tmp" "*/build/*" "*/test/*"` - with include argument
- `python compare_tool.py git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4 --method distance` - using Levenshtein.distance

### Docker

Build the Docker image by running the following command in the same directory as the Dockerfile:
- `docker build -t compare-tool .`

To run the script using Docker, use the following command; note that it uses "-v" to pass local SSH keys to Docker, so that the container can have the same git accesses as the host.
- `docker run -v ~/.ssh:/root/.ssh compare-tool git@github.com:hknio/Compare_Tool.git b9a41a8f511d5573cd41bf8987970bc2d727e8d4 b9a41a8f511d5573cd41bf8987970bc2d727e8d4`

## Example Output

| Name of the file | Similarity (Ratio) | Difference (Ratio) | Lines of code |
|------------------|--------------------|--------------------|---------------|
| token.sol        |              96.46 |               3.54 |            41 |
| staking.sol      |              93.21 |               6.79 |           631 |
| vesting.sol      |             100.00 |               0.00 |           102 |
|------------------|--------------------|--------------------|---------------|
| Total            |              94.28 |               5.72 |           774 |
