from .base import EventDefinition

class ConditionalEventDefinition(EventDefinition):
    """Conditional events can be used to trigger flows based on the state of the workflow"""

    def __init__(self, expression, **kwargs):
        super().__init__(**kwargs)
        self.expression = expression

    def has_fired(self, my_task):
        my_task._set_internal_data(
            has_fired=my_task.workflow.script_engine.evaluate(my_task, self.expression, external_context=my_task.workflow.data)
        )
        return my_task._get_internal_data('has_fired', False)
