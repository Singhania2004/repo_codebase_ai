import ast
from pathlib import Path


class CodeVisitor(ast.NodeVisitor):

    def __init__(self, source, file_name):

        self.source = source
        self.file_name = file_name

        self.imports = []
        self.functions = []
        self.classes = []

        self.current_class = None

    def extract_function(self, node, class_name=None):

        if class_name:
            unique_id = f"{self.file_name}::{class_name}.{node.name}"
        else:
            unique_id = f"{self.file_name}::{node.name}"

        return {
            "id": unique_id,
            "name": node.name,
            "class_name": class_name,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "calls": self.extract_calls(node),
            "source_code": ast.get_source_segment(self.source, node)
        }

    def extract_class(self, node):

        return {
            "id": f"{self.file_name}::{node.name}",
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "line_start": node.lineno,
            "line_end": node.end_lineno,
            "source_code": ast.get_source_segment(self.source, node),
            "methods": []
        }
    
    def extract_calls(self, node):

        calls = []

        for child in ast.walk(node):

            if isinstance(child, ast.Call):

                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)

                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)

        return list(set(calls))

    def visit_Import(self, node):

        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node):

        module = node.module if node.module else ""
        self.imports.append(module)

    def visit_FunctionDef(self, node):

        if self.current_class is not None:

            function_info = self.extract_function(
                node,
                self.current_class["name"]
            )

            self.current_class["methods"].append(function_info)

        else:

            function_info = self.extract_function(node)

            self.functions.append(function_info)

    def visit_AsyncFunctionDef(self, node):

        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):

        class_info = self.extract_class(node)

        self.classes.append(class_info)

        previous_class = self.current_class
        self.current_class = class_info

        self.generic_visit(node)

        self.current_class = previous_class


class CodeParser:

    def parse_file(self, file_path):

        file_path = Path(file_path)

        with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
        ) as f:

            source = f.read()

        tree = ast.parse(source)

        visitor = CodeVisitor(
            source,
            file_path.name
        )

        visitor.visit(tree)

        return {
            "file": str(file_path),
            "imports": visitor.imports,
            "functions": visitor.functions,
            "classes": visitor.classes
        }