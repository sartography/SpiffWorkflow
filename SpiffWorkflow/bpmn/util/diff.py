from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.specs.mixins.multiinstance_task import LoopTask
from .task import BpmnTaskFilter

class SpecDiff:
    """This class is used to hold results for comparisions between two workflow specs.

    Attributes:
        added (list(`TaskSpec`)):  task specs from the new version that cannot be aligned
        alignment (dict): a mapping of old task spec to new
        comparisons (dict): a mapping of old task spec to changed attributes

    Properties:
        removed (list of `TaskSpec`: specs from the original that cannot be aligned
        changed (dict): a filtered version of comparisons that contains only changed items


    The chief basis for alignment is `TaskSpec.name` (ie, the BPMN ID of the spec): if the IDs are identical,
    it is assumed the task specs correspond.  If a spec in the old version does not have an ID in the new,
    some attempt to match based on inputs and outputs is made.

    The general procdedure is to attempt to align as many tasks based on ID as possible first, and then
    attempt to match by other means while backing out of the traversal.

    Updates are organized primarily by the specs from the original version.
    """

    def __init__(self, registry, original, new):
        """Constructor for a spec diff.

        Args:
            registry (`DictionaryConverter`): a serislizer registry
            original (`BpmnProcessSpec`): the original spec
            new (`BpmnProcessSpec`): the spec to compare

        Aligns specs from the original with specs from the new workflow and checks each aligned pair
        for chames.
        """
        self.added = [spec for spec in new.task_specs.values() if spec.name not in original.task_specs]
        self.alignment = {}
        self.comparisons = {}
        self._registry = registry
        self._align(original.start, original, new)

    @property
    def removed(self):
        """Task specs from the old version that were removed from the new"""
        return [orig for orig, new in self.alignment.items() if new is None]

    @property
    def changed(self):
        """Task specs with updated attributes"""
        return dict((ts, changes) for ts, changes in self.comparisons.items() if changes)

    def _align(self, spec, original, new):

        candidate = new.task_specs.get(spec.name)
        self.alignment[spec] = candidate
        if candidate is not None:
            self.comparisons[spec] = self._compare_task_specs(spec, candidate)

        # Traverse the spec, prioritizing matching by name
        # Without this starting point, alignment would be way too difficult
        for output in spec.outputs:
            if output not in self.alignment:
                self._align(output, original, new)

        # If name matching fails, attempt to align by structure
        if candidate is None:
            self._search_unmatched(spec)

        # Multiinstance task specs aren't reachable via task outputs
        if isinstance(spec, LoopTask):
            original_child = original.task_specs.get(spec.task_spec)
            self.alignment[original_child] = new.task_specs.get(original_child.name)
            if self.alignment[original_child] is None:
                aligned = self.alignment[spec]
                if aligned is not None and isinstance(aligned, LoopTask):
                    self.alignment[original_child] = new.task_specs.get(aligned.task_spec)
            if self.alignment[original_child] is not None:
                self.comparisons[original_child] = self._compare_task_specs(original_child, self.alignment[original_child])

    def _search_unmatched(self, spec):
        # If any outputs were matched, we can use its unmatched inputs as candidates
        for match in self._substitutions(spec.outputs):
            for parent in [ts for ts in match.inputs if ts in self.added]:
                if self._aligned(spec.outputs, parent.outputs):
                    path = [parent]     # We may need to check ancestor inputs as well as this spec's inputs
                    searched = []       # We have to keep track of what we've looked at in case of loops
                    self._find_ancestor(spec, path, searched)

    def _find_ancestor(self, spec, path, searched):
        if path[-1] not in searched:
            searched.append(path[-1])
        # Stop if we reach a previously matched spec or if an ancestor's inputs match
        if path[-1] not in self.added or self._aligned(spec.inputs, path[-1].inputs):
            self.alignment[spec] = path[0]
            if path[0] in self.added:
                self.added.remove(path[0])
            self.comparisons[spec] = self._compare_task_specs(spec, path[0])
        else:
            for parent in [ts for ts in path[-1].inputs if ts not in searched]:
                self._find_ancestor(spec, path + [parent], searched)

    def _substitutions(self, spec_list, skip_unaligned=True):
        subs = [self.alignment.get(ts) for ts in spec_list]
        return [ts for ts in subs if ts is not None] if skip_unaligned else subs

    def _aligned(self, original, candidates):
        subs = self._substitutions(original, skip_unaligned=False)
        return len(subs) == len(candidates) and \
            all(first is not None and first.name == second.name for first, second in zip(subs, candidates))

    def _compare_task_specs(self, spec, candidate):

        s1 = self._registry.convert(spec)
        s2 = self._registry.convert(candidate)
        if s1.get('typename') != s2.get('typename'):
            return ['typename']
        else:
            return [key for key, value in s1.items() if s2.get(key) != value]

class WorkflowDiff:
    """This class is used to determine which tasks in a workflow are affected by updates
    to its WorkflowSpec.

    Attributes
        removed (list(`Task`)): a list of tasks whose specs do not exist in the new version
        changed (list(`Task`)): a list of tasks with aligned specs where attributes have changed
        alignment (dict): a mapping of old task spec to new task spec
    """

    def __init__(self, workflow, spec_diff):
        self.removed = []
        self.changed = []
        self.alignment = {}
        self._align(workflow, spec_diff)

    def _align(self, workflow, spec_diff):
        for task in workflow.get_tasks(skip_subprocesses=True):
            if task.task_spec in spec_diff.changed:
                self.changed.append(task)
            if task.task_spec in spec_diff.removed:
                self.removed.append(task)
            else:
                self.alignment[task] = spec_diff.alignment[task.task_spec]


def diff_dependencies(registry, original, new):
    """Helper method for comparing sets of spec dependencies.

    Args:
        registry (`DictionaryConverter`): a serislizer registry
        original (dict): the name -> `BpmnProcessSpec` mapping for the original spec
        new (dict): the name -> `BpmnProcessSpec` mapping for the updated spec

    Returns:
        a tuple of:
            mapping from name -> `SpecDiff` (or None) for each original dependency
            list of names of specs in the new dependencies that did not previously exist
    """
    result = {}
    subprocesses = {}
    for name, spec in original.items():
        if name in new:
            result[name] = SpecDiff(registry, spec, new[name])
        else:
            result[name] = None

    return result, [name for name in new if name not in original]


def diff_workflow(registry, workflow, new_spec, new_dependencies):
    """Helper method to handle diffing a workflow and all its dependencies at once.

    Args:
        registry (`DictionaryConverter`): a serislizer registry
        workflow (`BpmnWorkflow`): a workflow instance
        new_spec (`BpmnProcessSpec`): the new top level spec
        new_depedencies (dict): a dictionary of name -> `BpmnProcessSpec`

    Returns:
        tuple of `WorkflowDiff` and mapping of subworkflow id -> `WorkflowDiff`

    This method checks the top level workflow against the new spec as well as any 
    existing subprocesses for missing or updated specs.
    """
    spec_diff = SpecDiff(registry, workflow.spec, new_spec)
    top_diff = WorkflowDiff(workflow, spec_diff)
    sp_diffs = {}
    for sp_id, sp in workflow.subprocesses.items():
        if sp.spec.name in new_dependencies:
            dep_diff = SpecDiff(registry, sp.spec, new_dependencies[sp.spec.name])
            sp_diffs[sp_id] = WorkflowDiff(sp, dep_diff)
        else:
            sp_diffs[sp_id] = None
    return top_diff, sp_diffs

def filter_tasks(tasks, **kwargs):
    """Applies task filtering arguments to a list of tasks.

    Args:
        tasks (list(`Task`)): a list of of tasks

    Keyword Args:
        any keyword arg that may be passed to `BpmnTaskFilter`

    Returns:
        a list containing tasks matching the filter
    """
    task_filter = BpmnTaskFilter(**kwargs)
    return [t for t in tasks if task_filter.matches(t)]

def migrate_workflow(diff, workflow, spec, reset_mask=None):
    """Update the spec for workflow.

    Args:
        diff (`WorkflowDiff`): the diff of this workflow and spec
        workflow (`BpmnWorkflow` or `BpmnSubWorkflow`): the workflow
        spec (`BpmnProcessSpec`): the new spec

    Keyword Args:
        reset_mask (`TaskState`): reset and repredict tasks in this state

    The default rest_mask is TaskState.READY|TaskState.WAITING but can be overridden.
    """
    workflow.spec = spec
    for task in workflow.tasks.values():
        if diff.alignment.get(task) is not None:
            task.task_spec = diff.alignment.get(task)

    default_mask = TaskState.READY|TaskState.WAITING
    for task in list(workflow.get_tasks(state=reset_mask or default_mask, skip_subprocesses=True)):
        # In some cases, completed tasks with ready or waiting children could get removed
        # (for example, in cycle timer).  If a task has already been removed from the tree, ignore it.
        if task.id in workflow.tasks:
            task.reset_branch(None)
    
    if workflow.last_task not in workflow.tasks:
        workflow.last_task = None
