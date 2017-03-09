.. _features:

Features
========

Supported Workflow Patterns
---------------------------

.. HINT::
   All examples are located
   `here <https://github.com/knipknap/SpiffWorkflow/blob/master/tests/SpiffWorkflow/data/spiff/>`_.

Control-Flow Patterns
^^^^^^^^^^^^^^^^^^^^^

1. Sequence [control-flow/sequence.xml]
2. Parallel Split [control-flow/parallel_split.xml]
3. Synchronization [control-flow/synchronization.xml]
4. Exclusive Choice [control-flow/exclusive_choice.xml]
5. Simple Merge [control-flow/simple_merge.xml]
6. Multi-Choice [control-flow/multi_choice.xml]
7. Structured Synchronizing Merge [control-flow/structured_synchronizing_merge.xml]
8. Multi-Merge [control-flow/multi_merge.xml]
9. Structured Discriminator [control-flow/structured_discriminator.xml]
10. Arbitrary Cycles [control-flow/arbitrary_cycles.xml]
11. Implicit Termination [control-flow/implicit_termination.xml]
12. Multiple Instances without Synchronization [control-flow/multi_instance_without_synch.xml]
13. Multiple Instances with a Priori Design-Time Knowledge [control-flow/multi_instance_with_a_priori_design_time_knowledge.xml]
14. Multiple Instances with a Priori Run-Time Knowledge [control-flow/multi_instance_with_a_priori_run_time_knowledge.xml]
15. Multiple Instances without a Priori Run-Time Knowledge [control-flow/multi_instance_without_a_priori.xml]
16. Deferred Choice [control-flow/deferred_choice.xml]
17. Interleaved Parallel Routing [control-flow/interleaved_parallel_routing.xml]
18. Milestone [control-flow/milestone.xml]
19. Cancel Task [control-flow/cancel_task.xml]
20. Cancel Case [control-flow/cancel_case.xml]
21. *NOT IMPLEMENTED*
22. Recursion [control-flow/recursion.xml]
23. Transient Trigger [control-flow/transient_trigger.xml]
24. Persistent Trigger [control-flow/persistent_trigger.xml]
25. Cancel Region [control-flow/cancel_region.xml]
26. Cancel Multiple Instance Task [control-flow/cancel_multi_instance_task.xml]
27. Complete Multiple Instance Task [control-flow/complete_multiple_instance_activity.xml]
28. Blocking Discriminator [control-flow/blocking_discriminator.xml]
29. Cancelling Discriminator [control-flow/cancelling_discriminator.xml]
30. Structured Partial Join [control-flow/structured_partial_join.xml]
31. Blocking Partial Join [control-flow/blocking_partial_join.xml]
32. Cancelling Partial Join [control-flow/cancelling_partial_join.xml]
33. Generalized AND-Join [control-flow/generalized_and_join.xml]
34. Static Partial Join for Multiple Instances [control-flow/static_partial_join_for_multi_instance.xml]
35. Cancelling Partial Join for Multiple Instances [control-flow/cancelling_partial_join_for_multi_instance.xml]
36. Dynamic Partial Join for Multiple Instances [control-flow/dynamic_partial_join_for_multi_instance.xml]
37. Acyclic Synchronizing Merge [control-flow/acyclic_synchronizing_merge.xml]
38. General Synchronizing Merge [control-flow/general_synchronizing_merge.xml]
39. Critical Section [control-flow/critical_section.xml]
40. Interleaved Routing [control-flow/interleaved_routing.xml]
41. Thread Merge [control-flow/thread_merge.xml]
42. Thread Split [control-flow/thread_split.xml]
43. Explicit Termination [control-flow/explicit_termination.xml]

Workflow Data Patterns
^^^^^^^^^^^^^^^^^^^^^^

1. Task Data [data/task_data.xml]
2. Block Data [data/block_data.xml]
3. *NOT IMPLEMENTED*
4. *NOT IMPLEMENTED*
5. *NOT IMPLEMENTED*
6. *NOT IMPLEMENTED*
7. *NOT IMPLEMENTED*
8. *NOT IMPLEMENTED*
9. Task to Task [data/task_to_task.xml]
10. Block Task to Sub-Workflow Decomposition [data/block_to_subworkflow.xml]
11. Sub-Workflow Decomposition to Block Task [data/subworkflow_to_block.xml]

Specs that have no corresponding workflow pattern on workflowpatterns.com
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Execute - spawns a subprocess and waits for the results
- Transform - executes commands that can be used for data transforms
- Celery - executes a Celery task (see http://celeryproject.org/)
