(function() {
   
   var lang = YAHOO.lang, Dom = YAHOO.util.Dom, Event = YAHOO.util.Event;
   
/**
 * Handle a group of fields
 * @class inputEx.Group
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options The following options are added for Groups and subclasses:
 * <ul>
 *   <li>fields: Array of input fields declared like { label: 'Enter the value:' , type: 'text' or fieldClass: inputEx.Field, optional: true/false, ... }</li>
 *   <li>legend: The legend for the fieldset (default is an empty string)</li>
 *   <li>collapsible: Boolean to make the group collapsible (default is false)</li>
 *   <li>collapsed: If collapsible only, will be collapsed at creation (default is false)</li>
 *   <li>flatten:</li>
 * </ul>
 */
inputEx.Group = function(options) {
   inputEx.Group.superclass.constructor.call(this,options);
   
   // Run default field interactions (if setValue has not been called before)
   if(!this.options.value) {
      this.runFieldsInteractions();
   }
};
lang.extend(inputEx.Group, inputEx.Field, {
   
   /**
    * Adds some options: legend, collapsible, fields...
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
      
      inputEx.Group.superclass.setOptions.call(this, options);
         	
   	this.options.className = options.className || 'inputEx-Group';
   	
   	this.options.fields = options.fields;
   	
   	this.options.flatten = options.flatten;
   
      this.options.legend = options.legend || '';
   
      this.options.collapsible = lang.isUndefined(options.collapsible) ? false : options.collapsible;
      this.options.collapsed = lang.isUndefined(options.collapsed) ? false : options.collapsed;
      
      this.options.disabled = lang.isUndefined(options.disabled) ? false : options.disabled;
      
      // Array containing the list of the field instances
      this.inputs = [];

      // Associative array containing the field instances by names
      this.inputsNames = {};
   },

   /**
    * Render the group
    */
   render: function() {
   
      // Create the div wrapper for this group
	   this.divEl = inputEx.cn('div', {className: this.options.className});
	   if(this.options.id) {
   	   this.divEl.id = this.options.id;
   	}
  	   
  	   this.renderFields(this.divEl);
  	   
  	   if(this.options.disabled) {
  	      this.disable();
  	   }
   },
   
   /**
    * Render all the fields.
    * We use the parentEl so that inputEx.Form can append them to the FORM tag
    */
   renderFields: function(parentEl) {
      
      this.fieldset = inputEx.cn('fieldset');
      this.legend = inputEx.cn('legend', {className: 'inputEx-Group-legend'});
   
      // Option Collapsible
      if(this.options.collapsible) {
         var collapseImg = inputEx.cn('div', {className: 'inputEx-Group-collapseImg'}, null, ' ');
         this.legend.appendChild(collapseImg);
         inputEx.sn(this.fieldset,{className:'inputEx-Expanded'});
      }
   
      if(!lang.isUndefined(this.options.legend) && this.options.legend !== ''){
         this.legend.appendChild( inputEx.cn("span", null, null, " "+this.options.legend) );
      }
   
      if( this.options.collapsible || (!lang.isUndefined(this.options.legend) && this.options.legend !== '') ) {
         this.fieldset.appendChild(this.legend);
      }
  	   
      // Iterate this.createInput on input fields
      for (var i = 0 ; i < this.options.fields.length ; i++) {
         var input = this.options.fields[i];
        
			// Throw Error if input is undefined
			if(!input) {
				throw new Error("inputEx.Form: One of the provided fields is undefined ! (check trailing comma)");
			}
			
         // Render the field
         var field = this.renderField(input);
         this.fieldset.appendChild(field.getEl() );
  	   }
  	
  	   // Collapsed at creation ?
  	   if(this.options.collapsed) {
  	      this.toggleCollapse();
  	   }
  	
  	   // Append the fieldset
  	   parentEl.appendChild(this.fieldset);
   },
  
   /**
    * Instanciate one field given its parameters, type or fieldClass
    * @param {Object} fieldOptions The field properties as required by the inputEx() method
    */
   renderField: function(fieldOptions) {

      // Instanciate the field
      var fieldInstance = inputEx(fieldOptions,this);
      
	   this.inputs.push(fieldInstance);
      
      // Create an index to access fields by their name
      if(fieldInstance.options.name) {
         this.inputsNames[fieldInstance.options.name] = fieldInstance;
      }
      
      // Create the this.hasInteractions to run interactions at startup
      if(!this.hasInteractions && fieldOptions.interactions) {
         this.hasInteractions = true;
      }
      
	   // Subscribe to the field "updated" event to send the group "updated" event
      fieldInstance.updatedEvt.subscribe(this.onChange, this, true);
   	  
      return fieldInstance;
   },
  
   /**
    * Add a listener for the 'collapsible' option
    */
   initEvents: function() {
      if(this.options.collapsible) {
         Event.addListener(this.legend, "click", this.toggleCollapse, this, true);
      }
   },

   /**
    * Toggle the collapse state
    */
   toggleCollapse: function() {
      if(Dom.hasClass(this.fieldset, 'inputEx-Expanded')) {
         Dom.replaceClass(this.fieldset, 'inputEx-Expanded', 'inputEx-Collapsed');
      }
      else {
         Dom.replaceClass(this.fieldset, 'inputEx-Collapsed','inputEx-Expanded');
      }
   },
   
   /**
    * Validate each field
    * @returns {Boolean} true if all fields validate and required fields are not empty
    */
   validate: function() {
      var response = true;

      // Validate all the sub fields
      for (var i = 0; i < this.inputs.length; i++) {
         var input = this.inputs[i];
         if (!input.isDisabled()) {
            input.setClassFromState(); // update field classes (mark invalid fields...)
            var state = input.getState();
            if (state == inputEx.stateRequired || state == inputEx.stateInvalid) {
               response = false; // but keep looping on fields to set classes
            }
         }
      }
      return response;
   },
	
	/**
	 * Alternative method to validate for advanced error handling
	 * @returns {Object} with all Forms's fields state, error message
	 * and validate containing a boolean for the global Form validation
	 */
	getFieldsStates: function() {
		var input, inputName, state, message,
		returnedObj = { fields:{}, validate:true };
      
      // Loop on all the sub fields
      for (var i = 0 ; i < this.inputs.length ; i++) {
	
   	   input = this.inputs[i];
			inputName = input.options.name;
   	   state = input.getState();
			message = input.getStateString(state);
						
			returnedObj.fields[inputName] = {};
			returnedObj.fields[inputName].valid = true;
			returnedObj.fields[inputName].message = message;
			
			// check if subfield validates
   	   if( state == inputEx.stateRequired || state == inputEx.stateInvalid ) {
				returnedObj.fields[inputName].valid = false;
				returnedObj.validate = false;
   	   }

      }

      return returnedObj;
	},
   
   /**
    * Enable all fields in the group
    */
   enable: function() {
 	   for (var i = 0 ; i < this.inputs.length ; i++) {
 	      this.inputs[i].enable();
      }
   },
   
   /**
    * Disable all fields in the group
    */
   disable: function() {
 	   for (var i = 0 ; i < this.inputs.length ; i++) {
 	      this.inputs[i].disable();
      }
   },
   
   /**
    * Set the values of each field from a key/value hash object
     * @param {Any} value The group value
     * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   setValue: function(oValues, sendUpdatedEvt) {
      if(!oValues) {
         return;
      }
	   for (var i = 0 ; i < this.inputs.length ; i++) {
	      var field = this.inputs[i];
	      var name = field.options.name;
	      if(name && !lang.isUndefined(oValues[name]) ) {
	         field.setValue(oValues[name], false); // don't fire the updated event !
	      }
	      else {
	         field.clear(false);
	      }
      }
      
      this.runFieldsInteractions();
      
	   if(sendUpdatedEvt !== false) {
	      // fire update event
         this.fireUpdatedEvt();
      }
   },
   
   /**
    * Return an object with all the values of the fields
    */
   getValue: function() {
	   var o = {};
	   for (var i = 0 ; i < this.inputs.length ; i++) {
	      var v = this.inputs[i].getValue();
	      if(this.inputs[i].options.name) {
	         if(this.inputs[i].options.flatten && lang.isObject(v) ) {
	            lang.augmentObject( o, v);
	         }
	         else {
		         o[this.inputs[i].options.name] = v;
	         }
	      }
      }
	   return o;
   },
  
   /**
    * Close the group (recursively calls "close" on each field, does NOT hide the group )
    * Call this function before hidding the group to close any field popup
    */
   close: function() {
      for (var i = 0 ; i < this.inputs.length ; i++) {
 	      this.inputs[i].close();
      }
   },

   /**
    * Set the focus to the first input in the group
    */
   focus: function() {
      if( this.inputs.length > 0 ) {
         this.inputs[0].focus();
      }
   },

   /**
    * Return the sub-field instance by its name property
    * @param {String} fieldName The name property
    */
   getFieldByName: function(fieldName) {
      if( !this.inputsNames.hasOwnProperty(fieldName) ) {
         return null;
      }
      return this.inputsNames[fieldName];
   },
   
   
   /**
    * Called when one of the group subfields is updated.
    * @param {String} eventName Event name
    * @param {Array} args Array of [fieldValue, fieldInstance] 
    */
   onChange: function(eventName, args) {

      // Run interactions
      var fieldValue = args[0];
      var fieldInstance = args[1];
      this.runInteractions(fieldInstance,fieldValue);
      
      //this.setClassFromState();
      
      this.fireUpdatedEvt();
   },

   /**
    * Run an action (for interactions)
    * @param {Object} action inputEx action object
    * @param {Any} triggerValue The value that triggered the interaction
    */
   runAction: function(action, triggerValue) {
      var field = this.getFieldByName(action.name);
      if( YAHOO.lang.isFunction(field[action.action]) ) {
         field[action.action].call(field);
      }
      else if( YAHOO.lang.isFunction(action.action) ) {
         action.action.call(field, triggerValue);
      }
      else {
         throw new Error("action "+action.action+" is not a valid action for field "+action.name);
      }
   },
   
   /**
    * Run the interactions for the given field instance
    * @param {inputEx.Field} fieldInstance Field that just changed
    * @param {Any} fieldValue Field value
    */
   runInteractions: function(fieldInstance,fieldValue) {
      
      var index = inputEx.indexOf(fieldInstance, this.inputs);
      var fieldConfig = this.options.fields[index];
      if( YAHOO.lang.isUndefined(fieldConfig.interactions) ) return;
      
      // Let's run the interactions !
      var interactions = fieldConfig.interactions;
      for(var i = 0 ; i < interactions.length ; i++) {
         var interaction = interactions[i];
         if(interaction.valueTrigger === fieldValue) {
            for(var j = 0 ; j < interaction.actions.length ; j++) {
               this.runAction(interaction.actions[j], fieldValue);
            }
         }
      }
      
   },
   
   /**
    * Run the interactions for all fields
    */
   runFieldsInteractions: function() {
      if(this.hasInteractions) {
         for(var i = 0 ; i < this.inputs.length ; i++) {
            this.runInteractions(this.inputs[i],this.inputs[i].getValue());
         }
      }
   },
   
	/**
	 * Clear all subfields
	 * @param {boolean} [sendUpdatedEvt] (optional) Wether this clear should fire the updatedEvt or not (default is true, pass false to NOT send the event)
	 */
	clear: function(sendUpdatedEvt) {
	   for(var i = 0 ; i < this.inputs.length ; i++) {
	      this.inputs[i].clear(false);
	   }
	   if(sendUpdatedEvt !== false) {
	      // fire update event
         this.fireUpdatedEvt();
      }
	},
	
	/**
	 * Write error messages for fields as specified in the hash
	 * @param {Object || Array} errors Hash object containing error messages as Strings referenced by the field name, or array [ ["fieldName", "Message"], ...]
	 */
	setErrors: function(errors) {	
		var i,k;
		if(YAHOO.lang.isArray(errors)) {
			for(i = 0 ; i < errors.length ; i++) {
				k = errors[i][0];
				value = errors[i][1];
				if(this.inputsNames[k]) {
					if(this.inputsNames[k].options.showMsg) {
						this.inputsNames[k].displayMessage(value);
						Dom.replaceClass(this.inputsNames[k].divEl, "inputEx-valid", "inputEx-invalid" );
					}
				}
			}
		}
		else if(YAHOO.lang.isObject(errors)) {
			for(k in errors) {
				if(errors.hasOwnProperty(k)) {
					if(this.inputsNames[k]) {
						if(this.inputsNames[k].options.showMsg) {
							this.inputsNames[k].displayMessage(errors[k]);
							Dom.replaceClass(this.inputsNames[k].divEl, "inputEx-valid", "inputEx-invalid" );
						}
					}
				}
			}
		}
	},

   
   /**
    * Purge all event listeners and remove the component from the dom
    */
   destroy: function() {
      
      var i, length, field;
      
      // Recursively destroy inputs
      for (i = 0, length = this.inputs.length ; i < length ; i++) {
         field = this.inputs[i];
         field.destroy();
      }
      
      // Destroy group itself
      inputEx.Group.superclass.destroy.call(this);
      
   }
   
   
});

   
// Register this class as "group" type
inputEx.registerType("group", inputEx.Group, [
   { type: "string", label: "Name", name: "name", value: '' },
   { type: 'string', label: 'Legend', name:'legend'},
   { type: 'boolean', label: 'Collapsible', name:'collapsible', value: false},
   { type: 'boolean', label: 'Collapsed', name:'collapsed', value: false},
   { type: 'list', label: 'Fields', name: 'fields', elementType: {type: 'type' } }
], true);


})();