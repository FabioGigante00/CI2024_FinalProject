# """ This file contains the functions that are used to: generate, mutate, and combine the population """
# """ TODO: Populate this with the helper from the notebook when the notebook is ready """

# import random
# from typing import List
# from gxgp.node import Node
# from utils.operations_dict import basic_function_set, complex_function_set

# def generate_random_tree(max_height: int, pc: float, terminal_list: List[str],
#                          constants: list[float] = None, p_pick_constant: float = 0.2, p_cut_tree: float = 0.2) -> Node:
#     """
#     Generate a random symbolic expression tree.

#     Mandatory Parameters
#     ----------
#     max_height : int
#         The maximum height of the tree.
#     pc : float
#         The probability of choosing a complex function over a basic function.
#     terminal_list : List[str]
#         The terminal list to choose from. Example: ['x0', 'x1', 'x2']

#     Optional Parameters
#     ----------
#     constants : list[float]
#         A list of constants that can be used in the tree (default is None).
#     p_pick_constant : float
#         The probability of choosing a constant over a terminal (default is 0.2).
#     p_cut_tree : float
#         The probability of cutting the tree early (default is 0.2).        

#     Returns
#     -------
#     Node
#         A Node object representing the root of the tree.
#     """

#     # If height isn't 0, set is_root to True, so that we don't get 0-length trees unless specified
#     is_root = max_height != 0
#     #                                                                                                   > Flag to check if root, in order not to create 0-length trees
#     return generate_random_tree_R(max_height, pc, terminal_list, constants, p_pick_constant, p_cut_tree, is_root)

# def generate_random_tree_R(max_height: int, pc: float, terminal_list: List[str],
#                          constants: list[float] = None, p_pick_constant: float = 0.2, p_cut_tree: float = 0.2,
#                          is_root: bool = True) -> Node:
#     """
#     Wrapped function for generating a random symbolic expression tree.
#     """

#     # Cut the tree early with probability 0.2
#     if (not is_root and random.random() < p_cut_tree) or max_height == 0:  
#         # If constants are provided, choose one with probability p_pick_constant
#         if constants is not None and random.random() < p_pick_constant: 
#             terminal = random.choice(constants) 
#         # Otherwise, pick from the terminal set
#         else:                                                
#             terminal = random.choice(terminal_list)

#         # Set the height of the node to 0
#         my_node = Node(terminal)
#         my_node.set_height(0)
#         return my_node
#     else:
#         # Choose a complex function with probability pc
#         if random.random() < pc:                       
#             func = random.choice(list(complex_function_set.keys()))
#             num_children = complex_function_set[func].__code__.co_argcount  # Numero di argomenti della funzione
#             children = [generate_random_tree_R(max_height - 1, pc, terminal_list, constants, p_pick_constant, p_cut_tree, False)
#                         for _ in range(num_children)]
            
#             # Set height
#             cur_height = max([child.get_height() for child in children]) + 1
#             my_node = Node(complex_function_set[func], children, name=cur_height)
#             my_node.set_height(cur_height)
#             return my_node
#         # Otherwise, choose a basic function
#         else:                                           
#             func = random.choice(list(basic_function_set.keys()))
#             num_children = basic_function_set[func].__code__.co_argcount  # Numero di argomenti della funzione
#             children = [generate_random_tree_R(max_height - 1, pc, terminal_list, constants, p_pick_constant, p_cut_tree, False)
#                         for _ in range(num_children)]
#             # Set height
#             cur_height = max([child.get_height() for child in children]) + 1
#             my_node = Node(basic_function_set[func], children, name=cur_height)
#             my_node.set_height(cur_height)
#             return my_node
        
# def point_mutation(Tree: Node, terminal_list: List[str], constants: list[float] = None, p_pick_constant: float = 0.2, pc: float = 0.2) -> Node:
#     """
#     Mutate a tree by changing a random node to a new random node.

#     Parameters
#     ----------
#     Tree : Node
#         The tree to mutate.
#     terminal_list : List[str]
#         The terminal list to choose from. Example: ['x0', 'x1', 'x2']
#     constants : list[float]
#         A list of constants that can be used in the tree.
#     p_pick_constant : float
#         The probability of choosing a constant over a terminal.
#     pc : float
#         The probability of choosing a complex function over a basic function.

#     Returns
#     -------
#     Node
#         The mutated tree.
#     """

#     # Get the list of nodes in the tree
#     node = Tree.get_random_node()

#     # If the node is a terminal, change it to a new terminal
#     if node.is_leaf:
#         if constants is not None and random.random() < p_pick_constant:
#             terminal = random.choice(constants)
#         else:
#             terminal = random.choice(terminal_list)
#         node.set_func(terminal)
#         return Tree
#     # Otherwise, change it to a new function maintaining the arity
#     else:
#         if random.random() < pc:
#             while True:
#                 func = random.choice(list(complex_function_set.keys()))
#                 arity = complex_function_set[func].__code__.co_argcount
#                 if arity == node._arity:
#                     break
#             node.set_func(complex_function_set[func], name=func)
#         else:
#             while True:
#                 func = random.choice(list(basic_function_set.keys()))
#                 arity = basic_function_set[func].__code__.co_argcount
#                 if arity == node._arity:
#                     break
#             node.set_func(basic_function_set[func], name=func)
#         return Tree
    
# def subtree_mutation(Tree: Node, terminal_list: List[str], constants: list[float] = None, p_pick_constant: float = 0.2, pc: float = 0.2, height: int = 3, verbose: bool = False) -> Node:
#     """
#     Mutate a tree by changing a random subtree to a new random subtree.

#     Parameters
#     ----------
#     Tree : Node
#         The tree to mutate.
#     terminal_list : List[str]
#         The terminal list to choose from. Example: ['x0', 'x1', 'x2']
#     constants : list[float]
#         A list of constants that can be used in the tree.
#     p_pick_constant : float
#         The probability of choosing a constant over a terminal.
#     pc : float
#         The probability of choosing a complex function over a basic function.
#     height : int
#         The maximum height of the new subtree.

#     Returns
#     -------
#     Node
#         The mutated tree.
#     """

#     # Get the list of nodes in the tree
#     node = Tree.get_random_node()

#     if verbose:
#         print(f"Node to mutate: {node._str} at height {node._height}")

#     # # If the node is a terminal, change it to a new terminal
#     # new_subtree = generate_random_tree(height, pc, terminal_list, constants, p_pick_constant)  <-- not good cause gentree doesn't work with height = 0
#     new_subtree = Node()

#     #select from the tuple of the successor a node randomly
#     successors = list(node._successors)
#     if len(successors) != 0:
#         index = random.randint(0, len(successors) - 1)
#     else:
#         index = 0

#     if verbose:
#         print(f"Old subtree: {successors[index]._str}")
#     successors[index] = new_subtree

#     node._successors = tuple(successors)
#     return Tree

