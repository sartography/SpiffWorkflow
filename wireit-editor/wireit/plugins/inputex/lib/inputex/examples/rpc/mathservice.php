<?php

   $jsonRequest = file_get_contents('php://input');

   // Deserialize JSON
   $req = json_decode($jsonRequest);

   // run appropriate method
   if($req->method == "add") {
      $result = $req->params->a+$req->params->b;
   }

   // Serialize result
   $r = array();
   $r["result"] = $result;
   $r["error"] = NULL;
   $r["id"] = $req->id;
   
   echo json_encode($r);
?>