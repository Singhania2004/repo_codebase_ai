class GraphAnalyzer:

    def __init__(self, graph):
        self.graph = graph

    def who_calls(self, node_id):

        callers = []

        for predecessor in self.graph.predecessors(node_id):

            edge = self.graph[predecessor][node_id]

            if edge["relation"] == "CALLS":
                callers.append(predecessor)

        return callers

    def what_does_it_call(self, node_id):

        callees = []

        for successor in self.graph.successors(node_id):

            edge = self.graph[node_id][successor]

            if edge["relation"] == "CALLS":
                callees.append(successor)

        return callees

    def imported_files(self, file_id):

        imports = []

        for successor in self.graph.successors(file_id):

            edge = self.graph[file_id][successor]

            if edge["relation"] == "IMPORTS":
                imports.append(successor)

        return imports