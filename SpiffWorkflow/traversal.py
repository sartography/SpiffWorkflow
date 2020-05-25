import copy

def same_ending_length(node):
    """
    return the length of the endings of each child that match each other
    """
    # go get a modified list of just the ids in each child.
    endings = [[leaf['id'] for leaf in branch['children']] for branch in node]
    # the longest identical ending will be equal to the lenght of the
    # shortest list
    shortest_list = min([len(x) for x in endings])
    # walk through the list and determine if they are all the same
    # for each. If they are not the same, then we back off the snip point
    snip_point = shortest_list
    for x in reversed(range(shortest_list)):
        current_pos = -(x+1)
        end_ids = [el[current_pos] for el in endings]
        if not len(set(end_ids)) <= 1:
            snip_point = snip_point - 1
    return snip_point

def snip_same_ending(node,length):
    """
    shorten each child task list to be only it's unique children,
    return a list of the same endings so we can tack it on the
    parent tree.
    """
    retlist = node[0]['children'][-length:]
    for branch in node:
        branch['children'] = branch['children'][:-length]
    return retlist

def flatten(list,output=[],level=0):
    """
    Traverse the tree and return a list
    """
    for x in list:
        x['indent'] = level
        x['child_count'] = len(x['children'])
        output.append(x)
        if len(x['children']) >0:
            flatten(x['children'],output,level+1)
        del x['children']
    return output



def conditional_task_add(task,output,found,level):
    if task.description is not None and \
            task.description != '' and \
            task.id not in [x['id'] for x in output]:
        output.append({'id': task.id,
                       'name': task.name,
                       'description': task.description,
                       'backtracks': None,
                       'lane': task.lane,
                       'children': [],
                       'level': level})



def follow_tree(tree,output=[],found=set(),level=0):
    from SpiffWorkflow.bpmn.specs.UnstructuredJoin import UnstructuredJoin
    from SpiffWorkflow.bpmn.specs.MultiInstanceTask import MultiInstanceTask


    # I had an issue with a test being nondeterministic the yes/no
    # were in an alternate order in some cases. To be 100% correct, this should
    # probably also use the X/Y information that we are parsing elsewhere, but
    # I did not see that information in the task spec.
    # At a bare minimum, this should fix the problem where keys in a dict are
    # flip-flopping.
    # After I'm done, you should be able to manage the order of the sequence flows by
    # naming the Flow_xxxxx names in the order you want them to appear.

    outputs = list(tree.outgoing_sequence_flows.keys())
    idlinks = [(x,tree.outgoing_sequence_flows[x]) for x in outputs]
    idlinks.sort(key=lambda x: x[1].id)
    outputs = [x[0] for x in idlinks]

    # ---------------------
    # Endpoint, no children
    # ---------------------
    if len(outputs)==0:
        # This has no children, so we append it and terminate the recursion
        conditional_task_add(tree, output, found, level)
        found.add(tree.id)
        return output

    if isinstance(tree,MultiInstanceTask) and\
            not tree.isSequential:
        # NB: Not technically correct but expedient
        for task in tree.inputs[1].outputs:
            linkkey = list(task.outgoing_sequence_flows.keys())[0]
            link = task.outgoing_sequence_flows[linkkey]

            conditional_task_add(task,output,found,level)
            if task.id not in found:
                found.add(task.id)
                output = follow_tree(link.target_task_spec, output, found, level + 1)

        return output

    #------------------
    # Simple case - no branching
    # -----------------

    if len(outputs) == 1:
        # there are no branching points here, so our job is simple
        # add to the tree and descend into the tree some more
        link = tree.outgoing_sequence_flows[outputs[0]]
        conditional_task_add(tree,output,found,level)
        if tree.id not in found:
            found.add(tree.id)
            output = follow_tree(link.target_task_spec, output, found, level+1)
        return output
    # --------------------
    # I need to check and see if we are really using this section
    # It should get here in the case of a normal parallel gateway,
    # but not for a MI
    # --------------------

    if isinstance(tree,UnstructuredJoin):
        # here we have a parallel gateway, so we want to
        # add myself to the tree - subsequent calls will
        # not add if it is already in the list

        for key in outputs:
            link = tree.outgoing_sequence_flows[key]

            # consider to check and see if this one is already
            # in the list - we may have a problem if we are nesting
            # parallel gateways.
            conditional_task_add(tree,output,found,level)
            if tree.id not in found:
                found.add(tree.id)
            # For parallel tasks, Check all the children, not just the first one.
            output = follow_tree(link.target_task_spec, output, found, level + 1)

        return output
    # if we are here, then we assume that we have a decision point and process
    # accordingly - this may be incorrect and we may want to add some other
    # cases -
    taskchildren = []
    for key in outputs:
        link = tree.outgoing_sequence_flows[key]
        if link.name is not None:
            mychildren = []
            if link.target_task_spec.id not in found:
                f = copy.copy(found)
                mychildren = follow_tree(link.target_task_spec, mychildren, f, level + 2)
                backtracklink = None
            else:
                backtracklink = (link.target_task_spec.id,link.target_task_spec.description)
            mychildren.sort(key=lambda x: x['level'])
            taskchildren.append({'id':link.id,
                                 'name':link.name,
                                 'description':link.name,
                                 'is_decision': True,
                                 'lane': tree.lane,
                                 'backtracks':backtracklink,
                                 'children':mychildren,
                                 'level':level+1})
        # we know we have several decision points which may merge in the future. The lists
        # should be identical except for the levels.
        # essentially, we want to find the list of ID's that are in each of the taskchildren's children
        # and remove that from each list.
        # in addition, this should be the same length on each end because of the sort above.
    # now that we have our children lists, we can remove the intersection of the group
    if tree.id not in  [x['id'] for x in output]:
        snip_lists = same_ending_length(taskchildren)
        merge_list = snip_same_ending(taskchildren, snip_lists)
        output.append({'id':tree.id,
                       'name':tree.name,
                       'description':tree.description,
                       'backtracks':None,
                       'is_decision':False,
                       'lane': tree.lane,
                       'children':taskchildren,
                       'level':level+1})
        output =  output + merge_list
    found.add(tree.id)
    return output










