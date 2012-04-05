
CREATE TABLE `wirings` (
   `id` int( 11 ) NOT NULL AUTO_INCREMENT ,
   `name` varchar( 255 ) NOT NULL ,
   `working` text NOT NULL ,
   `language` varchar( 255 ) NOT NULL ,

   PRIMARY KEY ( `id` ) ,
   KEY `name` ( `name` , `language` )
);