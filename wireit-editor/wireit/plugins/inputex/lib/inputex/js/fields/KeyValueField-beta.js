/**
 * Display a selectors for keys and auto-update the value field
 * @class inputEx.KeyValueField
 * @constructor
 * @extends inputEx.CombineField
 * @param {Object} options InputEx definition object with the "availableFields"
 */
inputEx.KeyValueField = function(options) {
   inputEx.KeyValueField.superclass.constructor.call(this, options);
};

YAHOO.lang.extend( inputEx.KeyValueField, inputEx.CombineField, {
   
   /**
    * Subscribe the updatedEvt on the key selector
    */
   initEvents: function() {
      inputEx.KeyValueField.superclass.initEvents.call(this);

      this.inputs[0].updatedEvt.subscribe(this.onSelectFieldChange, this, true); 
   },


	/**
	 * Generate
	 */
	generateSelectConfig: function(availableFields) {
		
		this.nameIndex = {};
		
		var choices = [], i, field, fieldCopy, k, l;
		
		for (i = 0 , l = availableFields.length ; i < l ; i++) {
			
			field =  availableFields[i];
			fieldCopy = {};
			for (k in field) {
				if (field.hasOwnProperty(k) && k != "label") {
					fieldCopy[k] = field[k];
				}
			}
			
			this.nameIndex[field.name] = fieldCopy;
			
			choices.push({ value: field.name, label:field.label || field.name });
			
		}
		
		return { type: 'select', choices: choices };
	},

	/**
	 * Setup the options.fields from the availableFields option
	 */
	setOptions: function(options) {
		
		var selectFieldConfig = this.generateSelectConfig(options.availableFields);
	
		var newOptions = {
			fields: [
				selectFieldConfig,
				this.nameIndex[options.availableFields[0].name]
			]
		};
		
		YAHOO.lang.augmentObject(newOptions, options);
		
		inputEx.KeyValueField.superclass.setOptions.call(this, newOptions);
	},
   
   /**
    * Rebuild the value field
    */
   onSelectFieldChange: function(e, params) {
      var value = params[0];
      var f = this.nameIndex[value];
      var lastInput = this.inputs[this.inputs.length-1];
      var next = this.divEl.childNodes[inputEx.indexOf(lastInput.getEl(), this.divEl.childNodes)+1];
      lastInput.destroy();
      this.inputs.pop();
      var field = this.renderField(f);
      var fieldEl = field.getEl();
   	YAHOO.util.Dom.setStyle(fieldEl, 'float', 'left');
	   
   	this.divEl.insertBefore(fieldEl, next);
   }
   
});

inputEx.registerType("keyvalue", inputEx.KeyValueField, {});

