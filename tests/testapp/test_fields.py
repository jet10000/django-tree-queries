from types import SimpleNamespace

from django.test import TestCase

from .models import Model


class Test(TestCase):
    def create_tree(self):
        tree = SimpleNamespace()
        tree.root = Model.objects.create()
        tree.child1 = Model.objects.create(parent=tree.root, position=0)
        tree.child2 = Model.objects.create(parent=tree.root, position=1)
        tree.child1_1 = Model.objects.create(parent=tree.child1, position=0)
        tree.child2_1 = Model.objects.create(parent=tree.child2, position=0)
        tree.child2_2 = Model.objects.create(parent=tree.child2, position=1)
        return tree

    def test_stuff(self):
        Model.objects.create()

        self.assertEqual(len(Model.objects.with_tree_fields()), 1)

        instance = Model.objects.with_tree_fields().get()
        self.assertEqual(instance.tree_depth, 0)
        self.assertEqual(instance.tree_path, [instance.pk])

    def test_no_attributes(self):
        tree = self.create_tree()

        root = Model.objects.get(pk=tree.root.pk)
        self.assertFalse(hasattr(root, "tree_depth"))
        self.assertFalse(hasattr(root, "tree_ordering"))
        self.assertFalse(hasattr(root, "tree_path"))
        self.assertFalse(hasattr(root, "tree_pk"))

    def test_attributes_and_ancestors(self):
        tree = self.create_tree()
        child2_2 = Model.objects.with_tree_fields().get(pk=tree.child2_2.pk)
        self.assertEqual(child2_2.tree_depth, 2)
        self.assertEqual(child2_2.tree_ordering, [0, 1, 1])
        self.assertEqual(
            child2_2.tree_path, [tree.root.pk, tree.child2.pk, tree.child2_2.pk]
        )

        self.assertEqual(list(child2_2.ancestors()), [tree.root, tree.child2])
        self.assertEqual(
            list(child2_2.ancestors(include_self=True)),
            [tree.root, tree.child2, tree.child2_2],
        )

    def test_descendants(self):
        tree = self.create_tree()
        self.assertEqual(
            list(tree.child2.descendants()), [tree.child2_1, tree.child2_2]
        )
        self.assertEqual(
            list(tree.child2.descendants(include_self=True)),
            [tree.child2, tree.child2_1, tree.child2_2],
        )
