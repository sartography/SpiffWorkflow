/**
 * The inputEx Library
 * @module inputEx
 */
/*global inputEx: false, YAHOO: false */
(function() {
 
 var lang = YAHOO.lang;
 
/**
 * The inputEx method lets you create a field from the JSON definition:
 * <pre>
 *    inputEx({type: 'string', name: 'company', label: 'Your company' })
 * </pre>
 * Build a field from an object like: { type: 'color' or fieldClass: inputEx.ColorField, ... }<br />
 * If the neither type or fieldClass are found, it uses inputEx.StringField
 *
 * @class inputEx
 * @static
 * @param {Object} fieldOptions
 * @param {inputEx.Group|inputEx.Form|inputEx.ListField|inputEx.CombineField} (optional) parentField The parent field instance
 * @return {inputEx.Field} Created field instance
 */
inputEx = function(fieldOptions, parentField) {
   var fieldClass = null,
       inputInstance;
   
	if(fieldOptions.type) {
	   fieldClass = inputEx.getFieldClass(fieldOptions.type);
	   if(fieldClass === null) fieldClass = inputEx.StringField;
	}
	else {
	   fieldClass = fieldOptions.fieldClass ? fieldOptions.fieldClass : inputEx.StringField;
	}

   // Instanciate the field
   
   // Retro-compatibility with deprecated inputParams Object
   if (lang.isObject(fieldOptions.inputParams)) {
      inputInstance = new fieldClass(fieldOptions.inputParams);
      
   // New prefered way to instanciate a field
   } else {
      inputInstance = new fieldClass(fieldOptions);
   }

	// If the parentField argument is provided
	if(parentField) {
		inputInstance.setParentField(parentField);
	}

   // Add the flatten attribute if present in the params
   /*if(fieldOptions.flatten) {
      inputInstance._flatten = true;
   }*/
	  
   return inputInstance;
};

lang.augmentObject(inputEx, {
   
   VERSION: "0.5.0",
   
   /**
    * Url to the spacer image. This url schould be changed according to your project directories
    * @type String
    */
   spacerUrl: "images/space.gif", // 1x1 px
   
   /**
    * Field empty state constant
    * @type String
    */
   stateEmpty: 'empty',
   
   /**
    * Field required state constant
    * @type String
    */
   stateRequired: 'required',
   
   /**
    * Field valid state constant
    * @type String
    */
   stateValid: 'valid',
   
   /**
    * Field invalid state constant
    * @type String
    */
   stateInvalid: 'invalid',
   
   /**
    * Associative array containing field messages
    */
	messages: {
		required: "This field is required",
		invalid: "This field is invalid",
		valid: "This field is valid",
		defaultDateFormat: "m/d/Y",
		months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
		timeUnits: { SECOND: "seconds", MINUTE: "minutes", HOUR: "hours", DAY: "days", MONTH: "months", YEAR: "years" }
	},
   
   /**
    * inputEx widget namespace
    * @static 
    */
   widget: {},
   
   /**
    * inputEx mixin namespace
    * @static 
    */
   mixin: {},
   
   /**
    * Associative array containing common regular expressions
    */
   regexps: {
      email: /^[a-z0-9!\#\$%&'\*\-\/=\?\+\-\^_`\{\|\}~]+(?:\.[a-z0-9!\#\$%&'\*\-\/=\?\+\-\^_`\{\|\}~]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,6}$/i,
      url: /^(http|https):\/\/[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(\:[0-9]{1,5})?(([0-9]{1,5})?\/.*)?$/i,
      password: /^[0-9a-zA-Z\x20-\x7E]*$/
   },
   
   /**
    * Hash between inputEx types and classes (ex: <code>inputEx.typeClasses.color = inputEx.ColorField</code>)<br />
    * Please register the types with the <code>registerType</code> method
    */
   typeClasses: {},
   
   /**
    * Property to globally turn on/off the browser autocompletion
    * (used as default autocomplete option value by StringField, Form and their subclasses)
    */
   browserAutocomplete: true,
   
   /**
    * When you create a new inputEx Field Class, you can register it to give it a simple type.
    * ex:   inputEx.registerType("color", inputEx.ColorField);
    * @static
    * @param {String} type String used as the inputEx field type
    * @param {Class} fieldClass Field Class to register as this type
	 * @param {Array} groupOptions List of inputEx field description for each option
	 * @param {Boolean} dontInherit Won't inherhit the parent field properties if set to true
    */
   registerType: function(type, fieldClass, groupOptions, dontInherit) {
      if(!lang.isString(type)) {
         throw new Error("inputEx.registerType: first argument must be a string");
      }
      if(!lang.isFunction(fieldClass)) {
         throw new Error("inputEx.registerType: second argument must be a function");
      }
      this.typeClasses[type] = fieldClass;
      
      // Setup the groupOptions property on the class
      var opts = [];
      if(lang.isArray(groupOptions)) { opts = groupOptions; }
      if(fieldClass.superclass && !dontInherit && lang.isArray(fieldClass.superclass.constructor.groupOptions) ) {
         opts = opts.concat(fieldClass.superclass.constructor.groupOptions);
      }
      fieldClass.groupOptions = opts;
   },
   
   /**
    * Returns the class for the given type
    * ex: inputEx.getFieldClass("color") returns inputEx.ColorField
    * @static
    * @param {String} type String type of the field
    */
   getFieldClass: function(type) {
      return lang.isFunction(this.typeClasses[type]) ? this.typeClasses[type] : null;
   },
   
   /**
    * Get the inputex type for the given class (ex: <code>inputEx.getType(inputEx.ColorField)</code> returns "color")
    * @static
    * @param {inputEx.Field} FieldClass An inputEx.Field or derivated class
    * @return {String} returns the inputEx type string or <code>null</code>
    */
   getType: function(FieldClass) {
      for(var type in this.typeClasses) {
         if(this.typeClasses.hasOwnProperty(type) ) {
            if(this.typeClasses[type] == FieldClass) {
               return type;
            }
         }
      }
      return null;
   },
   
   /**
    * @deprecated Kept for backward compatibility (alias for inputEx() )
    * @param {Object} fieldOptions
    * @return {inputEx.Field} Created field instance
    */
   buildField: function(fieldOptions) {      
      return inputEx(fieldOptions);
   },
   
   /**
    * Helper function to set DOM node attributes and style attributes.
    * @static
    * @param {HTMLElement} el The element to set attributes to
    * @param {Object} domAttributes An object containing key/value pairs to set as node attributes (ex: {id: 'myElement', className: 'myCssClass', ...})
    * @param {Object} styleAttributes Same thing for style attributes. Please use camelCase for style attributes (ex: backgroundColor for 'background-color')
    */
   sn: function(el,domAttributes,styleAttributes){
      if(!el) { return; }
		var i;
      if(domAttributes){
         for(i in domAttributes){
            var domAttribute = domAttributes[i];
            if( lang.isFunction(domAttribute) ){
               continue;
            }
            if(i=="className"){
               i="class";
               el.className=domAttribute;
            }
            if(domAttribute!==el.getAttribute(i)){
               try{
                  if(domAttribute===false){
                     el.removeAttribute(i);
                  }else{
                     el.setAttribute(i,domAttribute);
                  }
               }
               catch(err){
                  //console.log("WARNING: WireIt.sn failed for "+el.tagName+", attr "+i+", val "+domAttribute);
               }
            }
         }
      }

      if(styleAttributes){
         for(i in styleAttributes){
            if( lang.isFunction(styleAttributes[i]) ){
               continue;
            }
            if(el.style[i]!=styleAttributes[i]){
               el.style[i]=styleAttributes[i];
            }
         }
      }
   },


   /**
    * Helper function to create a DOM node. (wrapps the document.createElement tag and the inputEx.sn functions)
    * @static
    * @param {String} tag The tagName to create (ex: 'div', 'a', ...)
    * @param {Object} [domAttributes] see inputEx.sn
    * @param {Object} [styleAttributes] see inputEx.sn
    * @param {String} [innerHTML] The html string to append into the created element
    * @return {HTMLElement} The created node
    */
   cn: function(tag, domAttributes, styleAttributes, innerHTML) {
        if (tag == 'input' && YAHOO.env.ua.ie) { //only limit to input tag that has no tag body
            var strDom = '<' + tag;
            if (domAttributes!=='undefined'){
                for (var k in domAttributes){
                    strDom += ' ' + (k === "className" ? "class" : k) + '="' + domAttributes[k] + '"';
                }
            }
            strDom += '/' + '>';
            return document.createElement(strDom);

        } else {
            var el = document.createElement(tag);
            this.sn(el, domAttributes, styleAttributes);
            if (innerHTML) {
                el.innerHTML = innerHTML;
            }
            return el;
        }
    },
   
   
   /**
    * Find the position of the given element. (This method is not available in IE 6)
    * @static
    * @param {Object} el Value to search
    * @param {Array} arr The array to search
    * @param {Function} (optional) fn A function to define another way to test inclusion of el than === (returns a boolean)
    * @return {number} Element position, -1 if not found
    */
	indexOf: function(el,arr,fn) {
	
		var l=arr.length,i;
		
		if ( !lang.isFunction(fn) ) { fn = function(elt,arrElt) { return elt === arrElt; }; }
		
		for ( i = 0 ;i < l ; i++ ) {
			if ( fn.call({}, el, arr[i]) ) { return i; }
		}
		
		return -1;
	},

   
   /**
    * Create a new array without the null or undefined values
    * @static
    * @param {Array} arr The array to compact
    * @return {Array} The new array
    */
   compactArray: function(arr) {
      var n = [], l=arr.length,i;
      for(i = 0 ; i < l ; i++) {
         if( !lang.isNull(arr[i]) && !lang.isUndefined(arr[i]) ) {
            n.push(arr[i]);
         }
      }
      return n;
   },

	/**
	 * Return a string without accent (only on lowercase)
	 * @static
	 * @param {String} str The string
	 * @return {String} String without accent
	 */
	removeAccents: function (str) {
	   return str.replace(/[àáâãäå]/g,"a").
					  replace(/[èéêë]/g,"e").
					  replace(/[ìíîï]/g,"i").
					  replace(/[òóôõö]/g,"o").
					  replace(/[ùúûü]/g,"u").
					  replace(/[ýÿ]/g,"y").
					  replace(/[ñ]/g,"n").
					  replace(/[ç]/g,"c").
					  replace(/[œ]/g,"oe").
					  replace(/[æ]/g,"ae");
	}
   
});

})();


// The main inputEx namespace shortcut
YAHOO.inputEx = inputEx;
