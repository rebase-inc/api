from collections import defaultdict


class ModelIds(defaultdict):

    def __init__(self, identity_map_keys=None):
        super().__init__(list)
        if identity_map_keys:
            for model_ids in identity_map_keys:
                self[model_ids[0]].append(model_ids[1])

    def __reduce__(self):
        return (ModelIds, tuple(), None, None, iter(self.items()))

    def __and__(self, other):
        _intersection = ModelIds([])
        intersect_models = set(self.keys()) & set(other.keys())
        for model in intersect_models:
            _intersecting_ids = set(self[model]) & set(other[model])
            if _intersecting_ids:
                _intersection[model].extend(_intersecting_ids)
        return _intersection


