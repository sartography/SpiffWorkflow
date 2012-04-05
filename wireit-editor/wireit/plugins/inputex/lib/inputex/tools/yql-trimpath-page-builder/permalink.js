/* 

This is a small utility to save the state of a client application in the url.
We use Tinyurl.com through the http://json-tinyurl.appspot.com/ webservice.

Exemple:
========

	var loadConfig = Permalink.load();
	console.log( loadConfig );
	var config = loadConfig || {"hello":"World","n":9}

	var pl = Permalink.get(config);
	console.log(pl);

	Permalink.getTiny( config, function(tinyurl){
   	var a = document.getElementById('link');
   	a.href=tinyurl;
   	a.innerHTML = tinyurl;
	});
	
*/
var Permalink = {

   load: function() {
		var s = window.location.search.substr(1);
		if( s.substr(0,10) != "permalink=" ) return null;
		return YAHOO.lang.JSON.parse(window.decodeURIComponent(s.substr(10)));
   },

   get: function(config) {
		var l = window.location, pl = YAHOO.lang.JSON.stringify(config);
		return l.protocol+"//"+l.host+l.pathname+"?permalink="+pl;
   },

   getTiny: function(config, success) {

	var longURL = this.get(config),
	    ud = 'pl'+(Math.random()*100).toString().replace(/\./g,''),
            API = 'http://json-tinyurl.appspot.com/?url=',
	    url = API + encodeURIComponent(longURL) + '&callback=' + ud;
         
         window[ud]= function(o){ success&&success(o.tinyurl); };

         document.getElementsByTagName('body')[0].appendChild((function(){
           var s = document.createElement('script');
           s.type = 'text/javascript';
           s.src = url;
           return s;
         })());
   }
};

