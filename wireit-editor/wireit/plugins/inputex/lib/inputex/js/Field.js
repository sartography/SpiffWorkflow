(function() {
   var Dom = YAHOO.util.Dom, lang = YAHOO.lang, util = YAHOO.util;

/** 
 * An abstract class (never instantiated) that contains the shared features for all fields.
 * @class inputEx.Field
 * @constructor
 * @param {Object} options Configuration object
 * <ul>
 *	  <li>name: the name of the field</li>
 *	  <li>required: boolean, the field cannot be null if true</li>
 *   <li>className: CSS class name for the div wrapper (default 'inputEx-Field')</li>
 *   <li>value: initial value</li>
 *   <li>parentEl: HTMLElement or String id, append the field to this DOM element</li>
 * </ul>
 */
inputEx.Field = function(options) {
	
	// Set the default values of the options
	this.setOptions(options || {});
	
	// Call the render of the dom
	this.render();
	
	/**
	 * Event fired after the user changed the value of the field.
	 * @event updatedEvt
	 * @param {Any} value The new value of the field
	 * @desc YAHOO custom event fired when the field is "updated"<br /> subscribe with: this.updatedEvt.subscribe(function(e, params) { var value = params[0]; console.log("updated",value, this.updatedEvt); }, this, true);
	 */
	this.updatedEvt = new util.CustomEvent('updated', this);
	
	// initialize behaviour events
	this.initEvents();
	
	// Set the initial value
	//   -> no initial value = no style (setClassFromState called by setValue)
	if(!lang.isUndefined(this.options.value)) {
		this.setValue(this.options.value, false);
	}
	
	// append it immediatly to the parent DOM element
	if(options.parentEl) {
	   if( lang.isString(options.parentEl) ) {
	     Dom.get(options.parentEl).appendChild(this.getEl());  
	   }
	   else {
	      options.parentEl.appendChild(this.getEl());
      }
	}
};


inputEx.Field.prototype = {
  
   /**
    * Set the default values of the options
    * @param {Object} options Options object as passed to the constructor
    */
	setOptions: function(options) {

   	/**
   	 * Configuration object to set the options for this class and the parent classes. See constructor details for options added by this class.
   	 */
   	this.options = {};
   	
   	// Basic options
   	this.options.name = options.name;
   	this.options.value = options.value;
   	this.options.id = options.id || Dom.generateId();
   	this.options.label = options.label;
   	this.options.description = options.description;
   
      // Define default messages
	   this.options.messages = {};
	   this.options.messages.required = (options.messages && options.messages.required) ? options.messages.required : inputEx.messages.required;
	   this.options.messages.invalid = (options.messages && options.messages.invalid) ? options.messages.invalid : inputEx.messages.invalid;
	   //this.options.messages.valid = (options.messages && options.messages.valid) ? options.messages.valid : inputEx.messages.valid;
	
	   // Other options
	   this.options.className = options.className ? options.className : 'inputEx-Field';
	   this.options.required = lang.isUndefined(options.required) ? false : options.required;
	   this.options.showMsg = lang.isUndefined(options.showMsg) ? false : options.showMsg;
	},
	
	
	/**
	 * Set the name of the field (or hidden field)
	 */
	setFieldName: function(name) {
	},

   /**
    * Default render of the dom element. Create a divEl that wraps the field.
    */
	render: function() {
	
	   // Create a DIV element to wrap the editing el and the image
	   this.divEl = inputEx.cn('div', {className: 'inputEx-fieldWrapper'});
	   if(this.options.id) {
	      this.divEl.id = this.options.id;
	   }
	   if(this.options.required) {
	      Dom.addClass(this.divEl, "inputEx-required");
	   }
	   
	   // Label element
	   if(this.options.label) {
	      this.labelDiv = inputEx.cn('div', {id: this.divEl.id+'-label', className: 'inputEx-label', 'for': this.divEl.id+'-field'});
	      this.labelEl = inputEx.cn('label');
	      this.labelEl.appendChild( document.createTextNode(this.options.label) );
	      this.labelDiv.appendChild(this.labelEl);
	      this.divEl.appendChild(this.labelDiv);
      }
      
      this.fieldContainer = inputEx.cn('div', {className: this.options.className}); // for wrapping the field and description
	
      // Render the component directly
      this.renderComponent();
      
      // Description
      if(this.options.description) {
         this.fieldContainer.appendChild(inputEx.cn('div', {id: this.divEl.id+'-desc', className: 'inputEx-description'}, null, this.options.description));
      }
      
   	this.divEl.appendChild(this.fieldContainer);
      
	   // Insert a float breaker
	   this.divEl.appendChild( inputEx.cn('div',null, {clear: 'both'}," ") );
	
	},
	
	/**
	 * Fire the "updated" event (only if the field validated)
	 * Escape the stack using a setTimeout
	 */
	fireUpdatedEvt: function() {
      // Uses setTimeout to escape the stack (that originiated in an event)
      var that = this;
      setTimeout(function() {
         that.updatedEvt.fire(that.getValue(), that);
      },50);
	},

   /**
    * Render the interface component into this.divEl
    */
	renderComponent: function() {
 	   // override me
	},

   /**
    * The default render creates a div to put in the messages
    * @return {HTMLElement} divEl The main DIV wrapper
    */
	getEl: function() {
	   return this.divEl;
	},

   /**
    * Initialize events of the Input
    */
	initEvents: function() {
 	   // override me
	},

   /**
    * Return the value of the input
    * @return {Any} value of the field
    */
	getValue: function() { 
	   // override me
	},

   /**
    * Function to set the value
    * @param {Any} value The new value
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
	setValue: function(value, sendUpdatedEvt) {
	   // to be inherited
	   
	   // set corresponding style
	   this.setClassFromState();
	   
	   if(sendUpdatedEvt !== false) {
	      // fire update event
         this.fireUpdatedEvt();
      }
	},

   /**
    * Set the styles for valid/invalide state
    */
	setClassFromState: function() {
		var className;
	   // remove previous class
	   if( this.previousState ) {
	      // remove invalid className for both required and invalid fields
	      className = 'inputEx-'+((this.previousState == inputEx.stateRequired) ? inputEx.stateInvalid : this.previousState);
		   Dom.removeClass(this.divEl, className);
	   }
	   
	   // add new class
	   var state = this.getState();
	   if( !(state == inputEx.stateEmpty && Dom.hasClass(this.divEl, 'inputEx-focused') ) ) {
	      // add invalid className for both required and invalid fields
	      className = 'inputEx-'+((state == inputEx.stateRequired) ? inputEx.stateInvalid : state);
	      Dom.addClass(this.divEl, className );
      }
	
	   if(this.options.showMsg) {
	      this.displayMessage( this.getStateString(state) );
      }
	   
	   this.previousState = state;
	},

   /**
    * Get the string for the given state
    */
	getStateString: function(state) {
      if(state == inputEx.stateRequired) {
         return this.options.messages.required;
      }
      else if(state == inputEx.stateInvalid) {
         return this.options.messages.invalid;
      }
      else {
         return '';
      }
	},

   /**
    * Returns the current state (given its value)
    * @return {String} One of the following states: 'empty', 'required', 'valid' or 'invalid'
    */
	getState: function() { 
	   // if the field is empty :
	   if( this.isEmpty() ) {
	      return this.options.required ? inputEx.stateRequired : inputEx.stateEmpty;
	   }
	   return this.validate() ? inputEx.stateValid : inputEx.stateInvalid;
	},

   /**
    * Validation of the field
    * @return {Boolean} field validation status (true/false)
    */
	validate: function() {
      return true;
   },

   /**
    * Function called on the focus event
    * @param {Event} e The original 'focus' event
    */
	onFocus: function(e) {
	   var el = this.getEl();
	   Dom.removeClass(el, 'inputEx-empty');
	   Dom.addClass(el, 'inputEx-focused');
	},

   /**
    * Function called on the blur event
    * @param {Event} e The original 'blur' event
    */
	onBlur: function(e) {
	   Dom.removeClass(this.getEl(), 'inputEx-focused');
	   
	   // Call setClassFromState on Blur
	   this.setClassFromState();
	},

   /**
    * onChange event handler
    * @param {Event} e The original 'change' event
    */
	onChange: function(e) {
      this.fireUpdatedEvt();
	},

   /**
    * Close the field and eventually opened popups...
    */
	close: function() {
	},

   /**
    * Disable the field
    */
	disable: function() {
	},

   /**
    * Enable the field
    */
	enable: function() {
	},

   /**
    * Check if the field is diabled
    */
   isDisabled: function() {
      return false;
   },

   /**
    * Focus the field
    */
   focus: function() {
   },
   
   /**
    * Purge all event listeners and remove the component from the dom
    */
   destroy: function() {
      var el = this.getEl();
      
      // Unsubscribe all listeners on the updatedEvt
      this.updatedEvt.unsubscribeAll();
      
      // Purge element (remove listeners on el and childNodes recursively)
      util.Event.purgeElement(el, true);
      
      // Remove from DOM
      if(Dom.inDocument(el)) {
         el.parentNode.removeChild(el);
      }
      
   },
   
   /**
    * Update the message 
    * @param {String} msg Message to display
    */
   displayMessage: function(msg) {
      if(!this.fieldContainer) { return; }
      if(!this.msgEl) {
         this.msgEl = inputEx.cn('div', {className: 'inputEx-message'});
          try{
             var divElements = this.divEl.getElementsByTagName('div');
             this.divEl.insertBefore(this.msgEl, divElements[(divElements.length-1>=0)?divElements.length-1:0]); //insertBefore the clear:both div
          }catch(e){alert(e);}
      }
      this.msgEl.innerHTML = msg;
   },

   /**
    * Show the field
    */
   show: function() {
      this.divEl.style.display = '';
   },
   
   /**
    * Hide the field
    */
   hide: function() {
      this.divEl.style.display = 'none';
   },
   
   /**
    * Clear the field by setting the field value to this.options.value
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this clear should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   clear: function(sendUpdatedEvt) {
      this.setValue(lang.isUndefined(this.options.value) ? '' : this.options.value, sendUpdatedEvt);
   },
   
   /**
    * Should return true if empty
    */
   isEmpty: function() {
      return this.getValue() === '';
   },

	/**
	 * Set the parentField.
	 * Generally use by composable fields (ie. Group,Form,ListField,CombineField,...}
	 * @param {inputEx.Group|inputEx.Form|inputEx.ListField|inputEx.CombineField} parentField The parent field instance
	 */
	setParentField: function(parentField) {
		this.parentField = parentField;
	},
	
	/**
	 * Return the parent field instance
	 * @return {inputEx.Group|inputEx.Form|inputEx.ListField|inputEx.CombineField}
	 */
	getParentField: function() {
		return this.parentField;
	}
   
};

inputEx.Field.groupOptions = [
   { type: "string", label: "Label", name: "label", value: '' },
   { type: "string", label: "Name", name: "name", value: '' },
   { type: "string", label: "Description",name: "description", value: '' },
   { type: "boolean", label: "Required?",name: "required", value: false },
   { type: "boolean", label: "Show messages",name: "showMsg", value: false }
];

})();