
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 100
explore_faction = 2.

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    tempState = state
    curr = node

    while not curr.untried_actions and not board.is_ended(tempState):

        #print("In while loop")
        scores = {}
        for key in curr.child_nodes:
            child = curr.child_nodes[key]
            #Checks whether the board is the current player
            # print("Identity:", identity, "Current player:",board.current_player(tempState))

            #Current state is enemies state
            if(board.current_player(tempState) == identity):
                scores[key] = ucb(child, curr, 0)

            else:
                scores[key] = ucb(child, curr, 1)


        if scores:
            selected = max(scores, key=scores.get)
        else:
            return curr


        #tempState = board.next_state(tempState, selected)
        curr = curr.child_nodes[selected]
   # print("Chosen Node:", curr)
    return curr



    # Hint: return leaf_node


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    #store and remove a random action from node that is giving birth
    if node.untried_actions:
        #print("Debugging untried actions:", len(node.untried_actions), node.untried_actions)
        pa = choice(node.untried_actions)
        node.untried_actions.remove(pa)



    #get the action list for your new child node
        al = board.legal_actions(board.next_state(state, pa))
        #print("expand_leaf", al)
        new_node = MCTSNode(node, pa, al)
        #print("new_node.untried_actions:", new_node.untried_actions)

    #update parent nodes child dict
        node.child_nodes[pa] = new_node
    
        return new_node
    else:
        return node
    # Hint: return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """

    #the current player
    player = board.current_player(state)
    while not board.is_ended(state):

        chosen = choice(board.legal_actions(state))
        state = board.next_state(state, chosen)

    value = board.win_values(state)

#Current player lost
    if value[player] == 0:
        return 0
    elif value[player] == 1:    #Current player won
        return 1
    else:
        return 2    #Tie

    # loser = board.current_player(state)
    # if player == loser:
    #     return 0
    # else:
    #     return 1



def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """


    curr = node
    #The current player won
    if won == 1:
        count = 1
    #If current player lost or a tie occur
    elif won == 0 or won == 2:
        count = 0


    while curr is not None:
        curr.visits += 1
        if count%2:
            curr.wins += 1  
        curr = curr.parent
        #Increment the count counter to rotate when to increment win as long as it's not a tie
        if won is not 2:
         count +=1


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))
    value = board.win_values(state)

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        #print("for loop ")
        chosenNode = traverse_nodes(node, board, sampled_game, identity_of_bot)
        if chosenNode.untried_actions:
            leaf = expand_leaf(chosenNode, board, state)
        #The state for the child node
       # print("Leaf Node", leaf.tree_to_string(), "Root node:", node.tree_to_string())
        tempState = board.next_state(state, leaf.parent_action)
        rolloutWinner = rollout(board, tempState)
        backpropagate(leaf, rolloutWinner)


    finalNode = chosenMove(root_node, board, sampled_game, identity_of_bot)


    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.

    return finalNode.parent_action

def ucb(child, current, identity):
        w = child.wins
        n = child.visits
        t = current.visits

        exploit_val = w / n
        explore_val = (explore_faction * (2*log(t) / n))
        if identity:
            val = exploit_val + explore_val
        else:
            val = 1 - exploit_val + explore_val
        return val


# Return the correct node
def chosenMove(node, board, state, identity):
    curr = node
    tempState = state
    scores = {}
    for key in curr.child_nodes:
        child = curr.child_nodes[key]
        # Checks whether the board is the current player
        # print("Identity:", identity, "Current player:",board.current_player(tempState))
        if (board.current_player(tempState) == identity):
            scores[key] = ucb(child, curr, 0)
        else:
            scores[key] = ucb(child, curr, 1)

    selected = max(scores, key=scores.get)
    curr = curr.child_nodes[selected]
    # print("Chosen Node:", curr)
    return curr

