from agent.memory.concept_node import ConceptNode

class AssociativeMemory:
    def __init__(self):
        self.nodes = []
        self.node_count = 0

    def _next_id(self):
        self.node_count += 1
        return f"node_{self.node_count}"

    def add_event(self, subject, predicate, obj, description, poignancy, keywords):
        node = ConceptNode(
            node_id=self._next_id(),
            node_type="event",
            depth=0,
            subject=subject,
            predicate=predicate,
            obj=obj,
            description=description,
            poignancy=poignancy,
            keywords=keywords
        )
        self.nodes.append(node)
        return node

    def add_thought(self, subject, predicate, obj, description, poignancy, keywords, depth=1):
        node = ConceptNode(
            node_id=self._next_id(),
            node_type="thought",
            depth=depth,
            subject=subject,
            predicate=predicate,
            obj=obj,
            description=description,
            poignancy=poignancy,
            keywords=keywords
        )
        self.nodes.append(node)
        return node

    def get_relevant(self, keywords, node_type=None, limit=5):
        keywords_lower = [k.lower() for k in keywords]
        scored = []
        for node in self.nodes:
            if node_type and node.type != node_type:
                continue
            overlap = len(set(keywords_lower) & {k.lower() for k in node.keywords})
            if overlap > 0:
                score = overlap * node.poignancy
                scored.append((score, node))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in scored[:limit]]

    def get_recent(self, node_type=None, limit=5):
        filtered = [n for n in self.nodes if not node_type or n.type == node_type]
        return sorted(filtered, key=lambda n: n.created, reverse=True)[:limit]

    def get_semantic_context(self, limit=5):
        thoughts = [n for n in self.nodes if n.type == "thought"]
        thoughts.sort(key=lambda n: n.poignancy, reverse=True)
        if not thoughts:
            return "No conceptual knowledge yet."
        return "\n".join([f"- {n.description}" for n in thoughts[:limit]])

    def to_dict(self):
        return {
            "node_count": self.node_count,
            "nodes": [n.to_dict() for n in self.nodes]
        }

    @staticmethod
    def from_dict(data):
        am = AssociativeMemory()
        am.node_count = data.get("node_count", 0)
        for node_data in data.get("nodes", []):
            am.nodes.append(ConceptNode.from_dict(node_data))
        return am