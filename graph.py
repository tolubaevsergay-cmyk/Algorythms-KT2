from collections import defaultdict, deque
from typing import List, Set, Optional, Dict


class DependencyGraph:

    def __init__(self):
        self._adj: Dict[str, Set[str]] = defaultdict(set)
        self._vertices: Set[str] = set()


    def add_component(self, name: str) -> None:
        self._vertices.add(name)
        _ = self._adj[name]

    def add_dependency(self, from_comp: str, to_comp: str) -> None:
        self.add_component(from_comp)
        self.add_component(to_comp)
        self._adj[from_comp].add(to_comp)

    @property
    def vertices(self) -> Set[str]:
        return self._vertices

    def get_neighbors(self, node: str) -> Set[str]:
        return self._adj.get(node, set())


    def _compute_indegrees(self) -> Dict[str, int]:
        indeg = {v: 0 for v in self._vertices}
        for u in self._adj:
            for v in self._adj[u]:
                indeg[v] += 1
        return indeg

    def get_topological_order(self) -> Optional[List[str]]:
        indeg = self._compute_indegrees()
        queue = deque([v for v, d in indeg.items() if d == 0])
        order: List[str] = []

        while queue:
            u = queue.popleft()
            order.append(u)
            for v in sorted(self._adj.get(u, set())):
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)

        if len(order) != len(self._vertices):
            return None
        return order

    def is_acyclic(self) -> bool:
        return self.get_topological_order() is not None


class DependencyAnalyzer:

    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def find_dependencies_bfs(self, start: str) -> List[List[str]]:
        if start not in self.graph.vertices:
            raise ValueError(f"Компонент '{start}' отсутствует в графе")

        levels: List[List[str]] = []
        frontier = {start}

        while frontier:
            next_level_set: Set[str] = set()
            for node in frontier:
                for nbr in self.graph.get_neighbors(node):
                    if nbr == start:
                        continue
                    next_level_set.add(nbr)

            next_level_set -= frontier

            if not next_level_set:
                break
            levels.append(sorted(next_level_set))
            frontier = next_level_set

        return levels

    def find_dependencies_dfs(self, start: str) -> Set[str]:
        if start not in self.graph.vertices:
            raise ValueError(f"Компонент '{start}' отсутствует в графе")

        visited: Set[str] = set()
        stack = list(self.graph.get_neighbors(start))

        while stack:
            node = stack.pop()
            if node in visited or node == start:
                continue
            visited.add(node)
            for nbr in self.graph.get_neighbors(node):
                if nbr not in visited and nbr != start:
                    stack.append(nbr)

        return visited

    def describe_all(self) -> str:
        lines = []
        for comp in sorted(self.graph.vertices):
            deps = sorted(self.graph.get_neighbors(comp))
            deps_str = ", ".join(deps) if deps else "—"
            lines.append(f"{comp} -> {deps_str}")
        return "\n".join(lines)

def build_example_graph() -> DependencyGraph:
    g = DependencyGraph()
    g.add_dependency("A", "B")
    g.add_dependency("A", "C")
    g.add_dependency("B", "D")
    g.add_dependency("C", "D")
    g.add_dependency("C", "E")
    g.add_dependency("E", "B")
    return g


if __name__ == "__main__":
    graph = build_example_graph()
    analyzer = DependencyAnalyzer(graph)

    print("Граф зависимостей:")
    print(analyzer.describe_all())
    print()

    order = graph.get_topological_order()
    if order is None:
        print("Обнаружен цикл — проект нельзя собрать.")
    else:
        print("Топологический порядок сборки:", order)

    print("BFS для 'A':", analyzer.find_dependencies_bfs("A"))

    print("DFS для 'A':", sorted(analyzer.find_dependencies_dfs("A")))
