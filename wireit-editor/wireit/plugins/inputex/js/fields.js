// this file ovveride many functions on inputEx fields to make them wirable

/**
 * setFieldName might change the name of the terminal
 */
inputEx.StringField.prototype.setFieldName = function(name) {
	this.el.name = name;
	if(this.terminal) {
		this.terminal.name = name;
		this.terminal.el.title = name;
	}
};


/**
 * Groups must set the container recursively
 */
inputEx.Group.prototype.setContainer = function(container) {
	
	inputEx.Group.superclass.setContainer.call(this, container);
	
	// Group and inherited fields must set this recursively
	if(this.inputs) {
		for(var i = 0 ; i < this.inputs.length ; i++) {
			this.inputs[i].setContainer(container);
		}
	}
	
};


/**
 * List must set the container recursively
 */
inputEx.ListField.prototype.setContainer = function(container) {
	
	inputEx.ListField.superclass.setContainer.call(this, container);

	if(this.subFields) {
		for(var i = 0 ; i < this.subFields.length ; i++) {
			this.subFields[i].setContainer(container);
		}
	}
	
};

/**
 * setContainer must be called on each new element
 */
inputEx.ListField.prototype._addElement = inputEx.ListField.prototype.addElement;
inputEx.ListField.prototype.addElement = function(value) {
	var f = this._addElement(value);
	f.setContainer(this.options.container);
	return f;
};


