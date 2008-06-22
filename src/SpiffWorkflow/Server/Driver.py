# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sqlalchemy            import *
from Exceptions            import WorkflowServerException
from DB                    import DB
from JobInfo               import JobInfo
from TaskInfo              import TaskInfo
from SpiffWorkflow.Storage import XmlReader
from SpiffWorkflow.Job     import Job

class Driver(object):
    """
    A driver provides an API for storing and loading workflows, receiving
    information regarding running Jobs, and for driving the workflow
    execution.
    """
    
    def __init__(self, db):
        """
        Instantiates a new Driver.
        
        @type  db: object
        @param db: An sqlalchemy database connection.
        @rtype:  Driver
        @return: The new instance.
        """
        self.db        = DB(db)
        self.xmlreader = XmlReader()


    def install(self):
        """
        Installs (or upgrades) the workflow server.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.db.install()


    def uninstall(self):
        """
        Uninstall the workflow engine. This also permanently removes all data,
        history, and running jobs. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.db.uninstall()


    def get_workflow_info(self, **filter):
        """
        Returns the WorkflowInfo objects that match the given criteria.

        @rtype:  [WorkflowInfo]
        @return: A list of WorkflowInfo objects from the database.
        """
        return self.db.get_workflow_info(**filter)


    def save_workflow_info(self, object):
        """
        Store the WorkflowInfo in the database.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.db.save(object)


    def delete_workflow_info(self, object):
        """
        Delete the WorkflowInfo from the database.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.db.delete(object)


    def create_job(self, workflow_info):
        """
        Creates an instance of the given workflow.

        @rtype:  JobInfo
        @return: The JobInfo for the newly created workflow instance.
        """
        if workflow_info is None:
            raise WorkflowServerException('workflow_info argument is None')
        if workflow_info.id is None:
            raise WorkflowServerException('workflow_info must be saved first')
        workflow = self.xmlreader.parse_string(workflow_info.xml)
        job      = Job(workflow[0])
        job_info = JobInfo(workflow_info.id, job)
        self.__save_job_info(job_info)
        return job_info


    def get_job_info(self, **filter):
        """
        Returns the workflow instances that matches the given criteria.

        @rtype:  [JobInfo]
        @return: A list of JobInfo objects from the database.
        """
        return self.db.get_job_info(**filter)


    def __save_job_info(self, job_info):
        self.db.save(job_info)
        for node in job_info.instance.branch_tree:
            task_info = self.get_task_info(job_id  = job_info.id,
                                           node_id = node.id)
            if len(task_info) == 1:
                task_info = task_info[0]
            elif len(task_info) == 0:
                task_info = TaskInfo(job_info.id, node)
            else:
                raise WorkflowServerException('More than one task found')
            task_info.status = node.state
            self.db.save(task_info)


    def delete_job_info(self, object):
        """
        Delete the workflow instance from the database.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        return self.db.delete(object)


    def get_task_info(self, **filter):
        """
        Returns the tasks that match the given criteria.

        @rtype:  [TaskInfo]
        @return: A list of TaskInfo objects from the database.
        """
        return self.db.get_task_info(**filter)


    def execute_task(self, task_info):
        if task_info is None:
            raise WorkflowServerException('task_info argument is None')
        if task_info.id is None:
            raise WorkflowServerException('task_info must be saved first')
        if task_info.status & task_info.WAITING == 0:
            raise WorkflowServerException('task is not in WAITING state')
        if task_info.job_id is None:
            raise WorkflowServerException('task_info must be associated with a job')
        job_info_list = self.get_job_info(id = task_info.job_id)
        if len(job_info_list) == 0:
            raise WorkflowServerException('Job not found')
        elif len(job_info_list) > 1:
            raise WorkflowServerException('Fatal error: More than one Job found')

        job_info = job_info_list[0]
        if job_info.status is job_info.COMPLETED:
            raise WorkflowServerException('Job is already completed')
        result = job_info.instance.execute_task_from_id(task_info.node_id)
        self.__save_job_info(job_info)
        return result
