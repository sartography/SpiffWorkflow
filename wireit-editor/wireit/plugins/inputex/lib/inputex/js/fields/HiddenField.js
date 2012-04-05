(function() {

/**
 * Create a hidden input, inherits from inputEx.Field
 * @class inputEx.HiddenField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.HiddenField = function(options) {
	inputEx.HiddenField.superclass.constructor.call(this,options);
};

YAHOO.lang.extend(inputEx.HiddenField, inputEx.Field, {
   
   /**
    * Doesn't render much...
    */
   render: function() {
      this.type = inputEx.HiddenField;
	   this.divEl = inputEx.cn('div', null, {display: 'none'});
	   
	   this.el = inputEx.cn('input', {type: 'hidden'});
	   this.rawValue = ''; // initialize the rawValue with '' (default value of a hidden field)
	
	   if(this.options.name) this.el.name = this.options.name;
	   this.divEl.appendChild(this.el);
   },

   /**
    * Stores the typed value in a local variable, and store the value in the hidden input (cast as string by the input)
    * @param {Any} val The value to set
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   setValue: function(val, sendUpdatedEvt) {
	
	   // store in the hidden input (so the value is sent as "string" if HTML form submit)
      this.el.value = val;

      // store the value in a variable, so getValue can return it without type casting
      this.rawValue = val;

      // Call Field.setValue to set class and fire updated event
		inputEx.HiddenField.superclass.setValue.call(this,val, sendUpdatedEvt);
   },

   /**
    * Get the previously stored value (respect the datatype of the value)
    * @return {Any} the previously stored value
    */
   getValue: function() {
      return this.rawValue;
   }

});
   
// Register this class as "hidden" type
inputEx.registerType("hidden", inputEx.HiddenField);

})();