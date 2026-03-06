import time

class ConceptNode:
    def __init__(self, node_id, node_type, depth,
                 subject, predicate, obj,
                 description, poignancy, keywords):
        self.node_id = node_id
        self.type = node_type  # "event" | "thought"
        self.depth = depth
        self.subject = subject
        self.predicate = predicate
        self.object = obj
        self.description = description
        self.poignancy = poignancy
        self.keywords = keywords
        self.created = time.time()
        self.last_accessed = self.created

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "type": self.type,
            "depth": self.depth,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "description": self.description,
            "poignancy": self.poignancy,
            "keywords": self.keywords,
            "created": self.created,
            "last_accessed": self.last_accessed
        }

    @staticmethod
    def from_dict(data):
        node = ConceptNode(
            node_id=data["node_id"],
            node_type=data["type"],
            depth=data["depth"],
            subject=data["subject"],
            predicate=data["predicate"],
            obj=data["object"],
            description=data["description"],
            poignancy=data["poignancy"],
            keywords=data["keywords"]
        )
        node.created = data["created"]
        node.last_accessed = data["last_accessed"]
        return node

    def spo_summary(self):
        return f"{self.subject} {self.predicate} {self.object}"