(function() {

   var Event = YAHOO.util.Event;

/**
 * Create a file input
 * @class inputEx.FileField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 * </ul>
 */
inputEx.FileField = function(options) {
	inputEx.FileField.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.FileField, inputEx.Field, {
	
   /**
    * Adds size and accept options
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
		inputEx.FileField.superclass.setOptions.call(this, options);
		this.options.size = options.size;
		this.options.accept = options.accept;
	},
	
   /**
    * Render an 'INPUT' DOM node
    */
   renderComponent: function() {
      
      // Attributes of the input field
      var attributes = {};
      attributes.id = this.divEl.id?this.divEl.id+'-field':YAHOO.util.Dom.generateId();
      attributes.type = "file";
      if(this.options.name) attributes.name = this.options.name;
   	if(this.options.size) attributes.size = this.options.size;
   	if(this.options.accept) attributes.accept = this.options.accept;

      // Create the node
      this.el = inputEx.cn('input', attributes);
      
      // Append it to the main element
      this.fieldContainer.appendChild(this.el);
   }

});

// Register this class as "file" type
inputEx.registerType("file", inputEx.FileField);

})();