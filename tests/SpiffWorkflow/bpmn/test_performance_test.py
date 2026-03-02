"""
Performance tests for performance_test.bpmn.
Measures execution and serialization time across different item counts.
"""
import os
import time

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase


class PerformanceTest(BpmnWorkflowTestCase):
    """
    Measure workflow execution and serialization/deserialization time for various item counts.
    """

    def _create_workflow_with_item_count(self, count):
        """
        Create a workflow from performance_test.bpmn with modified item count.

        Args:
            count: Number of items to create (replaces the hardcoded 20)

        Returns:
            BpmnWorkflow instance ready to execute
        """
        # Read the original BPMN file
        bpmn_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'performance_test.bpmn'
        )
        with open(bpmn_path, 'r') as f:
            bpmn_content = f.read()

        # Replace the item count
        modified_content = bpmn_content.replace(
            'items = [item]*20',
            f'items = [item]*{count}'
        )

        # Write to a temporary file in the data directory
        tmp_filename = f'_temp_performance_test_{count}.bpmn'
        tmp_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            tmp_filename
        )

        with open(tmp_path, 'w') as f:
            f.write(modified_content)

        try:
            # Load the workflow spec
            spec, subprocesses = self.load_workflow_spec(
                tmp_filename,
                'Process_3no3Cw9',
                validate=False
            )
            workflow = BpmnWorkflow(spec, subprocesses)
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return workflow

    def test_performance_20_items(self):
        """Measure execution and serialization time with 20 items."""
        workflow = self._create_workflow_with_item_count(20)

        # Measure execution time
        start_execution = time.time()
        workflow.do_engine_steps()
        end_execution = time.time()
        execution_time = end_execution - start_execution

        # Verify workflow completed
        self.assertTrue(workflow.completed)

        # Measure serialization
        start_serialize = time.time()
        state = self.serializer.to_dict(workflow)
        end_serialize = time.time()
        serialize_time = end_serialize - start_serialize

        # Measure deserialization
        start_deserialize = time.time()
        restored_workflow = self.serializer.from_dict(state)
        end_deserialize = time.time()
        deserialize_time = end_deserialize - start_deserialize

        # Verify deserialization worked
        self.assertTrue(restored_workflow.completed)

        # Print results
        print("\n" + "="*80)
        print("PERFORMANCE TEST (performance_test.bpmn)")
        print("="*80)
        print(f"  20 items:")
        print(f"    Execution:      {execution_time:.6f} seconds")
        print(f"    Serialization:  {serialize_time:.6f} seconds")
        print(f"    Deserialization: {deserialize_time:.6f} seconds")
        print(f"    Total:          {execution_time + serialize_time + deserialize_time:.6f} seconds")
        print("="*80)

    def test_performance_100_items(self):
        """Measure execution and serialization time with 100 items."""
        workflow = self._create_workflow_with_item_count(100)

        # Measure execution time
        start_execution = time.time()
        workflow.do_engine_steps()
        end_execution = time.time()
        execution_time = end_execution - start_execution

        # Verify workflow completed
        self.assertTrue(workflow.completed)

        # Measure serialization
        start_serialize = time.time()
        state = self.serializer.to_dict(workflow)
        end_serialize = time.time()
        serialize_time = end_serialize - start_serialize

        # Measure deserialization
        start_deserialize = time.time()
        restored_workflow = self.serializer.from_dict(state)
        end_deserialize = time.time()
        deserialize_time = end_deserialize - start_deserialize

        # Verify deserialization worked
        self.assertTrue(restored_workflow.completed)

        # Print results
        print("\n" + "="*80)
        print("PERFORMANCE TEST (performance_test.bpmn)")
        print("="*80)
        print(f" 100 items:")
        print(f"    Execution:      {execution_time:.6f} seconds")
        print(f"    Serialization:  {serialize_time:.6f} seconds")
        print(f"    Deserialization: {deserialize_time:.6f} seconds")
        print(f"    Total:          {execution_time + serialize_time + deserialize_time:.6f} seconds")
        print("="*80)

    def test_performance_200_items(self):
        """Measure execution and serialization time with 200 items."""
        workflow = self._create_workflow_with_item_count(200)

        # Measure execution time
        start_execution = time.time()
        workflow.do_engine_steps()
        end_execution = time.time()
        execution_time = end_execution - start_execution

        # Verify workflow completed
        self.assertTrue(workflow.completed)

        # Measure serialization
        start_serialize = time.time()
        state = self.serializer.to_dict(workflow)
        end_serialize = time.time()
        serialize_time = end_serialize - start_serialize

        # Measure deserialization
        start_deserialize = time.time()
        restored_workflow = self.serializer.from_dict(state)
        end_deserialize = time.time()
        deserialize_time = end_deserialize - start_deserialize

        # Verify deserialization worked
        self.assertTrue(restored_workflow.completed)

        # Print results
        print("\n" + "="*80)
        print("PERFORMANCE TEST (performance_test.bpmn)")
        print("="*80)
        print(f" 200 items:")
        print(f"    Execution:      {execution_time:.6f} seconds")
        print(f"    Serialization:  {serialize_time:.6f} seconds")
        print(f"    Deserialization: {deserialize_time:.6f} seconds")
        print(f"    Total:          {execution_time + serialize_time + deserialize_time:.6f} seconds")
        print("="*80)

    def test_performance_300_items(self):
        """Measure execution and serialization time with 300 items."""
        workflow = self._create_workflow_with_item_count(300)

        # Measure execution time
        start_execution = time.time()
        workflow.do_engine_steps()
        end_execution = time.time()
        execution_time = end_execution - start_execution

        # Verify workflow completed
        self.assertTrue(workflow.completed)

        # Measure serialization
        start_serialize = time.time()
        state = self.serializer.to_dict(workflow)
        end_serialize = time.time()
        serialize_time = end_serialize - start_serialize

        # Measure deserialization
        start_deserialize = time.time()
        restored_workflow = self.serializer.from_dict(state)
        end_deserialize = time.time()
        deserialize_time = end_deserialize - start_deserialize

        # Verify deserialization worked
        self.assertTrue(restored_workflow.completed)

        # Print results
        print("\n" + "="*80)
        print("PERFORMANCE TEST (performance_test.bpmn)")
        print("="*80)
        print(f" 300 items:")
        print(f"    Execution:      {execution_time:.6f} seconds")
        print(f"    Serialization:  {serialize_time:.6f} seconds")
        print(f"    Deserialization: {deserialize_time:.6f} seconds")
        print(f"    Total:          {execution_time + serialize_time + deserialize_time:.6f} seconds")
        print("="*80)

