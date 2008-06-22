import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def suite():
    tests = ['testInstall',
             'testJob',
             'testTask',
             'testWorkflow']
    return unittest.TestSuite(map(DBTest, tests))

import MySQLdb
from ConfigParser         import RawConfigParser
from sqlalchemy           import *
from sqlalchemy.orm       import clear_mappers
from SpiffWorkflow.Server import WorkflowInfo, JobInfo, TaskInfo
import SpiffWorkflow.Server

class DBTest(unittest.TestCase):
    def connectDB(self):
        # Read config.
        cfg = RawConfigParser()
        cfg.read(os.path.join(os.path.dirname(__file__), 'unit_test.cfg'))
        host     = cfg.get('database', 'host')
        db_name  = cfg.get('database', 'db_name')
        user     = cfg.get('database', 'user')
        password = cfg.get('database', 'password')

        # Connect to MySQL.
        auth        = user + ':' + password
        dbn         = 'mysql://' + auth + '@' + host + '/' + db_name
        self.engine = create_engine(dbn)
        clear_mappers()


    def setUp(self):
        self.connectDB()
        self.db = SpiffWorkflow.Server.DB(self.engine)


    def testInstall(self):
        self.assert_(self.db.uninstall())
        self.assert_(self.db.install())
        self.assert_(self.db.clear_database())
        self.assert_(self.db.uninstall())
        self.assert_(self.db.install())


    def testWorkflow(self):
        self.assert_(len(self.db.get_workflow_info(id = 1)) == 0)
        obj = WorkflowInfo('my/handle')
        self.db.save(obj)
        assert obj.id >= 0
        self.assert_(len(self.db.get_workflow_info(id = obj.id)) == 1)
        self.db.delete(obj)
        self.assert_(len(self.db.get_workflow_info(id = obj.id)) == 0)


    def testJob(self):
        self.assert_(len(self.db.get_job_info(id = 1)) == 0)
        obj = JobInfo()
        self.db.save(obj)
        assert obj.id >= 0
        self.assert_(len(self.db.get_job_info(id = obj.id)) == 1)
        self.db.delete(obj)
        self.assert_(len(self.db.get_job_info(id = obj.id)) == 0)


    def testTask(self):
        self.assert_(len(self.db.get_task_info(id = 1)) == 0)
        obj = TaskInfo()
        self.db.save(obj)
        assert obj.id >= 0
        self.assert_(len(self.db.get_task_info(id = obj.id)) == 1)
        self.db.delete(obj)
        self.assert_(len(self.db.get_task_info(id = obj.id)) == 0)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
