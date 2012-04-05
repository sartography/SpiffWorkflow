(function() {
   var lang = YAHOO.lang;
 
/**
 * Namespace containing utility functions for conversion between inputEx JSON format and JSON Schema
 *
 * based on "Json Schema Proposal Working Draft":
 * http://groups.google.com/group/json-schema/web/json-schema-proposal-working-draft
 * The proposal is still under discussion and the implementation is very minimalist.
 *
 *
 * TODO:
 *    - we should provide a lot of json schema examples and instances that should/should not validate
 *    - use the $ref (async calls => provide callbacks to methods)
 *    - Inheritance
 *
 * Limitations:
 *    - ??? Please do not trust inputEx: the getValue may return a value which do NOT validate the schema (provide an example ?)
 *    - no tuple typing for arrays
 *    - no "Union type definition"
 *
 * @class inputEx.JsonSchema
 * @static
 */
inputEx.JsonSchema = {
   
   /**
    * Convert the inputEx JSON fields to a JSON schema
    */
   inputExToSchema: function(inputExJson) {
      
      var t = inputExJson.type || "string",
          // inputParams is here for retro-compatibility : TODO -> remove
          // -> ip = inputExJson || {};
          ip = (lang.isObject(inputExJson.inputParams) ? inputExJson.inputParams : inputExJson) || {};
      
      if(t == "group") {
         var ret = {
            type:'object',
            title: ip.legend,
            properties:{
            }
         };
         
         for(var i = 0 ; i < ip.fields.length ; i++) {
            var field = ip.fields[i];
            // inputParams is here for retro-compatibility : TODO -> remove
            // -> var fieldName = field.name;
            var fieldName = lang.isObject(field.inputParams) ? field.inputParams.name : field.name;
            ret.properties[fieldName] = inputEx.JsonSchema.inputExToSchema(field);
         }
         
         return ret;
      }
      else if(t == "number") {
         return {
    			'type':'number',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label
    		};
      }
      else if(t == "string") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label
    		};
      }
      else if(t == "text") {
         return {
 			   'type':'string',
			   'format':'text',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
				'_inputex':{
					'rows':5,
					'cols':50
				}
    		};
      }
      else if(t == "html") {
         return {
 			   'type':'string',
			   'format':'html',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
				'_inputex':{
					
				}
    		};
      }
      else if(t == "list") {
         return {
 			   'type':'array',
    			'title': ip.label,
    			'items': inputEx.JsonSchema.inputExToSchema(ip.elementType),
				'_inputex':{
				}
    		};
      }
      else if(t == "email") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'email'
    		};
      }
      else if(t == "url") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'url'
    		};
      }
      else if(t == "time") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'time'
    		};
      }
      else if(t == "IPv4") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'ip-address'
    		};
      }
      else if(t == "color") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'color'
    		};
      }
      else if(t == "date") {
         return {
    			'type':'string',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'format':'date'
    		};
      }
      else if(t == "multiselect" || t == "multiautocomplete"){
        return {
    			'type':'array',
    			'optional': typeof ip.required == "undefined" ? true : !ip.required,
    			'title': ip.label,
    			'items': typeof ip.jsonSchemaRef == "undefined" ? {"type":"string"}: ip.jsonSchemaRef,// it's a little bit weird to mix a inputEx description field and jsonSchema in a specific attribute, we should had a $ref system to go through this properly
    			'_inputex': ip
    		};
      }
      else {
			return {
				'type': 'string',
				'title': ip.label,
				'optional': typeof ip.required == "undefined" ? true : !ip.required,
				'_inputex': ip
			};
      }
      
   }

};


/**
 * @class inputEx.JsonSchema.Builder
 */
inputEx.JsonSchema.Builder = function(opts) {
	
	var options = opts || {};
	this.options  = options; 
	
	/**
	 * specify how other schema properties are mapped to inputParam properties
	 */
	this.schemaToParamMap = options.schemaToParamMap || {
		'title':'label',
		'description':'description',
		'_inputex':null	// null value means copy child key/value pairs into field options directly
	};
	
	/**
	 * @property referenceResolver
	 */
	this.referenceResolver = options.referenceResolver || null;
	
	/**
	 * options to be applied unless already specified
	 * @property defaultOptions
	 */
	this.defaultOptions = options.defaultOptions || {};	
	
	/**
	 * key is reference, value is schema
	 * @property schemaIdentifierMap
	 */
	this.schemaIdentifierMap = options.schemaIdentifierMap || {};
};

inputEx.JsonSchema.Builder.prototype = {
   
   /** 
 	 * return a schema based on the reference value default is to look up in map
    */
	defaultReferenceResolver:function(reference) {
		return this.schemaIdentifierMap[reference] || null;
	},
	
	/**
	 * Convert a JSON schema to inputEx JSON
	 * @param {JSONSchema} p
	 */
	schemaToInputEx:function(p, propertyName) {
	
	   var fieldDef = { label: propertyName, name: propertyName };
	   var schemaMap = this.schemaToParamMap;
    	var referencedSchema = p["$ref"];
		var key;
	    
	   if(referencedSchema){
	    	var new_schema = null;
	    	if(this.referenceResolver) {
		       new_schema = this.referenceResolver(referencedSchema);
		    }
	    	if(new_schema === null) {
	    		new_schema = this.defaultReferenceResolver(referencedSchema);
	    	}
	    	if(new_schema === null) {
	    		throw new Error('Schema for property : "'+propertyName+'" $references "'+referencedSchema+'", not found');
	    	}
	    	// copy options into new schema, for example we can overide presentation
	    	// of a defined schema depending on where it is used
	    	new_schema = lang.merge(new_schema);	// copy new_schema
	    	
	    	for(var pk in p) {
	    		if(p.hasOwnProperty(pk) && lang.isUndefined(new_schema[pk]) && pk != '$ref') {
	    			new_schema[pk] = p[pk];
	    		}
	    	}
	    	p = new_schema;
	   }

	   if(!p.optional) {
	      fieldDef.required = true;
	   }

	    for(key in schemaMap) {
	        if(schemaMap.hasOwnProperty(key)) {
	      	  var paramName = schemaMap[key]; 
	      	  var v = p[key];
	      	  if(!lang.isUndefined(v)) {
	      		  if(paramName === null) {
	      			  // copy / merge values from v directly into options
	      			  if(lang.isObject(v)) {
	      				  // v must be an object, copy key/value pairs into options
	      				  for(var vkey in v) {
	      					  if(v.hasOwnProperty(vkey)) {
	      						  fieldDef[vkey] = v[vkey];
	      					  }
	      				  }
	      			  }
	      		  } else {
	      			  fieldDef[paramName] = v;
	      		  }
	      	  }
	        }
	    }
	    if(!p.type) p.type = 'object';
	    var type = p.type;
	       
	       // If type is a "Union type definition", we'll use the first type for the field
	       // "array" <=>  [] <=> ["any"]
	       if(lang.isArray(type)) {
	          if(type.length === 0 || (type.length == 1 && type[0] == "any") ) {
	             type = "array";
	          }
	          else {
	             type = type[0];
	          }
	       }
	       //else if(lang.isObject(type) ) {
	          // What do we do ??
	          //console.log("type is an object !!");
	       //}
	       
	       fieldDef.type = type;
	       
	       // default value
	       if( !lang.isUndefined(p["default"]) ) {
	          fieldDef.value = p["default"];
	       }
	    
	       if(type == "array" ) {
	          fieldDef.type = "list";
	          if(lang.isObject(p.items) && !lang.isArray(p.items)) {
	        	  // when items is an object, it's a schema that describes each item in the list
	        	  fieldDef.elementType = this.schemaToInputEx(p.items, propertyName);
	          }
	
		       if(p.minItems) { fieldDef.minItems = p.minItems; }
				 if(p.maxItems) { fieldDef.maxItems = p.maxItems; }
	
	       }
	       else if(type == "object" ) {
	          fieldDef.type = "group";
	          if(p.title && lang.isUndefined(fieldDef.legend)) {
	        	  fieldDef.legend = p.title; 
	          }
	          //fieldDef = this.schemaToInputEx(p, propertyName);
	          //fieldDef = this._parseSchemaProperty(p, propertyName);
	          var fields = [];
	          if(propertyName) {
	        	  fieldDef.name = propertyName;
	          }
	
	          for(key in p.properties) {
	             if(p.properties.hasOwnProperty(key)) {
	                fields.push( this.schemaToInputEx(p.properties[key], key) );
	             }
	          }
	
	          fieldDef.fields = fields;
	          
	       }
	       else if(type == "string" && (p["enum"] || p["choices"]) ) {
	          fieldDef.type = "select";
	          
	          if(p.choices) {
	             fieldDef.choices = [];
	             for(var i = 0 ; i < p.choices.length ; i++) {
	                var o = p.choices[i];
	                fieldDef.choices[i] = { label: o.label, value: o.value };
	             }
             }
             else {
	             fieldDef.choices = [];
	             for(var i = 0 ; i < p["enum"].length ; i++) {
	                var o = p["enum"][i];
	                fieldDef.choices[i] = { label: o.label, value: o.value };
	             }
             }
	       }
	       else if(type == "string") {
	    	  if(!lang.isUndefined(p.pattern) && lang.isUndefined(fieldDef.regexp)) {
	    		  if(lang.isString(p.pattern)) {
	    			  fieldDef.regexp = new RegExp(p.pattern);
	    		  } else {
	    			  fieldDef.regexp = p.pattern;
	    		  }
	    	  }
	    	  if(!lang.isUndefined(p.maxLength) && lang.isUndefined(fieldDef.maxLength)) {
	    		  fieldDef.maxLength = p.maxLength; 
	    	  }

	    	  if(!lang.isUndefined(p.minLength) && lang.isUndefined(fieldDef.minLength)) {
	    		  fieldDef.minLength = p.minLength; 
	    	  }

	    	  if(!lang.isUndefined(p.readonly) && lang.isUndefined(fieldDef.readonly)) {
	    		  fieldDef.readonly = p.readonly; 
	    	  }

           // According to http://groups.google.com/group/json-schema/web/json-schema-possible-formats
	          if( p.format ) {
	             if(p.format == "html") {
	                fieldDef.type = "html";
	             } else if(p.format == "date") {
	                fieldDef.type = "date";
	                fieldDef.tooltipIcon = true;
	             } else if(p.format == 'url') {
	            	 fieldDef.type = 'url';
	             } else if(p.format == 'email') {
	            	 fieldDef.type = 'email';
	             } else if(p.format == 'text') {
	            	 fieldDef.type = 'text';
	             } else if(p.format == 'time') {
	                fieldDef.type = 'time';
	             } else if(p.format == 'ip-address') {
    	             fieldDef.type = 'IPv4';
    	          } else if(p.format == 'color') {
    	             fieldDef.type = 'color';
    	          }
	          }
	       }
	
			 // Override inputEx's type with the "_type" attribute
			 if( !!p["_inputex"] && !!p["_inputex"]["_type"]) {
				fieldDef.type = p["_inputex"]["_type"];
			 }
	
	    // Add the defaultOptions
	    for(var kk in this.defaultOptions) {
	        if(this.defaultOptions.hasOwnProperty(kk) && lang.isUndefined(fieldDef[kk])) {
	        	fieldDef[kk] = this.defaultOptions[kk]; 
	        }	    	
	    }
	    return fieldDef;
	},

   /**
    * Create an inputEx Json form definition from a json schema instance object
    * Respect the "Self-Defined Schema Convention"
    */
   formFromInstance: function(instanceObject) {
      if(!instanceObject || !instanceObject["$schema"]) {
         throw new Error("Invalid json schema instance object. Object must have a '$schema' property.");
      }
      
      var formDef = this.schemaToInputEx(instanceObject["$schema"]);
      
      // Set the default value of each property to the instance value
      for(var i = 0 ; i < formDef.fields.length ; i++) {
         var fieldName = formDef.fields[i].name;
         formDef.fields[i].value = instanceObject[fieldName];
      }
      
      return formDef;
   }
   
};




})();
