import networkx as nx


class GraphBuilder:

    def build_graph(self, repo_index):

        graph = nx.DiGraph()

        # ---------- files ----------
        for file in repo_index["files"]:

            graph.add_node(
                file["id"],
                type="file"
            )


        # file imports
        file_lookup = {
            f["id"].replace(".py", ""): f["id"]
            for f in repo_index["files"]
        }

        for file in repo_index["files"]:

            source_file = file["id"]

            for imported_module in file["imports"]:

                module_name = imported_module.split(".")[-1]

                if module_name in file_lookup:

                    graph.add_edge(
                        source_file,
                        file_lookup[module_name],
                        relation="IMPORTS"
                    )


        # ---------- classes ----------
        for cls in repo_index["classes"]:

            graph.add_node(
                cls["id"],
                type="class"
            )

        # ---------- functions ----------
        for func in repo_index["functions"]:

            graph.add_node(
                func["id"],
                type="function"
            )

        # ---------- file contains function ----------
        for func in repo_index["functions"]:

            file_name = func["id"].split("::")[0]

            graph.add_edge(
                file_name,
                func["id"],
                relation="CONTAINS"
            )

        # ---------- file contains class ----------
        for cls in repo_index["classes"]:

            file_name = cls["id"].split("::")[0]

            graph.add_edge(
                file_name,
                cls["id"],
                relation="CONTAINS"
            )

        # ---------- class contains methods ----------
        for cls in repo_index["classes"]:

            for method in cls["methods"]:

                graph.add_node(
                    method["id"],
                    type="method"
                )

                graph.add_edge(
                    cls["id"],
                    method["id"],
                    relation="CONTAINS"
                )

        # ---------- calls ----------
        name_to_id = {}

        for func in repo_index["functions"]:
            name_to_id[func["name"]] = func["id"]

        for cls in repo_index["classes"]:
            for method in cls["methods"]:
                name_to_id[method["name"]] = method["id"]

        # top-level functions
        for func in repo_index["functions"]:

            for called_name in func["calls"]:

                if called_name in name_to_id:

                    graph.add_edge(
                        func["id"],
                        name_to_id[called_name],
                        relation="CALLS"
                    )

        # methods
        for cls in repo_index["classes"]:

            for method in cls["methods"]:

                for called_name in method["calls"]:

                    if called_name in name_to_id:

                        target = name_to_id[called_name]

                        if target != method["id"]:

                            graph.add_edge(
                                method["id"],
                                target,
                                relation="CALLS"
                            )

        return graph