from django.test import TestCase
from .models import Author, Book
from refsql import RefSQL
from django.db import models

# Create your tests here.
class TestRefSQL(TestCase):
    def test_basic(self):
        Author.objects.create(name='Anssi', height=180, weight=80)
        Author.objects.create(name='Matti', height=170, weight=70)
        qs = Author.objects.annotate(
            casewhen=RefSQL("case when {{name}} = %s then height else weight end", ('Anssi',),
                            output_field=models.IntegerField())
        ).order_by('name')
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0].name, 'Anssi')
        self.assertEqual(qs[1].name, 'Matti')
        self.assertEqual(qs[0].casewhen, 180)
        self.assertEqual(qs[1].casewhen, 70)

    def test_param_amount(self):
        with self.assertRaises(ValueError):
            Author.objects.annotate(
                casewhen=RefSQL("case when {{name}} = %s then height else weight end",
                                ('Anssi', 'Matti'))
            )
        with self.assertRaises(ValueError):
            Author.objects.annotate(
                casewhen=RefSQL("case when {{name}} = %s then %s else %s end",
                                ('Anssi', 'Matti'))
            )

    def test_foreign_key(self):
        a = Author.objects.create(name='Anssi', height=180, weight=80)
        m = Author.objects.create(name='Matti', height=170, weight=70)
        Book.objects.create(name='Book1', author=a)
        Book.objects.create(name='Book2', author=m)
        qs = Book.objects.annotate(
            height_divided=RefSQL('{{author__height}} / %s', (10,))
        ).values_list('height_divided', flat=True).order_by('height_divided')
        self.assertQuerysetEqual(
            qs, [17, 18], lambda x: x)

    def test_in(self):
        a = Author.objects.create(name='Anssi', height=180, weight=80)
        m = Author.objects.create(name='Matti', height=170, weight=80)
        qs = Author.objects.annotate(
            ref_height=RefSQL('{{height}}')
        ).filter(ref_height=180)
        self.assertQuerysetEqual(
            Author.objects.filter(pk__in=qs),
            [a], lambda x: x)
        self.assertQuerysetEqual(
            Author.objects.exclude(pk__in=qs),
            [m], lambda x: x)
