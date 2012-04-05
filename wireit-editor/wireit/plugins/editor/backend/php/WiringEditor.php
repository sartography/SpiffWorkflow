<?php

class WiringEditor {
   
    private $dbData = array (
       'dbhost' => "localhost",
       'dbuser' => "root",
       'dbpass' => "root",
       'dbname' => "WireIt"
    );
    
    private $link = null;

    private function connect() {
       if($this->link) {
          return;
       }
       $this->link = mysql_connect( $this->dbData["dbhost"], $this->dbData["dbuser"], $this->dbData["dbpass"]);
       mysql_select_db($this->dbData["dbname"]);
    }

    private function query($sql) {
       $this->connect();
       return mysql_query($sql);
    }
    
    private function queryToArray($sql) {
       $res = $this->query($sql);
       $obj = array();
       while($line = mysql_fetch_assoc($res)) {
          $obj[]=$line;
       }
       return $obj;
    }
    
    
    // variable needs to be in alphabetical order
    public function saveWiring($language, $name, $working) {
       
    	$result = $this->query( sprintf("SELECT * from wirings where name='%s' AND language='%s'", mysql_real_escape_string($name), mysql_real_escape_string($language)) );

      if( mysql_num_rows($result) == 0) {
    		$query = sprintf("INSERT INTO wirings (`name` ,`language`,`working`) VALUES ('%s','%s','%s');", 		
    							mysql_real_escape_string($name), 
    							mysql_real_escape_string($language),
    							mysql_real_escape_string($working) );
    	}
    	else {
    		$query = sprintf("UPDATE wirings SET working='%s' where name='%s' AND language='%s';",
    							mysql_real_escape_string($working),
    							mysql_real_escape_string($name),
    							mysql_real_escape_string($language) );
    	}
    	
    	$this->query($query);
       
      return true;
    }
    
    public function listWirings($language) {
	
	     $query = sprintf("SELECT * from wirings WHERE `language`='%s'", $language );
         $wirings = $this->queryToArray( $query );
         return $wirings;
    }
     
    public function loadWiring($language, $name) {
       $wirings = $this->queryToArray( sprintf("SELECT * from wirings WHERE name='%s' AND language='%s'", mysql_real_escape_string($name), mysql_real_escape_string($language)) );
       return $wirings[0];
    }
      
    public function deleteWiring($language, $name) {
      $this->query( sprintf("DELETE from wirings WHERE name='%s' AND language='%s'", mysql_real_escape_string($name), mysql_real_escape_string($language)) );
      return true;
   }
       
}

// JSON-RPC
class jsonRPCServer {
	public static function handle($object) {
	   
		if ($_SERVER['REQUEST_METHOD'] != 'POST')
			return false;
				
		$request = json_decode(file_get_contents('php://input'),true);
		
		try {
			if ($result = @call_user_func_array(array($object,$request['method']),$request['params'])) {
				$response = array ('id' => $request['id'],'result' => $result,'error' => NULL);
			} else {
				$response = array ('id' => $request['id'], 'result' => NULL,'error' => "unknown method '".$request['method']."' or incorrect parameters");
			}
		} catch (Exception $e) {
			$response = array ('id' => $request['id'],'result' => NULL,'error' => $e->getMessage());
		}
		
		if (!empty($request['id'])) {
			header('content-type: text/javascript');
			echo json_encode($response);
		}
		
		return true;
	}
}

$myExample = new WiringEditor();
jsonRPCServer::handle($myExample) or print 'no request';

?>
