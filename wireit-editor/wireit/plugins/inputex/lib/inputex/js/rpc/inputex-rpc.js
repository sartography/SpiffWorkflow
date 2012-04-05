/**
 * inputEx RPC utility functions
 * Implements SMD and create forms directly from services
 * @class inputEx.RPC
 * @static
 */
inputEx.RPC = {
   
   /**
    * Build a form to run a service !
    * @param {function} method A method created through inputEx.RPC.Service
    * @param {Object} formOpts
    */
   generateServiceForm: function(method, formOpts, callback) {
   
      var options = null;
      if(YAHOO.lang.isObject(formOpts) && YAHOO.lang.isArray(formOpts.fields) ) {
         options = formOpts;
      }
      // create the form directly from the method params
      else {
         options = inputEx.RPC.formForMethod(method);
      	// Add user options from formOpts
         YAHOO.lang.augmentObject(options, formOpts, true);
      }
   
      // Add buttons to launch the service
      options.type = "form";
      if(!options.buttons) {
         options.buttons = [
            {type: 'submit', value: method.name, onClick: function(e) {
               YAHOO.util.Event.stopEvent(e);
               form.showMask();
               method(form.getValue(), {
                  success: function(results) {
                     form.hideMask();
                     if(YAHOO.lang.isObject(callback) && YAHOO.lang.isFunction(callback.success)) {
               		   callback.success.call(callback.scope || this, results);
               		}
                  },
                  failure: function() {
                     form.hideMask();
                  }
               });
					return false; // do NOT send the browser submit event
            }}
         ];
      }
   
      var form = inputEx(options);
   
      return form;
   },

   /**
    * Return the inputEx form options from a method
    * @param {function} method A method created through inputEx.RPC.Service
    */
   formForMethod: function(method) {
   
      // convert the method parameters into a json-schema :
      var schemaIdentifierMap = {};
      schemaIdentifierMap[method.name] = {
          id: method.name,
          type:'object',
          properties:{}
      };
      for(var i = 0 ; i < method._parameters.length ; i++) {
         var p = method._parameters[i];
         schemaIdentifierMap[method.name].properties[p.name] = p;
      }
   
      // Use the builder to build an inputEx form from the json-schema
      var builder = new inputEx.JsonSchema.Builder({
   	  'schemaIdentifierMap': schemaIdentifierMap,
   	  'defaultOptions':{
   	     'showMsg':true
   	  }
      });
   	var options = builder.schemaToInputEx(schemaIdentifierMap[method.name]);
	
   	return options;
   }
   
};



(function() {
   
   var rpc = inputEx.RPC, lang = YAHOO.lang, util = YAHOO.util;

/**
 * Provide SMD support 
 * http://groups.google.com/group/json-schema/web/service-mapping-description-proposal
 * Not implemented: REST envelope, TCP/IP transport
 * Take a string as a url to retrieve an smd or an object that is an smd or partial smd to use 
 * as a definition for the service
 * @class inputEx.RPC.Service
 * @constructor
 */
inputEx.RPC.Service = function(smd, callback) {

   if( lang.isString(smd) ) {
      this.smdUrl = smd;
      this.fetch(smd, callback);
   }
   else if( lang.isObject(smd) ) {
      this._smd = smd;
      this.process(callback);
   }
   else {
      throw new Error("smd should be an object or an url");
   }
   
};


inputEx.RPC.Service.prototype = {
   
   /**
    * Generate the function from a service definition
    * @method _generateService
    * @param {String} serviceName
    * @param {Method definition} method
    */
   _generateService: function(serviceName, method) {
      
      if(this[method]){
			throw new Error("WARNING: "+ serviceName+ " already exists for service. Unable to generate function");
		}
		method.name = serviceName;
	
		var self = this;
		var func = function(data, opts) {
		   var envelope = rpc.Envelope[method.envelope || self._smd.envelope];
		   var callback = {
   	      success: function(o) {
               var results = envelope.deserialize(o);
      	      opts.success.call(opts.scope || self, results);
   	      },
   	      failure: function(o) {
   	         if(lang.isFunction(opts.failure) ) {
						var results = envelope.deserialize(o);
   	            opts.failure.call(opts.scope || self, results);
   	         }
   	      },
   	      scope: self
   	   };
   	   
   	   
   	   var params = {};
   	   if(self._smd.additionalParameters && lang.isArray(self._smd.parameters) ) {
   	      for(var i = 0 ; i < self._smd.parameters.length ; i++) {
   	         var p = self._smd.parameters[i];
   	         params[p.name] = p["default"];
   	      }
   	   }
   	   lang.augmentObject(params, data, true);
   	   
   	   var url = method.target || self._smd.target;
   	   var urlRegexp = /^(http|https):\/\/[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(([0-9]{1,5})?\/.*)?$/i;
   	   if(!url.match(urlRegexp) && url != self._smd.target) {
   	      url = self._smd.target+url;
   	   }
   	   
	      if( !!this.smdUrl && !url.match(urlRegexp) ) {
   	      // URL is still relative !
   	      var a=this.smdUrl.split('/');
   	      a[a.length-1]="";
   	      url = a.join("/")+url;
   	   }
   	   
   	   
         var r = {
            target: url,
            callback: callback,
            data: params,
            origData: data,
            opts: opts,
            callbackParamName: method.callbackParamName || self._smd.callbackParamName,
            transport: method.transport || self._smd.transport
         };
   	   var serialized = envelope.serialize(self._smd, method, params);
         lang.augmentObject(r, serialized, true);
         
   	   rpc.Transport[r.transport].call(self, r ); 
		};
		
		func.name = serviceName;
		func.description = method.description;
		func._parameters = method.parameters;
		
		return func;
   },
   
   /**
    * Process the SMD definition
    * @method process
    */
   process: function(callback) {
      
      var serviceDefs = this._smd.services;
      
      // Generate the methods to this object
		for(var serviceName in serviceDefs){
		   if( serviceDefs.hasOwnProperty(serviceName) ) {
		      
		      // Get the object that will contain the method.
		      // handles "namespaced" services by breaking apart by '.'
			   var current = this;
			   var pieces = serviceName.split("."); 
			   for(var i=0; i< pieces.length-1; i++){
				   current = current[pieces[i]] || (current[pieces[i]] = {});
			   }
			   
			   current[pieces[pieces.length-1]] =	this._generateService(serviceName, serviceDefs[serviceName]);
		   }
		}
		
		// call the success handler
		if(lang.isObject(callback) && lang.isFunction(callback.success)) {
		   callback.success.call(callback.scope || this);
		}
		
   },
   
   /**
    * Download the SMD at the given url
    * @method fetch
    * @param {String} Absolute or relative url
    */
   fetch: function(url, callback) {
      
      // TODO: if url is not in the same domain, we should use jsonp !
      util.Connect.asyncRequest('GET', url, { 
         success: function(o) {
            try {
               this._smd = lang.JSON.parse(o.responseText);
               this.process(callback);
            }
            catch(ex) {
               if(lang.isObject(console) && lang.isFunction(console.log))
                  console.log(ex);
               if( lang.isFunction(callback.failure) ) {
                  callback.failure.call(callback.scope || this, {error: ex});
               }
            }
         }, 
         failure: function(o) {
            if( lang.isFunction(callback.failure) ) {
               callback.failure.call(callback.scope || this, {error: "unable to fetch url "+url});
            }
         },
         scope: this
      });
   }
   
    
};




inputEx.RPC.Service._requestId = 1;


/**
 * inputEx.RPC.Transport
 * @class inputEx.RPC.Transport
 * @static
 */
inputEx.RPC.Transport = {
   
	/**
	 * Build a ajax request using 'POST' method
	 * @method POST
	 * @param {Object} r Object specifying target, callback and data attributes
	 */
   "POST": function(r) {
      return util.Connect.asyncRequest('POST', r.target, r.callback, r.data );
   },
   
	/**
	 * Build a ajax request using 'GET' method
	 * @method GET
	 * @param {Object} r Object specifying target, callback and data attributes
	 */
   "GET": function(r) {
      return util.Connect.asyncRequest('GET', r.target + (r.data ? '?'+  r.data : ''), r.callback, '');
   },
   
	/**
	 * Build an ajax request using the right HTTP method
	 * @method REST
	 * @param {Object} r Object specifying target, callback and data attributes
	 */
   "REST": function(r) {
      // TODO
   },
   
   jsonp_id: 0,
	/**
	 * Receive data through JSONP (insert a script tag within the page)
	 * @method JSONP
	 * @param {Object} r Object specifying target, callback and data attributes
	 */
   "JSONP": function(r) {
		r.callbackParamName = r.callbackParamName || "callback";
		var fctName = encodeURIComponent("inputEx.RPC.Transport.JSONP.jsonpCallback"+inputEx.RPC.Transport.jsonp_id);
		inputEx.RPC.Transport["JSONP"]["jsonpCallback"+inputEx.RPC.Transport.jsonp_id] = function(results) {
      	if(lang.isObject(r.callback) && lang.isFunction(r.callback.success)) {
      	   r.callback.success.call(r.callback.scope || this, results);
      	}
		};
   	inputEx.RPC.Transport.jsonp_id+=1;
      return util.Get.script( r.target + ((r.target.indexOf("?") == -1) ? '?' : '&') + r.data + "&"+r.callbackParamName+"="+fctName);
   },
   
	/**
	 * NOT implemented
	 * @method TCP/IP
	 */
   "TCP/IP": function(r) {
      throw new Error("TCP/IP transport not implemented !");
   }
   
};


/**
 * inputEx.RPC.Envelope
 * @class inputEx.RPC.Envelope
 * @static
 */
inputEx.RPC.Envelope = {
   
	/**
	 * URL envelope
	 * @class inputEx.RPC.Envelope.URL
	 * @static
	 */
   "URL":  {
	
			/**
			 * Serialize data into URI encoded parameters
			 */
         serialize: function(smd, method, data) {
            var eURI = encodeURIComponent;
            var params = [];
            for(var name in data){
         	   if(data.hasOwnProperty(name)){
            	   var value = data[name];
            		if(lang.isArray(value)){
            			for(var i=0; i < value.length; i++){
            				params.push(eURI(name)+"="+eURI(value[i]));
            			}
            		}else{
            			params.push(eURI(name)+"="+eURI(value));
            		}
            	}
            }
            return {
   				data: params.join("&")
            };   
         },
			/**
			 * Deserialize
			 */
         deserialize: function(results) {
            return results;
         }
   },

   /**
	 * PATH envelope
	 * @class inputEx.RPC.Envelope.PATH
	 * @static
	 */
   "PATH": {
		  /**
		 	* serialize
		   */
        serialize: function(smd, method, data) {
     			var target = method.target || smd.target, i;
     			if(lang.isArray(data)){
     				for(i = 0; i < data.length;i++){
     					target += '/' + data[i];
     				}
     			}else{
     				for(i in data){
     				   if(data.hasOwnProperty(i)) {
     					   target += '/' + i + '/' + data[i];
  					   }
     				}
     			}
           return {
              data: '',
              target: target
           };   
        },
		  /**
		 	* deserialize
		   */
        deserialize: function(results) {
           return results;
        }
    },
    
	/**
	 * JSON envelope
	 * @class inputEx.RPC.Envelope.JSON
	 * @static
	 */
   "JSON": {
		 /**
		  * serialize
		  */
       serialize: function(smd, method, data) {
          return {
             data: lang.JSON.stringify(data)
          };   
       },
 		 /**
		  * deserialize
		  */
       deserialize: function(results) {
          return results;
       }
    },
   
	/**
	 * JSON-RPC-1.0 envelope
	 * @class inputEx.RPC.Envelope.JSON-RPC-1.0
	 * @static
	 */
   "JSON-RPC-1.0":  {
		 /**
		  * serialize
		  */
       serialize: function(smd, method, data) {
          return {
             data: lang.JSON.stringify({
       	      "id": rpc.Service._requestId++,
       	      "method": method.name,
       	      "params": data
       	   })
          };   
       },
	 	 /**
		  * deserialize
		  */
       deserialize: function(results) {
          return lang.JSON.parse(results.responseText);
       }
    },

   /**
	 * JSON-RPC-2.0 envelope
	 * @class inputEx.RPC.Envelope.JSON-RPC-2.0
	 * @static
	 */
   "JSON-RPC-2.0": {
		/**
  	  	 * serialize
		 */
      serialize: function(smd, method, data) {
         return {
            data: lang.JSON.stringify({
      	      "id": rpc.Service._requestId++,
      	      "method": method.name,
      	      "version": "json-rpc-2.0",
      	      "params": data
      	   })
         };   
      },
		/**
 	 	 * serialize
		 */
      deserialize: function(results) {
         return lang.JSON.parse(results.responseText);
      }
   }
   
};

})();
