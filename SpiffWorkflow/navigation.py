import copy

from .task import Task
from .bpmn.specs.BpmnSpecMixin import BpmnSpecMixin, SequenceFlow
from .bpmn.specs.UnstructuredJoin import UnstructuredJoin
from .bpmn.specs.MultiInstanceTask import MultiInstanceTask
from .bpmn.specs.CallActivity import CallActivity
from .bpmn.specs.BoundaryEvent import _BoundaryEventParent


class NavItem(object):
    """
        A waypoint in a workflow along with some key metrics
        - Each list item has :
           spec_id          -   TaskSpec or Sequence flow id
           name             -   The name of the task spec (or sequence)
           spec_type        -   The type of task spec (it's class name)
           task_id          -   The uuid of the actual task instance, if it exists
           description      -   Text description
           backtracks       -   Boolean, if this backtracks back up the list or not
           indent           -   A hint for indentation
           lane             -   This is the lane for the task if indicated.
           state            -   State of the task
    """

    def __init__(self, spec_id, name, spec_type, description,
                 lane=None, backtracks=None, indent=0):
        self.spec_id = spec_id
        self.name = name
        self.spec_type = spec_type
        self.description = description
        self.lane = lane
        self.backtracks = backtracks
        self.indent = indent
        self.task_id = None
        self.state = None

    @classmethod
    def from_spec(cls, spec: BpmnSpecMixin, task:Task=None, backtracks=None, indent=None):
        instance = cls(
            spec_id=spec.id,
            name=spec.name,
            spec_type=spec.__class__.__name__,
            description=spec.description,
            lane=spec.lane,
            backtracks=backtracks,
            indent=indent
        )
        if task:
            instance.task_id = task.id
            instance.state = task.state
        return instance


    @classmethod
    def from_flow(cls, flow: SequenceFlow, lane, backtracks, indent):
        """We include flows in the navigation if we hit a conditional gateway,
        as in do this if x, do this if y...."""
        return cls(
            spec_id=flow.id,
            name=flow.name,
            spec_type=flow.__class__.__name__,
            description=flow.name,
            lane=lane,
            backtracks=backtracks,
            indent=indent
        )

    def __str__(self):
        text = self.description
        if self.spec_type == "StartEvent":
            text = "O"
        elif self.spec_type == "TaskEndEvent":
            text = "@"
        elif self.spec_type == "ExclusiveGateway":
            text = f"X {text} X"
        elif self.spec_type == "ParallelGateway":
            text = f"+ {text}"
        elif self.spec_type == "SequenceFlow":
            text = f"-> {text}"
            if self.backtracks:
                text += f"  (BACKTRACK to {self.backtracks}"
        elif self.spec_type[-4:] == "Task":
            text = f"[{text}] STATE: {self.state}  TASK ID: {self.task_id}"
        else:
            text = f"({self.spec_type}) {text}"

        result = f' {"..," * self.indent }{text}'
        if self.lane:
            result = f'|{self.lane}| {result}'
        return result

class NavWithChildren(object):
    def __init__(self, nav:NavItem, children):
        self.nav_item = nav
        self.children = children


def get_nav_list(workflow):
    # traverse the tree, getting a complete navigation, but without
    # task states.
    nav_items = []
    for top in workflow.task_tree.children[0].task_spec.outputs:
        nav_items.extend(follow_tree(top, output=[],
                                      found=set(), workflow=workflow))
    task_list = workflow.get_tasks()

    # Remove any ignorable navigation items, these are classes that begin
    # with an _
    nav_items = list(filter(lambda ni: not(ni.spec_type.startswith("_")), nav_items))


    # look up task status for each item in the list
    for nav_item in nav_items:
        # get a list of statuses for the current task_spec
        # we may have more than one task for each
        tasks = [x for x in task_list if
                 (x.task_spec.id == nav_item.spec_id) and (
                     x.task_spec.name == nav_item.name)]
        if len(tasks) == 0:
            nav_item.state = None
            nav_item.task_id = None
        else:
            # Something has caused us to loop back around in some way to
            # this task spec again, and so there are multiple states for
            # this navigation item. Opt for returning the first ready task,
            # if available, then fall back to the last completed task.
            ready_task = next((t for t in tasks
                               if t.state == Task.READY), None)
            comp_task = next((t for t in reversed(tasks)
                              if t.state == Task.COMPLETED), None)
            if len(tasks) == 1:
                task = tasks[0]
            elif ready_task:
                task = ready_task
            elif comp_task:
                task = comp_task
            else:
                task = tasks[0]  # Not sure what else to do here yet.
            nav_item.state = task.state_names[task.state]
            nav_item.task_id = task.id

    return nav_items


def same_ending_length(nav_with_children):
    """
    return the length of the endings of each child that match each other
    """
    # go get a modified list of just the ids in each child.
    endings = [[leaf.spec_id for leaf in branch.children] for branch in nav_with_children]
    # the longest identical ending will be equal to the lenght of the
    # shortest list
    if len(endings) == 0:
        shortest_list = 0
    else:
        shortest_list = min([len(x) for x in endings])
    # walk through the list and determine if they are all the same
    # for each. If they are not the same, then we back off the snip point
    snip_point = shortest_list
    for x in reversed(range(shortest_list)):
        current_pos = -(x + 1)
        end_ids = [el[current_pos] for el in endings]
        if not len(set(end_ids)) <= 1:
            snip_point = snip_point - 1
    return snip_point


def snip_same_ending(nav_with_children, length):
    """
    shorten each child task list to be only it's unique children,
    return a list of the same endings so we can tack it on the
    parent tree.
    """
    if len(nav_with_children) == 0 or length == 0:
        return []
    retlist = nav_with_children[0].children[-length:]
    for branch in nav_with_children:
        branch.children = branch.children[:-length]
    return retlist


def conditional_task_add(output, task_spec, task, backtracks, indent):
    if task_spec.id not in [x.spec_id for x in output]:
        output.append(NavItem.from_spec(spec=task_spec, task=task,
                              backtracks=backtracks, indent=indent))


def follow_tree(tree, output=[], found=set(), level=0, workflow=None):
    """RECURSIVE - follows the tree returning a list of NavItem objects"""

    # I had an issue with a test being nondeterministic the yes/no
    # were in an alternate order in some cases. To be 100% correct, this should
    # probably also use the X/Y information that we are parsing elsewhere, but
    # I did not see that information in the task spec.
    # At a bare minimum, this should fix the problem where keys in a dict are
    # flip-flopping.
    # After I'm done, you should be able to manage the order of the sequence flows by
    # naming the Flow_xxxxx names in the order you want them to appear.

    outputs = list(tree.outgoing_sequence_flows.keys())
    idlinks = [(x, tree.outgoing_sequence_flows[x]) for x in outputs]
    idlinks.sort(key=lambda x: x[1].target_task_spec.position['y'])
    outputs = [x[0] for x in idlinks]

    # ---------------------
    # Endpoint, no children
    # ---------------------
    if len(outputs) == 0:
        # This has no children, so we append it and terminate the recursion
        conditional_task_add(output, tree,
                             task=None, backtracks=False, indent=level)
        found.add(tree.id)
        return output

    # ---------------------
    # Call Activity - follow subtree
    # ---------------------
    if isinstance(tree, CallActivity):
        tsk = workflow.get_tasks_from_spec_name(tree.name)[0]
        x = tree.create_sub_workflow(tsk)
        sublist_outputs = [
            follow_tree(top, output=[], found=set(), level=level, workflow=x)
            for top in x.task_tree.children[0].task_spec.outputs]
        for lst in sublist_outputs:
            for item in lst:
                item.indent = level + 1
                output.append(item)
        for key in tree.outgoing_sequence_flows.keys():
            link = tree.outgoing_sequence_flows[key]
            output = follow_tree(link.target_task_spec, output, found,
                                 level, workflow)
        return output

    if isinstance(tree, MultiInstanceTask) and not tree.isSequential:
        # When we have expanded the tree, we'll have multiple tasks, and
        # need this special case.  If the tree has not yet been expanded
        # it should just run through logic lower on in this function,
        if len(tree.inputs) > 1:
            # we have expanded the tree:
            outputs = tree.inputs[1].outputs
            for task_spec in outputs:
                last_spec = task_spec
                linkkey = list(task_spec.outgoing_sequence_flows.keys())[0]
                link = task_spec.outgoing_sequence_flows[linkkey]
                conditional_task_add(output, task_spec,
                                     task=None, backtracks=False, indent=level)
                if task_spec.id not in found:
                    found.add(task_spec.id)

            if last_spec:
                output = follow_tree(link.target_task_spec, output, found,
                                     level, workflow)
                return output
        else:
            # Don't treat this like a multi-instance yet, and continue.
            pass


    # ------------------
    # Simple case - no branching
    # -----------------

    if len(outputs) == 1:
        # there are no branching points here, so our job is simple
        # add to the tree and descend into the tree some more
        link = tree.outgoing_sequence_flows[outputs[0]]
        conditional_task_add(output, tree,
                             task=None, backtracks=False, indent=level)
        if tree.id not in found:
            found.add(tree.id)
            output = follow_tree(link.target_task_spec, output, found,
                                 level, workflow)
        return output

    if isinstance(tree, _BoundaryEventParent):
        for task in outputs:
            link = tree.outgoing_sequence_flows[task]
            conditional_task_add(output, tree,
                                 task=None, backtracks=False, indent=level)
            if link.target_task_spec.id not in found:
                found.add(link.target_task_spec.id)
                output = follow_tree(link.target_task_spec, output, found,
                                     level + 1, workflow)
        return output

    # if we are here, then we assume that we have a gateway of some form,
    # where more than one path will exist, we need to follow multiple paths
    # and then sync those paths and realign.
    task_children = []
    structured = not(isinstance(tree, UnstructuredJoin))
    for key in outputs:
        f = copy.copy(found)
        flow = tree.outgoing_sequence_flows[key]
        my_children = []
        level_increment = 1
        if structured: level_increment = 2
        if flow.target_task_spec.id not in found:
            my_children = follow_tree(flow.target_task_spec, my_children, f,
                                      level + level_increment, workflow)
            backtrack_link = None
        else:
            my_children = [] # This is backtracking, no need to follow it.
            backtrack_link = flow.target_task_spec.name

        # Note that we append the NavWithChildren here, not just nav
        task_children.append(NavWithChildren(NavItem.from_flow(flow=flow, lane=tree.lane,
                             backtracks=backtrack_link, indent=level+1),
                             my_children))

    """ we know we have several decision points which may merge in the future.
        The lists should be identical except for the levels.
        essentially, we want to find the list of ID's that are in each of the
        task_children's children and remove that from each list.
        in addition, this should be the same length on each end because
        of the sort above. now that we have our children lists, we can remove
        the intersection of the group """
    if tree.id not in [x.spec_id for x in output]:
        snip_lists = same_ending_length(task_children)
        merge_list = snip_same_ending(task_children, snip_lists)
        output.append(NavItem.from_spec(spec=tree, task=None,
                                        backtracks=None, indent=level))
        for child in task_children:
            # Add the flow nav item, but only if this is an exclsive gateway,
            # and not an instructured join
            if structured:
                output.append(child.nav_item)
            for descendent in child.children:
                output.append(descendent)

        if len(merge_list) > 0:
            # This bit gets the indentation right, we are merging back out
            # to the current level, so the first child here should be moved
            # out to current level, and any subsequent children should be
            # reduced by that same difference.
            indent_correction = merge_list[0].indent - level
            for child in merge_list:
                child.indent -= indent_correction
                output.append(child)

    found.add(tree.id)
    return output
