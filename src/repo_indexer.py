class RepoIndexer:

    def __init__(self, parser):

        self.parser = parser

    def build_index(self, py_files):

        repo_index = {
            "files": [],
            "functions": [],
            "classes": []
        }

        for file in py_files:

            parsed = self.parser.parse_file(file)

            repo_index["files"].append({
                "id": file.name,
                "path": str(file),
                "imports": parsed["imports"]
            })

            repo_index["functions"].extend(
                parsed["functions"]
            )

            repo_index["classes"].extend(
                parsed["classes"]
            )

        return repo_index
    

    def build_chunks(self, repo_index):

        chunks = []

        # ---------- functions ----------
        for func in repo_index["functions"]:

            file_name = func["id"].split("::")[0]

            text = f"""
    File: {file_name}

    Function: {func['name']}

    Arguments:
    {func['args']}

    Docstring:
    {func['docstring']}

    Code:
    {func['source_code']}
    """

            chunks.append({
                "id": func["id"],
                "type": "function",
                "text": text
            })

        # ---------- classes ----------
        for cls in repo_index["classes"]:

            file_name = cls["id"].split("::")[0]

            class_text = f"""
    File: {file_name}

    Class: {cls['name']}

    Docstring:
    {cls['docstring']}

    Code:
    {cls['source_code']}
    """

            chunks.append({
                "id": cls["id"],
                "type": "class",
                "text": class_text
            })

            # ---------- methods ----------
            for method in cls["methods"]:

                method_text = f"""
    File: {file_name}

    Class: {cls['name']}

    Method: {method['name']}

    Arguments:
    {method['args']}

    Docstring:
    {method['docstring']}

    Code:
    {method['source_code']}
    """

                chunks.append({
                    "id": method["id"],
                    "type": "method",
                    "text": method_text
                })

        return chunks