(function() {

   var Event = YAHOO.util.Event, lang = YAHOO.lang;

/**
 * A field limited to number inputs (floating)
 * @class inputEx.NumberField
 * @extends inputEx.StringField
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.NumberField = function(options) {
   inputEx.NumberField.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.NumberField, inputEx.StringField, {
   /**
    * Adds the min, and max options
    * @param {Object} options
    */
   setOptions: function(options) {
      inputEx.NumberField.superclass.setOptions.call(this, options);
      
      this.options.min = lang.isUndefined(options.min) ? -Infinity : parseFloat(options.min);
      this.options.max = lang.isUndefined(options.max) ? Infinity : parseFloat(options.max);
   },
   /**
    * Return a parsed float (javascript type number)
    * @return {Number} The parsed float
    */
   getValue: function() {
      // don't return NaN if empty field
      if ((this.options.typeInvite && this.el.value == this.options.typeInvite) || this.el.value == '') {
         return '';
      }
      
      return parseFloat(this.el.value);
   },
   
   /**
    * Check if the entered number is a float
    */
   validate: function() { 
      var v = this.getValue();
      
      // empty field
      if (v === '') {
         // validate only if not required
         return !this.options.required;
      }
      
      if(isNaN(v)) return false;
	   
	   // We have to check the number with a regexp, otherwise "0.03a" is parsed to a valid number 0.03
	   return !!this.el.value.match(/^([\+\-]?((([0-9]+(\.)?)|([0-9]*\.[0-9]+))([eE][+-]?[0-9]+)?))$/) && v >= this.options.min && v <= this.options.max;
   }

});

// Register this class as "number" type
inputEx.registerType("number", inputEx.NumberField, []);

})();