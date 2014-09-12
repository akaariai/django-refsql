import re
from django.db import models
from django.utils.functional import cached_property

class RefSQL(models.ExpressionNode):
    EXTEND_PARAMS_MARKER = object()

    def __init__(self, sql, params=(), output_field=None):
        super(RefSQL, self).__init__(output_field=output_field)
        self.sql = sql
        self.params = params
        self.sources = []
        self.param_groups = []
        self.lookups = []
        param_amount = len(params)
        params = list(reversed(params))
        results = re.findall('(%s)|({{\s*[\w_]+\s*}})', self.sql)
        for result in results:
            if result[0]:
                if not params:
                    raise ValueError("Not enough parameters (%s) for SQL: %s" %
                                     (param_amount, self.sql))
                self.param_groups.append(params.pop())
            else:
                self.param_groups.append(self.EXTEND_PARAMS_MARKER)
                self.lookups.append(result[1][2:-2].strip())
        if params:
            raise ValueError("Too many parameters (%s) for SQL: %s" %
                             (param_amount, self.sql))
        self.sql = re.sub('%s', '%%s', self.sql)
        self.sql = re.sub('{{\s*[\w_]+\s*}}', '%s', self.sql)
        self._used_joins = []

    def get_source_expressions(self):
        return self.sources

    def set_source_expressions(self, sources):
        self.sources = sources

    def as_sql(self, qn, connection):
        sql_parts = []
        params = []
        cols = list(reversed(self.sources))
        for param in self.param_groups:
            if param is self.EXTEND_PARAMS_MARKER:
                sql, sql_params = cols.pop().as_sql(qn, connection)
                params.extend(sql_params)
                sql_parts.append(sql)
            else:
                params.append(param)
        return self.sql % tuple(sql_parts), params

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False):
        c = self.copy()
        c.is_summary = summarize
        for lookup in c.lookups:
            self.sources.append(query.resolve_ref(lookup, allow_joins, reuse, summarize))
        return c

    @cached_property
    def output_field(self):
        if self._output_field:
            return self._output_field
        return self.sources[0].output_field
