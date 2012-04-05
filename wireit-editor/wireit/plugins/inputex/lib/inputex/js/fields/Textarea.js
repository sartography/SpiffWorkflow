(function() {

   var Event = YAHOO.util.Event;

/**
 * Create a textarea input
 * @class inputEx.Textarea
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *	   <li>rows: rows attribute</li>
 *	   <li>cols: cols attribute</li>
 * </ul>
 */
inputEx.Textarea = function(options) {
	inputEx.Textarea.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.Textarea, inputEx.StringField, {

   /**
    * Set the specific options (rows and cols)
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
      inputEx.Textarea.superclass.setOptions.call(this, options);
      this.options.rows = options.rows || 6;
      this.options.cols = options.cols || 23;
      
      // warning : readonly option doesn't work on IE < 8
      this.options.readonly = !!options.readonly;
   },
   
   /**
    * Render an 'INPUT' DOM node
    */
   renderComponent: function() {
      
      // This element wraps the input node in a float: none div
      this.wrapEl = inputEx.cn('div', {className: 'inputEx-StringField-wrapper'});
      
      // Attributes of the input field
      var attributes = {};
      attributes.id = this.divEl.id?this.divEl.id+'-field':YAHOO.util.Dom.generateId();
      attributes.rows = this.options.rows;
      attributes.cols = this.options.cols;
      if(this.options.name) attributes.name = this.options.name;
      if(this.options.readonly) attributes.readonly = 'readonly';
      
      //if(this.options.maxLength) attributes.maxLength = this.options.maxLength;
   
      // Create the node
      this.el = inputEx.cn('textarea', attributes, null, this.options.value);
      
      // Append it to the main element
      this.wrapEl.appendChild(this.el);
      this.fieldContainer.appendChild(this.wrapEl);
   },
   
	/**
    * Uses the optional regexp to validate the field value
    */
   validate: function() { 
      var previous = inputEx.Textarea.superclass.validate.call(this);
      
      // emulate maxLength property for textarea
      //   -> user can still type but field is invalid
      if (this.options.maxLength) {
         previous = previous && this.getValue().length <= this.options.maxLength;
      }
      
      return previous;
   },
   
   /**
    * Add the minLength string message handling
    */
    getStateString: function(state) {
	   if(state == inputEx.stateInvalid && this.options.minLength && this.el.value.length < this.options.minLength) {  
	      return inputEx.messages.stringTooShort[0]+this.options.minLength+inputEx.messages.stringTooShort[1];
	   
	   // Add message too long
      } else if (state == inputEx.stateInvalid && this.options.maxLength && this.el.value.length > this.options.maxLength) {
         return inputEx.messages.stringTooLong[0]+this.options.maxLength+inputEx.messages.stringTooLong[1];
      }
	   return inputEx.Textarea.superclass.getStateString.call(this, state);
	},
	
	
	/**
	 * Insert text at the current cursor position
	 * @param {String} text Text to insert
	 */
	insert: function(text) {
		
		var sel, startPos, endPos;
		
		//IE support
		if (document.selection) {
			this.el.focus();
			sel = document.selection.createRange();
			sel.text = text;
		}
		//Mozilla/Firefox/Netscape 7+ support
		else if (this.el.selectionStart || this.el.selectionStart == '0') {
			startPos = this.el.selectionStart;
			endPos = this.el.selectionEnd;
			this.el.value = this.el.value.substring(0, startPos)+ text+ this.el.value.substring(endPos, this.el.value.length);
		} 
		else {
			this.el.value += text;
		}	
	}

});

inputEx.messages.stringTooLong = ["This field should contain at most "," numbers or characters"];

// Register this class as "text" type
inputEx.registerType("text", inputEx.Textarea, [
   { type: 'integer', label: 'Rows',  name: 'rows', value: 6 },
   { type: 'integer', label: 'Cols', name: 'cols', value: 23 }
]);

})();