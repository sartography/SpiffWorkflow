Parsing BPMN
============

The example application assumes that a :code:`BpmnProcessSpec` will be generated for each process independently of
starting a workflow and that these will be immediately serialized and provided with a ID.  We'll discuss serialization
in greater detail later; for now we'll simply note that the file serializer simply writes a JSON representation of the
spec to a file and uses the filename as the ID.

.. note::

    This is design choice -- it would be possible to re-parse the specs each time a process was run.

Default Parsers
===============

Importing
---------

Each of the BPMN modules (:code:`bpmn`, :code:`spiff`, or :code:`camunda`) has a parser that is preconfigured with
the specs in that module (if a particular TaskSpec is not implemented in the module, :code:`bpmn` TaskSpec is used).

- :code:`bpmn`: :code:`from SpiffWorkflow.bpmn.parser import BpmnParser`
- :code:`dmn`: :code:`from SpiffWorkflow.dmn.parser import BpmnDmnParser`
- :code:`spiff`: :code:`from SpiffWorkflow.spiff.parser import SpiffBpmnParser`
- :code:`camunda`: :code:`from SpiffWorkflow.camunda.parser import CamundaParser`

.. note::

    The default parser cannot parse DMN files.  The :code:`BpmnDmnParser` extends the default parser to add that
    capability.  Both the :code:`spiff` and :code:`camunda` parsers inherit from :code:`BpmnDmnParser`.

Instantiation of a parser has no required arguments, but there are several optional parameters.

Validation
----------

The :code:`SpiffWorkflow.bpmn.parser` module also contains a :code:`BpmnValidator`.

The default validator validates against the BPMN 2.0 spec.  It is possible to import additional specifications (e.g.
for custom extensions) as well.

By default the parser does not validate, but if a validator is passed in, it will be used on any files added to the parser.

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import BpmnParser, BpmnValidator
    parser = BpmnParser(validator=BpmnValidator())

Spec Descriptions
-----------------

A default set of :code:`decription` attributes for each Task Spec.  The description is intended to be a user-friendly
representation of the task type.  It is a mapping of XML tag to string.

The default set of descriptions can be found in :code:`SpiffWorkflow.bpmn.parser.spec_descriptions`.

Creating a BpmnProcessSpec from BPMN Process
--------------------------------------------

From the :code:`add_spec` method of our BPMN engine (:app:`engine/engine.py`):

.. code-block:: python

    def add_spec(self, process_id, bpmn_files, dmn_files):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec = self.parser.get_spec(process_id)
            dependencies = self.parser.get_subprocess_specs(process_id)
        except ValidationException as exc:
            self.parser.process_parsers = {}
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {process_id} with id {spec_id}')
        return spec_id

    def add_files(self, bpmn_files, dmn_files):
        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files is not None:
            self.parser.add_dmn_files(dmn_files)

The first step is adding BPMN and DMN files to the parser using the :code:`add_bpmn_files` and
:code:`add_dmn_files` methods.

We use the :code:`get_spec` to parse the BPMN process with the provided :code:`process_id` (*not* the process name).

.. note::

    Ths parser was designed to load one set of files and parse a process and will raise a :code:`ValidationException`
    if any duplicate iDs are present.  The available processes are immediately added to :code:`process_parsers`, so
    re-adding a file will generate an exception.  Therefore, if we run into a problem (the specific case here) or wish
    to reuse the same parser, we need to clear this attribute.

Other Methods for Adding Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :code:`add_bpmn_files_by_glob`: Loads files from a glob instead of a list.
- :code:`add_bpmn_file`: Adds one file rather than a list.
- :code:`load_bpmn_str`: Loads and parses XML from a string.
- :code:`load_bpmn_io`: Loads and parses XML from an object implementing the IO interface.
- :code:`load_bpmn_xml`: Parses BPMN from an :code:`lxml` parsed tree.

.. _parsing_subprocesses:

Handling Subprocesses and Call Activities
-----------------------------------------

Internally, Call Activities and Subprocesses (as well as Transactional Subprocesses) are all treated as separate
specifications.  This is to prevent a single specification from becoming too large, especially in the case where the
same process spec will be called more than once.

The :code:`get_subprocess_specs` method takes a process ID and recursively searches for Call Activities, Subprocesses,
etc used by or defined in the provided BPMN files.  It returns a mapping of process ID to parsed specification.

Other Methods for Finding Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :code:`find_all_specs`: Returns a mapping of name -> :code:`BpmnWorkflowSpec` for all processes in all files that have been
  provided to the parser at that point.
- :code:`get_process_dependencies`: Returns a list of process IDs referenced by the provided process ID
- :code:`get_dmn_dependencies`: Returns a list of DMN IDs referenced by the provided process ID

Creating a BpmnProcessSpec from a BPMN Collaboration
----------------------------------------------------

The parser can also generate a workflow spec based on a collaboration:

.. code-block:: python

    def add_collaboration(self, collaboration_id, bpmn_files, dmn_files=None):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec, dependencies = self.parser.get_collaboration(collaboration_id)
        except ValidationException as exc:
            self.parser.process_parsers = {}
            raise exc

A spec is created for each of the processes in the collaboration, and each of these processes is wrapped inside a
subworkflow.  This means that a spec created this way will *always* require subprocess specs, and this method
returns the generated spec (which doesn't directly correspond to anything in the BPMN file) as well as the processes
present in the file, and theit dependencies.

