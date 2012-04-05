/**
 * <h1>inputEx YQL utility</h1>
 * <p>Provide functions to run YQL javascript code and get results asynchronously.</p>
 * <p>YQL Execute is only available from a YQL request using a YQL Open Table XML file.
 * This script uses a php (http://javascript.neyric.com/yql/js.php) to generate the wanted XML file from javascript code.</p>
 * <p>Examples:</p>
 * <ul>
 *    <li><a href='http://javascript.neyric.com/yql/js.php?url=http://gist.github.com/106503.txt'>http://javascript.neyric.com/yql/js.php?url=http://gist.github.com/106503.txt</a></li>
 *    <li><a href='http://javascript.neyric.com/yql/js.php?code=...jscode...'>http://javascript.neyric.com/yql/js.php?code=...jscode...</a></li>
 * </ul>
 * <p>We use a classic JSONP hack to get the results via a callback method.</p>
 * @class inputEx.YQL
 * @static
 */
inputEx.YQL = {
	
	// Used as an identifier for the JSONP callback hack
	query_index: 0,
	
	/**
	 * Generate the jsonp request to YQL
	 * @param {String} yql YQL query string
	 * @param {Function} callback Callback function
	 */
	query: function(yql, callback) {
		 var ud = 'yqlexecuteconsole'+(inputEx.YQL.query_index)++,
		      API = 'http://query.yahooapis.com/v1/public/yql?q=',
		      url = API + window.encodeURIComponent(yql) + '&format=json&callback=' + ud;
		 window[ud]= function(o){ callback && callback(o); };
	    document.body.appendChild((function(){
		    var s = document.createElement('script');
          s.type = 'text/javascript';
	       s.src = url;
	       return s;
	    })());	
	},
	
	/**
	 * Dynamically build a XML from javascript code and generate a dummy request for YQL
	 * @param {String} codeStr YQL-execute javascript code
	 * @param {Function} callback Callback function
	 */
	queryCode: function(codeStr, callback) {
		var url = ("http://javascript.neyric.com/yql/js.php?code="+window.encodeURIComponent(codeStr)).replace(new RegExp("'","g"),"\\'");
		var yql = "use '"+url+"' as yqlexconsole; select * from yqlexconsole;";
		inputEx.YQL.query(yql,callback);
	},
	
	/**
	 * Dynamically build a XML from a URL and generate a dummy request for YQL
	 * @param {String} codeUrl Url to a YQL-execute javascript file
	 * @param {Function} callback Callback function
	 */
	queryUrl: function(codeUrl, callback) {
	   var url = ("http://javascript.neyric.com/yql/js.php?url="+window.encodeURIComponent(codeUrl)).replace(new RegExp("'","g"),"\\'");
		var yql = "use '"+url+"' as yqlexconsole; select * from yqlexconsole;";
		inputEx.YQL.query(yql,callback);
	},
	
	/**
	 * Run script type="text/yql" tags on YQL servers
	 * If you have just one script tag and one callback, pass [[function(results) {}]]
	 * If you have two script tags and two callback for each: [ [function() {},function() {}] , [function() {},function() {}]]
	 * etc...
	 * @param {Array} callbacks Array of (list of callbacks functions) (provide a list of callbacks for each script type="text/yql" tag in the page)
	 */
	init: function(callbacks) {
	   var yqlScripts = YAHOO.util.Dom.getElementsBy( function(el) {
   		return (el.type && el.type == "text/yql");
   	} , "script" );

      var genCallbackFunction = function(fcts) {
         return function(results) {
            for(var i = 0 ; i < fcts.length ; i++) {
              fcts[i].call(this, results);
            }
         };
      };

      for(var i = 0 ; i < yqlScripts.length ; i++) {
         var yqlCode = yqlScripts[i].innerHTML;
      	inputEx.YQL.queryCode(yqlCode, genCallbackFunction(callbacks[i]) );
      }
	},
	
	/**
	 * YQL-trimpath-page is a utility to create pages using YQL queries ant Trimpath templating
	 * All YQL queries are made using the rpc/yql.js utility.
	 * see examples/yql-trimpath-page.html
	 * Call this method on page load to run yql queries and the associated templates
	 * @param {Array} additionalCallbacks List of [list of callbacks] (each yql query can call multiple callbacks)
	 */
	initTrimpathPage: function(additionalCallbacks) {
   
		 var templates = YAHOO.util.Dom.getElementsBy( function(el) {
	   		return (el.type && el.type == "text/trimpath");
	   } , "script" );

	 	var callbacks = [];

		for(var i = 0 ; i < templates.length ; i++) {
			var t = templates[i];
			var split = t.src.split('#');
			var requestId = parseInt(split[split.length-1], 10);
			if(!callbacks[requestId]) callbacks[requestId] = [];
			callbacks[requestId].push( inputEx.YQL.genTrimpathCallback(t) );
		}
	
		if(additionalCallbacks) {
		   for(i = 0 ; i < additionalCallbacks.length ; i++) {
		      var cbks = additionalCallbacks[i];
		      if(YAHOO.lang.isArray(cbks)) {
		         if(!callbacks[i]) callbacks[i] = [];
		         for(var j = 0 ; j < cbks.length ; j++) {
	   		      callbacks[i].push( cbks[j] );
			      }
		      }
		   }
	   }

		inputEx.YQL.init(callbacks);
	},

	/**
	 * Build a callback that runs a trimpath template (used by initTrimpathPage)
	 * @static
	 * @private
	 */
	genTrimpathCallback: function(scriptTag) {
	  return function(results) {
	     var t = TrimPath.parseTemplate(scriptTag.innerHTML);
		  var templateResult = t.process(results);
	     scriptTag.parentNode.innerHTML += "<div class='trimpathDiv'>"+templateResult+"</div>";
	  };
	}

};

