import functools
import json


class AudioSetOntology:
    def __init__(self, path):
        with open(path, 'r') as f:
            ontology = json.load(f)

        # Create a dictionary of OntologyNodes where the keys are IDs
        self.nodes = {node['id']: OntologyNode(node) for node in ontology}
        for node in self.nodes.values():
            _visit_ontology(self.nodes, node)

        # Create a dictionary where keys are labels
        self.nodes_by_name = {node.name: node for node in self.nodes.values()}

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError('`key` must be a string (label or ID)')

        if key[0] == '/':
            return self.nodes[key]
        return self.nodes_by_name[key]

    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        return '\n'.join([str(node.lineage[0])
                          for node in self.nodes.values()])


class OntologyNode:
    def __init__(self, info):
        self.info = info
        self.level = 0
        self.parents = []
        self.children = []

        self._visiting = False
        self._visited = False

    @functools.cached_property
    def lineage(self):
        return OntologyLineage(self)

    def is_ancestor(self, node):
        if self.level < node.level:
            for parent in node.parents:
                if self is parent:
                    return True
                return self.is_ancestor(parent)
        return False

    def is_descendant(self, node):
        return node.is_ancestor(self)

    def __getitem__(self, key):
        return self.info[key]

    def __getattr__(self, attr):
        return self.info[attr]

    def __repr__(self):
        parent_ids = [node.id for node in self.parents]
        return (
            f'ID: {self.id}\n'
            f'Name: {self.name}\n'
            f'Level: {self.level}\n'
            f'Parent IDs: {parent_ids}\n'
            f'Child IDs: {self.child_ids}'
        )


class OntologyLine:
    def __init__(self, nodes):
        self.nodes = nodes

    def __getitem__(self, index):
        return self.nodes[index]

    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        return ' > '.join([node.name for node in self.nodes])


class OntologyLineage:
    def __init__(self, node):
        lineage = _lineage(node, [[node]])
        self.lineage = [OntologyLine(line) for line in lineage]

    def __getitem__(self, index):
        return self.lineage[index]

    def __len__(self):
        return len(self.lineage)

    def __repr__(self):
        return '\n'.join(map(str, self.lineage))


def _visit_ontology(nodes, current_node):
    if current_node._visiting:
        raise RuntimeError('`nodes` contains loop (must be simple graph)')

    # Calculate level/depth of node
    # Note that a node may have more than one parent
    if len(current_node.parents) > 0:
        levels = [node.level for node in current_node.parents]
        current_node.level = max(levels) + 1

    current_node._visiting = True

    # Visit ontology depth-first to set parent/child relationships
    for child_id in current_node.child_ids:
        child_node = nodes[child_id]
        if not current_node._visited:
            child_node.parents.append(current_node)
            current_node.children.append(child_node)

        _visit_ontology(nodes, child_node)

    current_node._visiting = False
    current_node._visited = True


def _lineage(node, branches):
    new_branches = []
    for parent in node.parents:
        for branch in branches:
            new_branches += _lineage(parent, [[parent] + branch])

    if len(new_branches) > 0:
        return new_branches
    return branches
