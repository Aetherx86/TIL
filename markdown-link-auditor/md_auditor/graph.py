from collections import defaultdict
from typing import Dict, List, Set, Tuple

class TarjanSCC:
    """
    Tarjan's algorithm for computing Strongly Connected Components (SCCs)
    in a directed documentation dependency graph. Identifies mutual circular
    reference clusters across markdown documents.
    """
    def __init__(self, adj_list: Dict[str, Set[str]]):
        self.adj = adj_list
        self.index = 0
        self.indices: Dict[str, int] = {}
        self.lowlink: Dict[str, int] = {}
        self.on_stack: Dict[str, bool] = defaultdict(bool)
        self.stack: List[str] = []
        self.sccs: List[List[str]] = []

    def compute_scc(self) -> List[List[str]]:
        for node in self.adj:
            if node not in self.indices:
                self._strongconnect(node)
        return [scc for scc in self.sccs if len(scc) > 1]

    def _strongconnect(self, u: str):
        self.indices[u] = self.index
        self.lowlink[u] = self.index
        self.index += 1
        self.stack.append(u)
        self.on_stack[u] = True

        for v in self.adj.get(u, set()):
            if v not in self.indices:
                self._strongconnect(v)
                self.lowlink[u] = min(self.lowlink[u], self.lowlink[v])
            elif self.on_stack[v]:
                self.lowlink[u] = min(self.lowlink[u], self.indices[v])

        if self.lowlink[u] == self.indices[u]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack[w] = False
                scc.append(w)
                if w == u:
                    break
            self.sccs.append(scc)

class DocumentationGraph:
    """
    Builds and analyzes a formal directed graph of documentation linkages,
    performing reachability sweeps, orphan island identification, and cycle detection.
    """
    def __init__(self):
        self.adj: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adj: Dict[str, Set[str]] = defaultdict(set)
        self.all_nodes: Set[str] = set()

    def add_edge(self, src: str, dst: str):
        self.all_nodes.add(src)
        self.all_nodes.add(dst)
        self.adj[src].add(dst)
        self.reverse_adj[dst].add(src)

    def find_cycles(self) -> List[List[str]]:
        tarjan = TarjanSCC(self.adj)
        return tarjan.compute_scc()

    def find_orphans(self, entrypoints: List[str]) -> List[str]:
        """Detects unreachable documentation nodes from standard root entrypoints."""
        reachable: Set[str] = set()
        queue = [ep for ep in entrypoints if ep in self.all_nodes]
        for ep in queue:
            reachable.add(ep)

        while queue:
            curr = queue.pop(0)
            for neighbor in self.adj.get(curr, set()):
                if neighbor not in reachable:
                    reachable.add(neighbor)
                    queue.append(neighbor)

        orphans = [node for node in self.all_nodes if node not in reachable]
        return sorted(orphans)
