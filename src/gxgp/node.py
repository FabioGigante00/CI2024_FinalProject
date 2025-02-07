#   *        Giovanni Squillero's GP Toolbox
#  / \       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2   +      A no-nonsense GP in pure Python
#    / \
#  10   11   Distributed under MIT License

import numbers
import random
import warnings
from typing import Callable
import numpy as np
import re

from .draw import draw
from .utils import arity

__all__ = ['Node']

from utils.operations_dict import function_set

class Node:
    _func: Callable
    _successors: tuple['Node']
    _arity: int
    _str: str
    _height: int
    _constant:bool

    def __init__(self, node=None, successors=None, *, name=None, height=None):
        if callable(node):
            # print(f"inside callable(node)")
            def _f(*_args, **_kwargs):
                return node(*_args)
            self._height=height
            self._func = _f
            if successors is None:
                successors = tuple([])
            else:
                self._successors = tuple(successors)
            self._arity = arity(node)
            assert self._arity is None or len(tuple(successors)) == self._arity, (
                "Panic: Incorrect number of children."
                + f" Expected {len(tuple(successors))} found {arity(node)}"
            )
            self._leaf = False
            assert all(isinstance(s, Node) for s in successors), "Panic: Successors must be `Node`"
            self._successors = tuple(successors)
            if name is not None:
                self._str = name
            elif node.__name__ == '<lambda>':
                self._str = 'λ'
            else:
                self._str = node.__name__
            self._constant = False
        elif isinstance(node, numbers.Number):
            # print(f"inside isinstance(node, numbers.Number)")
            self._func = eval(f'lambda **_kw: {node}')
            self._successors = tuple()
            self._arity = 0
            self._str = f'{node:g}'
            self._height=height
            self._constant = True
        elif isinstance(node, str):
            # print(f"inside isinstance(node, str)")
            self._func = eval(f'lambda *, {node}, **_kw: {node}')
            self._successors = tuple()
            self._arity = 0
            self._str = str(node)
            self._height=height
            self._constant = False
        else:
            assert False

    def __call__(self, **kwargs):
        #====# Debugging Fossils
        # print(f"successors are ", end="")
        # for c in self._successors:
        #     print(f"{c._str} ", end="")
        # print()
        # print(f"Calling node: {self._str} with kwargs: {kwargs}")
        # try:
        #     result = self._func(*[c(**kwargs) for c in self._successors], **kwargs)
        #     print(f"Result of node {self._str}: {result}")
        #     return result
        # except TypeError as e:
        #     print(f"Error in node {self._str}: {e}")
        #     raise
        #====# End of Debugging Fossils
        return self._func(*[c(**kwargs) for c in self._successors], **kwargs)

    def __str__(self):
        return self.long_name

    def __len__(self):
        return 1 + sum(len(c) for c in self._successors)

    @property
    def value(self):
        return self()

    @property
    def arity(self):
        return self._arity

    @property
    def successors(self):
        return list(self._successors)

    @successors.setter
    def successors(self, new_successors):
        assert len(new_successors) == len(self._successors)
        self._successors = tuple(new_successors)

    @property
    def is_leaf(self):
        # return self._successors is None or len(self._successors) == 0
        return self._arity == 0

    @property
    def short_name(self):
        return self._str

    @property
    def long_name(self):
        if self.is_leaf:
            return self.short_name
        else:
            return f'{self.short_name}(' + ', '.join(c.long_name for c in self._successors) + ')'

    @property
    def subtree(self):
        result = set()
        _get_subtree(result, self)
        return result

    def draw(self):
        """ 
        Draws the tree. Note that if the depth is too high, you may need to save the output figure and then zoom in using a photo viewer.
        """
        self.reeval_heights()

        try:
            print(f"Drawing tree with height {self._height}...")
            return draw(self, self._height)
        except Exception as msg:
            warnings.warn(f"Drawing not available ({msg})", UserWarning, 2)
            return None


    """ Additions by Leonardo, Fabio, Dragos """
    def get_random_node(self):
        nodes = list(self.subtree)
        return random.choice(nodes)

    def set_height(self, height):
        self._height = height

    def get_height(self):
        return self._height
    
    def set_func(self, func, name=None):
        def _f(*_args, **_kwargs):
                return func(*_args)
        if callable(func):
            self._func = _f
            self._arity = arity(func)
            if name is not None:
                self._str = name
            elif func.__name__ == '<lambda>':
                self._str = 'λ'
            else:
                self._str = func.__name__
        elif isinstance(func, numbers.Number):
            self._func = eval(f'lambda **_kw: {func}')
            self._arity = 0
            self._str = f'{func:g}'
        elif isinstance(func, str):
            self._func = eval(f'lambda *, {func}, **_kw: {func}')
            self._arity = 0
            self._str = str(func)
        else:
            assert False

    def replace_tree_shallow(self, tree):
        self._func = tree._func
        self._successors = tree._successors
        self._arity = tree._arity
        self._str = tree._str
        self._height = tree._height
        self._constant = tree._constant

    def get_leafs(self):
        leafs = []
        for node in self.subtree:
            if node.is_leaf:
                leafs.append(node)
        return leafs
    def clone(self):
        #recursive clone of the tree
        try:
            my_node = function_set[self._str]   # 1) if the node _str is in the function set then take the relative lambda
        except KeyError:
            try:
                my_node = float(self._str)      # 2) if the node _str is a number then take the number converted as float
            except ValueError:
                my_node = self._str             # 3) if the node _str is a string then keep it as string

        if self.is_leaf:
            return Node(my_node, name=self._str, height=self._height)
        else:
            return Node(my_node, [c.clone() for c in self._successors], name=self._str, height=self._height)
        
    def reeval_heights(self):
        def _reeval_heights(node):
            if node.is_leaf:
                node._height = 0
            else:
                for child in node._successors:
                    _reeval_heights(child)
                node._height = 1 + max(child._height for child in node._successors)

        _reeval_heights(self) 

    def tree_distance(self, other):
        def _tree_distance(node1, node2):
            if node1.is_leaf:
                return node2.__len__() + 1 if node1._str != node2._str else 0
            if node2.is_leaf:
                return node1.__len__() + 1
            if node1._str != node2._str:
                # return number of descendants of the two nodes
                return node1.__len__() + node2.__len__() + 1
            return sum(_tree_distance(c1, c2) for c1, c2 in zip(node1._successors, node2._successors))

        return _tree_distance(self, other)
    
    def collapse_constants(self):
        # This function needs to explore the tree and replace
        # subtrees that have only constants as leafs with a single node
        # that contains the result of the evaluation of the subtree
        # with the constants as arguments
        def _collapse_constants(node):
            if node.is_leaf:
                return node
            if all(c._constant for c in node.get_leafs()):
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("error", RuntimeWarning)
                        result = node._func(*[c() for c in node._successors])
                        if np.isfinite(result):
                            return Node(result, name=node._str, height=node._height)
                        else:
                            return node
                except (OverflowError, RuntimeWarning) as e:
                    print(f"Error in node {node._str}: {e}")
                    return node
                
            return Node(node._func, [_collapse_constants(c) for c in node._successors], name=node._str, height=node._height)
        return _collapse_constants(self)
    
    def parse_formula(self, formula: str):
        """
        Parses a formula string and recreates a tree using the Node class.

        Parameters
        ----------
        formula : str
            The formula string to parse.

        Returns
        -------
        Node
            The root node of the recreated tree.
        """
        # Remove whitespace
        formula = formula.replace(" ", "")

        # Define a regex pattern to match function calls and their arguments
        pattern = re.compile(r'(\w+)\((.*)\)')

        def parse_subtree(subformula: str):
            match = pattern.match(subformula)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                args = split_args(args_str)
                children = [parse_subtree(arg) for arg in args]
                return Node(function_set[func_name], successors=children, name=func_name)
            else:
                # Handle terminal nodes (variables and constants)
                try:
                    return Node(float(subformula))
                except ValueError:
                    return Node(subformula)

        def split_args(args_str: str) -> list:
            """
            Splits the arguments string into individual arguments, handling nested parentheses.
            """
            args = []
            depth = 0
            current_arg = []
            for char in args_str:
                if char == ',' and depth == 0:
                    args.append(''.join(current_arg)) # Merge the characters found so far into a string, then reset (in the line below)
                    current_arg = []
                else:
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                    current_arg.append(char)
            args.append(''.join(current_arg))
            return args

        return parse_subtree(formula)


def _get_subtree(bunch: set, node: Node):
    bunch.add(node)
    for c in node._successors:
        _get_subtree(bunch, c)

