import re
from typing import Dict, List, Any

class DiffReader:
    """
    Parses Git diff payloads to extract changed files, line numbers,
    modified functions/routes, and code modifications.
    """

    def parse_diff(self, diff_text: str) -> Dict[str, Any]:
        """
        Parses raw git diff string into a structured dictionary.
        """
        files_changed = []
        current_file = None
        added_lines = []
        removed_lines = []
        modified_functions = []
        modified_routes = []

        lines = diff_text.strip().split("\n")
        for line in lines:
            if line.startswith("--- a/") or line.startswith("+++ b/"):
                match = re.search(r"[ab]/(.+)$", line)
                if match:
                    current_file = match.group(1)
                    if current_file not in files_changed:
                        files_changed.append(current_file)
            elif line.startswith("diff --git"):
                match = re.search(r"b/(.+)$", line)
                if match:
                    current_file = match.group(1)
                    if current_file not in files_changed:
                        files_changed.append(current_file)
            elif line.startswith("+") and not line.startswith("+++"):
                content = line[1:].strip()
                added_lines.append(content)
                # Detect route definitions or python functions
                if "@app." in content or "def " in content or "class " in content:
                    modified_functions.append(content)
                if "/api/" in content:
                    route_match = re.search(r"/(api/[a-zA-Z0-9_/{}]+)", content)
                    if route_match:
                        modified_routes.append(route_match.group(1))
            elif line.startswith("-") and not line.startswith("---"):
                content = line[1:].strip()
                removed_lines.append(content)

        return {
            "files_changed": files_changed,
            "total_files": len(files_changed),
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "modified_functions": list(set(modified_functions)),
            "modified_routes": list(set(modified_routes)),
            "raw_diff": diff_text
        }


# Quick Standalone Test
if __name__ == "__main__":
    sample_diff = """
diff --git a/sample_app/main_api.py b/sample_app/main_api.py
--- a/sample_app/main_api.py
+++ b/sample_app/main_api.py
@@ -45,3 +45,3 @@
- if user.role != "admin":
-     return 403
+ if not user:
+     return 401
    """
    reader = DiffReader()
    result = reader.parse_diff(sample_diff)
    print("\n--- BlastShield AI DiffReader Test ---")
    print("Files Changed:", result["files_changed"])
    print("Added Lines:  ", result["added_lines"])
    print("---------------------------------------\n")
