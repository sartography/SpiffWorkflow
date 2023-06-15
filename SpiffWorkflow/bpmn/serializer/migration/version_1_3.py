def update_event_definition_attributes(dct):

    def update_specs(wf_spec):
        for spec in wf_spec['task_specs'].values():
            if 'event_definition' in spec:
                spec['event_definition'].pop('internal', None)
                spec['event_definition'].pop('external', None)
                if 'escalation_code' in spec['event_definition']:
                    spec['event_definition']['code'] = spec['event_definition'].pop('escalation_code')
                if 'error_code' in spec['event_definition']:
                    spec['event_definition']['code'] = spec['event_definition'].pop('error_code')          

    update_specs(dct['spec'])
    for sp_spec in dct['subprocess_specs'].values():
        update_specs(sp_spec)