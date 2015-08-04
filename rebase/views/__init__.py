from marshmallow import Schema, SchemaOpts

class NamespaceOpts(SchemaOpts):
    """Same as the default class Meta options, but adds "name" and
    "plural_name" options for namespacing.
    """

    def __init__(self, meta):
        SchemaOpts.__init__(self, meta)
        self.name = getattr(meta, 'name', None)
        self.plural_name = getattr(meta, 'plural_name', self.name)

class NamespacedSchema(Schema):
    OPTIONS_CLASS = NamespaceOpts

    def _postprocess(self, data, many, obj):
        """Execute any postprocessing steps, including adding a namespace to the final
        output.
        """
        data = Schema._postprocess(self, data, many, obj)
        if self.opts.name:   # Add namespace
            namespace = self.opts.name
            if self.many or many:
                namespace = self.opts.plural_name
            data = {namespace: data}
        return data
