import copy

from . import WorkflowException
from .bpmn.specs.events import StartEvent, EndEvent, IntermediateCatchEvent, IntermediateThrowEvent, BoundaryEvent, _BoundaryEventParent
from .bpmn.specs.ExclusiveGateway import ExclusiveGateway
from .bpmn.specs.ManualTask import ManualTask
from .bpmn.specs.NoneTask import NoneTask
from .bpmn.specs.ParallelGateway import ParallelGateway
from .bpmn.specs.ScriptTask import ScriptTask
from .bpmn.specs.UserTask import UserTask
from .dmn.specs.BusinessRuleTask import BusinessRuleTask
from .specs import CancelTask, StartTask
from .task import Task
from .bpmn.specs.BpmnSpecMixin import BpmnSpecMixin, SequenceFlow
from .bpmn.specs.UnstructuredJoin import UnstructuredJoin
from .bpmn.specs.MultiInstanceTask import MultiInstanceTask
from .bpmn.specs.SubWorkflowTask import SubWorkflowTask, CallActivity, TransactionSubprocess


class NavItem(object):
    """
        A waypoint in a workflow along with some key metrics
        - Each list item has :
           spec_id          -   TaskSpec or Sequence flow id
           name             -   The name of the task spec (or sequence)
           spec_type        -   The type of task spec (it's class name)
           task_id          -   The uuid of the actual task instance, if it exists
           description      -   Text description
           backtrack_to     -   The spec_id of the task this will back track to.
           indent           -   A hint for indentation
           lane             -   This is the lane for the task if indicated.
           state            -   State of the task
    """

    def __init__(self, spec_id, name, description,
                 lane=None, backtrack_to=None, indent=0):
        self.spec_id = spec_id
        self.name = name
        self.spec_type = "None"
        self.description = description
        self.lane = lane
        self.backtrack_to = backtrack_to
        self.indent = indent
        self.task_id = None
        self.state = None
        self.children = []

    def set_spec_type(self, spec):
        types = [UserTask, ManualTask, BusinessRuleTask, CancelTask,
                 ScriptTask, StartTask, EndEvent, StartEvent,
                 MultiInstanceTask, StartEvent, SequenceFlow,
                 ExclusiveGateway, ParallelGateway, CallActivity, TransactionSubprocess,
                 UnstructuredJoin, NoneTask, BoundaryEvent, IntermediateThrowEvent,IntermediateCatchEvent]
        spec_type = None
        for t in types:
            if isinstance(spec, t):
                spec_type = t.__name__
                break
        if spec_type:
            self.spec_type = spec_type
        elif spec.__class__.__name__.startswith('_'):
            # These should be removed at some point in the process.
            self.spec_type = spec.__class__.__name__
        else:
            raise WorkflowException(spec, "Unknown spec: " +
                                    spec.__class__.__name__)

    @classmethod
    def from_spec(cls, spec: BpmnSpecMixin, backtrack_to=None, indent=None):
        instance = cls(
            spec_id=spec.id,
            name=spec.name,
            description=spec.description,
            lane=spec.lane,
            backtrack_to=backtrack_to,
            indent=indent
        )
        instance.set_spec_type(spec)
        return instance

    @classmethod
    def from_flow(cls, flow: SequenceFlow, lane, backtrack_to, indent):
        """We include flows in the navigation if we hit a conditional gateway,
        as in do this if x, do this if y...."""
        instance = cls(
            spec_id=flow.id,
            name=flow.name,
            description=flow.name,
            lane=lane,
            backtrack_to=backtrack_to,
            indent=indent
        )
        instance.set_spec_type(flow)
        return instance

    def __eq__(self, other):
        if isinstance(other, NavItem):
            return self.spec_id == other.spec_id and \
                   self.name == other.name and \
                   self.spec_type == other.spec_type and \
                   self.description == other.description and \
                   self.lane == other.lane and \
                   self.backtrack_to == other.backtrack_to and \
                   self.indent == other.indent
        return False

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
        elif self.spec_type[-4:] == "Task":
            text = f"[{text}] TASK ID: {self.task_id}"
        else:
            text = f"({self.spec_type}) {text}"

        result = f' {"..," * self.indent} STATE: {self.state} {text}'
        if self.lane:
            result = f'|{self.lane}| {result}'
        if self.backtrack_to:
            result += f"  (BACKTRACK to {self.backtrack_to}"

        return result

def get_deep_nav_list(workflow):
    # converts a flat nav into a hierarchical list, that is easier to render
    # in some cases. This assumes that we never jump more than one indent
    # forward at a time, which should always be the case, but that we might
    # un-indent any amount.
    nav_items = []
    flat_navs = get_flat_nav_list(workflow)
    parents = []
    for nav_item in flat_navs:
        if nav_item.indent == 0:
            nav_items.append(nav_item)
            parents = [nav_item]
        else:
            if len(parents) >= nav_item.indent:
                parents[nav_item.indent - 1].children.append(nav_item)
            else:
                parents[-1].children.append(nav_item)
            if len(parents) > nav_item.indent:
                parents = parents[:nav_item.indent] # Trim back to branch point.
            parents.append(nav_item)

    # With this navigation now deep, we can work back trough tasks, and set
    # states with a little more clarity
    set_deep_state(nav_items)

    return nav_items


def set_deep_state(nav_items):
    # recursive, in a deeply nested navigation, use the state of children to
    # inform the state of the parent, so we have some idea what is going on at
    # that deeper level.  This may override the state of a gateway, which
    # may be completed, but contain children that are not.
    state_precedence = ['READY', 'LIKELY', 'FUTURE', 'MAYBE', 'WAITING',
                        'COMPLETED', 'CANCELLED']
    for nav_item in nav_items:
        if len(nav_item.children) > 0:
            child_states = []
            for child in nav_item.children:
                child_states.append(set_deep_state([child]))
            for state in state_precedence:
                if state in child_states:
                    nav_item.state = state
                    return state
    return nav_item.state

def get_flat_nav_list(workflow):
    # This takes the flat navigation returned from the follow_tree, and
    # adds task states, producing a full flat navigation list.
    nav_items = []
    for top in workflow.task_tree.children[0].task_spec.outputs:
        nav_items.extend(follow_tree(top, output=[],
                                     found=set(), workflow=workflow))
    task_list = workflow.get_tasks()

    # look up task status for each item in the list
    used_tasks = set()  # set of tasks already used to get state.
    for nav_item in nav_items:
        # get a list of statuses for the current task_spec
        # we may have more than one task for each
        tasks = [x for x in task_list if
                 x.task_spec.id == nav_item.spec_id and
                 x.task_spec.name == nav_item.name and
                 x not in used_tasks]

        if len(tasks) == 0:
            # There is no task associated with this nav item, so we don't
            # know its state here.
            nav_item.state = None
            nav_item.task_id = None
        else:
            if len(tasks) == 1:
                task = tasks[0]
            else:
                # Something has caused us to loop back around in some way to
                # this task spec again, and so there are multiple states for
                # this navigation item. Opt for returning the last state.
                # the first ready task,
                # if available, then fall back to the last completed task.
                ready_task = next((t for t in tasks
                                   if t.state == Task.READY), None)
                comp_task = next((t for t in reversed(tasks)
                                  if t.state == Task.COMPLETED), None)
                if ready_task:
                    task = ready_task
                elif comp_task:
                    task = comp_task
                else:
                    task = tasks[0]  # Not sure what else to do here yet.
            used_tasks.add(task)
            nav_item.state = task.state_names[task.state]
            nav_item.task_id = task.id

    return nav_items


def same_ending_length(nav_with_children):
    """
    return the length of the endings of each child that match each other
    """
    # go get a modified list of just the ids in each child.
    endings = [[leaf.spec_id for leaf in branch.children] for branch in
               nav_with_children]
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


def conditional_task_add(output, task_spec, indent, backtrack_to=None):
    #if task_spec.id not in [x.spec_id for x in output]:
    output.append(NavItem.from_spec(spec=task_spec,
                                    backtrack_to=backtrack_to,
                                    indent=indent))


def follow_tree(tree, output=None, found=None, level=0, workflow=None):
    """RECURSIVE - follows the tree returning a list of NavItem objects"""

    # I had an issue with a test being nondeterministic the yes/no
    # were in an alternate order in some cases. To be 100% correct, this should
    # probably also use the X/Y information that we are parsing elsewhere, but
    # I did not see that information in the task spec.
    # At a bare minimum, this should fix the problem where keys in a dict are
    # flip-flopping.
    # After I'm done, you should be able to manage the order of the sequence flows by
    # naming the Flow_xxxxx names in the order you want them to appear.

    if found is None:
        found = set()
    if output is None:
        output = []
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
                             backtrack_to=False, indent=level)
        found.add(tree.id)
        return output

    # ---------------------
    # Call Activity - follow subtree
    # ---------------------
    if isinstance(tree, SubWorkflowTask):
        tasks = workflow.get_tasks_from_spec_name(tree.name)
        if len(tasks) == 0:
            # The call activity may not exist yet in some circumstances.
            return output
        tsk = tasks[0]
        x = tree.create_sub_workflow(tsk)

        output.append( NavItem.from_spec(tree, indent=level))

        sublist_outputs = [
            follow_tree(top, output=[], found=set(), level=level + 1, workflow=x)
            for top in x.task_tree.children[0].task_spec.outputs]
        for lst in sublist_outputs:
            for item in lst:
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
                conditional_task_add(output, task_spec, indent=level)
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
        if tree.id not in found:
            conditional_task_add(output, tree, indent=level)
            found.add(tree.id)
            output = follow_tree(link.target_task_spec, output, found,
                                 level, workflow)
        else:
            conditional_task_add(output, tree, indent=level, backtrack_to=tree.name)
        return output

    if isinstance(tree, _BoundaryEventParent):
        for task in outputs:
            link = tree.outgoing_sequence_flows[task]
            conditional_task_add(output, tree, indent=level)
            if link.target_task_spec.id not in found:
                found.add(link.target_task_spec.id)
                output = follow_tree(link.target_task_spec, output, found,
                                     level + 1, workflow)
        return output

    # if we are here, then we assume that we have a gateway of some form,
    # where more than one path will exist, we need to follow multiple paths
    # and then sync those paths and realign.
    task_children = []
    structured = not (isinstance(tree, UnstructuredJoin))
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
            my_children = []  # This is backtracking, no need to follow it.
            backtrack_link = flow.target_task_spec.name

        # Note that we append the NavWithChildren here, not just nav
        item = NavItem.from_flow(flow=flow, lane=tree.lane,
                                 backtrack_to=backtrack_link, indent=level + 1)
        item.children = my_children
        task_children.append(item)

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
        output.append(NavItem.from_spec(spec=tree,
                                        backtrack_to=None, indent=level))
        for child in task_children:
            # Add the flow nav item, but only if this is an exclsive gateway,
            # and not an instructured join
            if structured:
                output.append(child)
            for descendent in child.children:
                output.append(descendent)
            child.children = [] # Remove internal children, as the results
                                  # of this should be flat.

        if len(merge_list) > 0:
            # This bit gets the indentation right, we are merging back out
            # to the current level, so the first child here should be moved
            # out to current level, and any subsequent children should be
            # reduced by that same difference.
            indent_correction = merge_list[0].indent - level
            for child in merge_list:
                child.indent -= indent_correction
                if child.indent < 0:
                    child.indent=0
                output.append(child)

    found.add(tree.id)
    return output
