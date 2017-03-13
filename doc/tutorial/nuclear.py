from SpiffWorkflow.specs import WorkflowSpec, ExclusiveChoice, Cancel
from SpiffWorkflow.operators import Equal, Attrib
from strike import NuclearStrike

class NuclearStrikeWorkflowSpec(WorkflowSpec):
    def __init__(self):
        WorkflowSpec.__init__(self)

        # The first step of our workflow is to let the general confirm
        # the nuclear strike.
        general_choice = ExclusiveChoice(self, 'general')
        self.start.connect(general_choice)

        # The default choice of the general is to abort.
        cancel = Cancel(self, 'workflow_aborted')
        general_choice.connect(cancel)

        # Otherwise, we will ask the president to confirm.
        president_choice = ExclusiveChoice(self, 'president')
        cond = Equal(Attrib('confirmation'), 'yes')
        general_choice.connect_if(cond, president_choice)

        # The default choice of the president is to abort.
        president_choice.connect(cancel)

        # Otherwise, we will perform the nuclear strike.
        strike = NuclearStrike(self, 'nuclear_strike')
        president_choice.connect_if(cond, strike)

        # As soon as all tasks are either "completed" or  "aborted", the
        # workflow implicitely ends.
