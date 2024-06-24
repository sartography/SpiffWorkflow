from .task import BpmnTaskFilter

class SpecDiff:

    def __init__(self, serializer, original, new):
        """This class is used to hold results for comparisions between two workflow specs.

        Attributes:
            registry: a serializer's registry
            unmatched (list(`TaskSpec`)): a list of task specs that cannot be aligned
            alignment (dict): a mapping of old task spec to new
            updated (dict): a mapping of old task spec to changed attributes

        The chief basis for alignment is `TaskSpec.name` (ie, the BPMN ID of the spec): if the IDs are identical,
        it is assumed the task specs correspond.  If a spec in the old version does not have an ID in the new,
        some attempt to match based on inputs and outputs is made.

        The general procdedure is to attempt to align as many tasks based on ID as possible first, and then
        attempt to match by other means while backing out of the traversal.

        Updates are organized primarily by the specs from the original version.
        """

        self.registry = serializer.registry
        self.unmatched = [spec for spec in new.task_specs.values() if spec.name not in original.task_specs]
        self.alignment = {}
        self.updated = {}
        self._align(original.start, new)

    @property
    def added(self):
        """Task specs from the new version that did not exist in the old"""
        return self.unmatched

    @property
    def removed(self):
        """Task specs from the old version that were removed from the new"""
        return [orig for orig, new in self.alignment.items() if new is None]

    @property
    def changed(self):
        """Task specs with updated attributes"""
        return dict((ts, changes) for ts, changes in self.updated.items() if changes)

    def _align(self, spec, new):

        candidate = new.task_specs.get(spec.name)
        self.alignment[spec] = candidate
        if candidate is not None:
            self.updated[spec] = self._compare_task_specs(spec, candidate)

        # Traverse the spec, prioritizing matching by name
        # Without this starting point, alignment would be way too difficult
        for output in spec.outputs:
            if output not in self.alignment:
                self._align(output, new)

        # If name matching fails, attempt to align by structure
        if candidate is None:
            self._search_unmatched(spec)

    def _search_unmatched(self, spec):
        # If any outputs were matched, we can use its unmatched inputs as candidates
        for match in self._substitutions(spec.outputs):
            for parent in [ts for ts in match.inputs if ts in self.unmatched]:
                if self._aligned(spec.outputs, parent.outputs):
                    path = [parent]     # We may need to check ancestor inputs as well as this spec's inputs
                    searched = []       # We have to keep track of what we've looked at in case of loops
                    self._find_ancestor(spec, path, searched)

    def _find_ancestor(self, spec, path, searched):
        if path[-1] not in searched:
            searched.append(path[-1])
        # Stop if we reach a previously matched spec or if an ancestor's inputs match
        if path[-1] not in self.unmatched or self._aligned(spec.inputs, path[-1].inputs):
            self.alignment[spec] = path[0]
            self.unmatched.remove(path[0])
        else:
            for parent in [ts for ts in path[-1].inputs if ts not in searched]:
                self._find_ancestor(spec, path + [parent], searched)

    def _substitutions(self, spec_list, skip_unaligned=True):
        subs = [self.alignment[ts] for ts in spec_list]
        return [ts for ts in subs if ts is not None] if skip_unaligned else subs

    def _aligned(self, original, candidates):
        subs = self._substitutions(original, skip_unaligned=False)
        return len(subs) == len(candidates) and \
            all(first is not None and first.name == second.name for first, second in zip(subs, candidates))

    def _compare_task_specs(self, spec, candidate):
        s1 = self.registry.convert(spec)
        s2 = self.registry.convert(candidate)
        if s1.get('typename') != s2.get('typename'):
            return ['typename']
        else:
            return [key for key, value in s1.items() if s2.get(key) != value]

class WorkflowDiff:
    """This class is used to determine which tasks in a workflow are affected by updates
    to its WorkflowSpec.

    Attributes
        workflow (`BpmnWorkflow`): a workflow instance
        spec_diff (`SpecDiff`): the results of a comparision of two specs
        removed (list(`Task`)): a list of tasks whose specs do not exist in the new version
        changed (list(`Task`)): a list of tasks with aligned specs where attributes have changed
        alignment (dict): a mapping of old task spec to new task spec
    """

    def __init__(self, workflow, spec_diff):
        self.workflow = workflow
        self.spec_diff = spec_diff
        self.removed = []
        self.changed = []
        self.alignment = {}
        self._align()

    def filter_tasks(self, tasks, **kwargs):
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

    def _align(self):
        for task in self.workflow.get_tasks(skip_subprocesses=True):
            if task.task_spec in self.spec_diff.changed:
                self.changed.append(task)
            if task.task_spec in self.spec_diff.removed:
                self.removed.append(task)
            else:
                self.alignment[task] = self.spec_diff.alignment[task.task_spec]
