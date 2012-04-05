(function() {

   var lang = YAHOO.lang, Event = YAHOO.util.Event;

/**
 * A field limited to number inputs
 * @class inputEx.IntegerField
 * @extends inputEx.StringField
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *    <li>negative: boolean indicating if we accept boolean numbers</li>
 * </ul>
 */
inputEx.IntegerField = function(options) {
   inputEx.IntegerField.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.IntegerField, inputEx.StringField, {
   /**
    * Adds the negative, min, and max options
    * @param {Object} options
    */
   setOptions: function(options) {
      inputEx.IntegerField.superclass.setOptions.call(this, options);
      
      this.options.negative = lang.isUndefined(options.negative) ? false : options.negative;
      this.options.min = lang.isUndefined(options.min) ? (this.options.negative ? -Infinity : 0) : parseInt(options.min,10);
      this.options.max = lang.isUndefined(options.max) ? Infinity : parseInt(options.max,10);
   },
   
   /**
    * Get the value
    * @return {int} The integer value
    */
   getValue: function() {
      // don't return NaN if empty field
      if ((this.options.typeInvite && this.el.value == this.options.typeInvite) || this.el.value == '') {
         return '';
      }
      
      return parseInt(this.el.value, 10);
   },
   
   /**
    * Validate  if is a number
    */
   validate: function() {
      var v = this.getValue();
      
      // empty field
      if (v === '') {
         // validate only if not required
         return !this.options.required;
      }
      
      if(isNaN(v)) return false;
      return !!this.el.value.match(new RegExp(this.options.negative ? "^[+-]?[0-9]*$" : "^\\+?[0-9]*$") ) && v >= this.options.min && v <= this.options.max;
   }
   
});

// Register this class as "integer" type
inputEx.registerType("integer", inputEx.IntegerField, [
   //{ type: 'integer', label: 'Radix', name: 'radix', value: 10},
   {type: 'boolean', label: 'Accept negative', name: 'negative', value: false }
]);

})();