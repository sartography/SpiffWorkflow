/**
 * Add an SQL operator select field in the middle of a KeyValueField
 * @class inputEx.KeyOpValueField
 * @constructor
 * @extend inputEx.KeyValueField
 * @param {Object} options InputEx definition object with the "availableFields"
 */
inputEx.KeyOpValueField = function (options) {
	inputEx.KeyValueField.superclass.constructor.call(this, options);
};

YAHOO.lang.extend(inputEx.KeyOpValueField, inputEx.KeyValueField, {
	
	/**
	 * Setup the options.fields from the availableFields option
	 */
	setOptions: function (options) {
		
		var selectFieldConfig, operators, labels, selectOptions, newOptions, i, length;
		
		selectFieldConfig = this.generateSelectConfig(options.availableFields);
		
		operators = options.operators || ["=", ">", "<", ">=", "<=", "!=", "LIKE", "NOT LIKE", "IS NULL", "IS NOT NULL"];
		labels = options.operatorLabels || operators;
		
		selectOptions = [];
		
		for (i = 0, length = operators.length; i < length; i += 1) {
			selectOptions.push({ value: operators[i], label: labels[i] });
		}
		
		newOptions = {
			fields: [
				selectFieldConfig,
				{type: 'select', choices: selectOptions},
				this.nameIndex[options.availableFields[0].name]
			]
		};
		
		YAHOO.lang.augmentObject(newOptions, options);
		
		inputEx.KeyValueField.superclass.setOptions.call(this, newOptions);
	}
	
});

inputEx.registerType("keyopvalue", inputEx.KeyOpValueField, {});
