django-refsql
=============

Raw SQL and field lookups combined (for Django 1.8+)

This project allows one to write raw SQL annotations, where the annotations
can contain Django's lookup syntax. The lookups are placed inside {{ and }}
markers.

For example one could write `qs.annotate(authoragedivided=RefSQL('{{author__age}} / %s', (10,)))`.
The RefSQL implementation will know how to turn the `author__age` lookup to
joins and column reference, so that the actual SQL might look something like::

    SELECT ..., author.age / 10 as authoragedivided
      FROM book
      JOIN author on book.author_id = author.id

For examples, see testproject/testproject/tests.py
