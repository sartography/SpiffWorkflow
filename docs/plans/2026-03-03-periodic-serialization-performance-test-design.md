# Periodic Serialization Performance Test Design

**Date:** 2026-03-03
**Status:** Approved

## Problem Statement

The `BpmnWorkflowSerializer.to_dict()` method walks the entire workflow task tree on every call. Current performance tests only measure serialization once after workflow completion. We need to understand the cost of repeated serialization calls during workflow execution, which is critical for checkpoint/state-saving scenarios.

## Context

Recent commits show significant work on serialization optimization:
- Commit 26fe7390: Reduced serialized workflow size using delta storage for child tasks
- Commit 5a865caa: Simplified serialization change detection
- Commit 7ac8477b: Made engine steps non-recursive

Analysis of `SpiffWorkflow/bpmn/serializer/default/workflow.py` confirms that `WorkflowConverter.to_dict()` calls `mapping_to_dict(workflow.tasks)`, which iterates through all tasks and converts each one. The delta optimization reduces output size but doesn't avoid the tree traversal.

## Design

### Test Method

Add one new test method to `tests/SpiffWorkflow/bpmn/test_performance_test.py`:

```python
test_performance_periodic_serialization_300_items()
```

### Execution Pattern

1. Create workflow with 300 items using existing `_create_workflow_with_item_count(300)` helper
2. Execute workflow in batches of 10 engine steps using `workflow.complete_next(10)`
3. After each batch:
   - Measure serialization time: `serializer.to_dict(workflow)`
   - Record task count: `len(workflow.tasks)`
   - Accumulate metrics
4. Continue until `workflow.is_completed()` returns True

### Metrics Collected

At each checkpoint:
- Individual serialization time
- Number of tasks in the workflow tree
- Step count

Summary metrics:
- Total execution time
- Total serialization time
- Number of serializations performed
- Average serialization time
- Serialization overhead percentage (total serialization / execution time)

### Output Format

```
PERIODIC SERIALIZATION TEST (performance_test.bpmn)
================================================================
  300 items (serialize every 10 steps):
    Execution time:           X.XXXXXX seconds

    Serialization checkpoints:
      After 10 steps  (N tasks):   X.XXXXXX seconds
      After 20 steps  (N tasks):   X.XXXXXX seconds
      After 30 steps  (N tasks):   X.XXXXXX seconds
      ...

    Total serialization time:       X.XXXXXX seconds
    Serialization overhead:         XX.X% of execution time
    Number of serializations:       N
    Average per serialization:      X.XXXXXX seconds
================================================================
```

## Expected Outcomes

This test will reveal:
1. How serialization time grows as the task tree expands during execution
2. The cumulative cost of repeated tree traversals
3. Whether serialization overhead becomes significant relative to execution time
4. Whether there are opportunities for incremental or differential serialization

## Implementation Approach

Following TDD:
1. Write failing test first
2. Verify it fails for the expected reason (method not implemented)
3. Implement minimal code to pass
4. Refactor if needed

## Alternatives Considered

**Multiple serializations on completed workflow:** Simpler but doesn't show how cost changes as tree grows. Rejected because it doesn't capture the realistic scenario of serializing during execution.

**Serialize after every step:** Too granular, would dominate test execution time. Using 10-step batches provides sufficient granularity while keeping test runtime reasonable.

**Test all item counts (20, 100, 200, 300):** Would provide more data points but significantly increase test suite runtime. Starting with 300 items (largest tree) provides the most meaningful signal. Can add more if needed.

## Success Criteria

- Test executes without errors
- Serialization happens multiple times during workflow execution
- Output clearly shows serialization time growth correlated with task count
- Results help inform serialization optimization decisions
