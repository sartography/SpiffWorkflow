(function () {
	
	/**
	 * Create a select field from a datasource
	 * @class inputEx.DSSelectField
	 * @extends inputEx.SelectField
	 * @constructor
	 * @param {Object} options Added options:
	 * <ul>
	 *	   <li>options: list of option elements configurations</li>
	 *    <li>datasource: the datasource</li>
	 *    <li>valueKey: value key</li>
	 *    <li>labelKey: label key</li>
	 * </ul>
	 */
	inputEx.DSSelectField = function (options) {
		inputEx.DSSelectField.superclass.constructor.call(this, options);
	};
	
	YAHOO.lang.extend(inputEx.DSSelectField, inputEx.SelectField, {
		/**
		 * Setup the additional options for selectfield
		 * @param {Object} options Options object as passed to the constructor
		 */
		setOptions: function (options) {
		
			inputEx.DSSelectField.superclass.setOptions.call(this, options);
		
			this.options.valueKey = options.valueKey || "value";
			this.options.labelKey = options.labelKey || "label";
		
			this.options.datasource = options.datasource;
		
		},
		
		/**
		 * Build a select tag with options
		 */
		renderComponent: function () {
		
			inputEx.DSSelectField.superclass.renderComponent.call(this);
		
			// Send the data request
			this.sendDataRequest(null); // TODO: configurable default request ?
		},
		
		/**
		 * Send the datasource request
		 */
		sendDataRequest: function (oRequest) {
			if (!!this.options.datasource) {
				this.options.datasource.sendRequest(oRequest, {success: this.onDatasourceSuccess, failure: this.onDatasourceFailure, scope: this});
			}
		},
		
		/**
		 * Insert the options
		 */
		populateSelect: function (items) {
		
			var i, length;
		
			// remove previous <option>s nodes
			while (this.el.childNodes.length > 0) {
				this.el.removeChild(this.el.childNodes[0]);
			}
		
			// add new options
			for (i = 0, length = items.length; i < length ; i += 1) {
				this.addChoice({ value: items[i][this.options.valueKey], label: items[i][this.options.labelKey] });
			}
		},
		
		/**
		 * Callback for request success 
		 */
		onDatasourceSuccess: function (oRequest, oParsedResponse, oPayload) {
			this.populateSelect(oParsedResponse.results);
		},
		
		/**
		 * Callback for request failure 
		 */
		onDatasourceFailure: function (oRequest, oParsedResponse, oPayload) {
			// TODO
			this.el.innerHTML = "<option>error</option>";
		}
		
	});
	
	// Register this class as "dsselect" type
	inputEx.registerType("dsselect", inputEx.DSSelectField);

}());