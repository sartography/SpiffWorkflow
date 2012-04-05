(function () {
	
	// shortcuts
	var lang = YAHOO.lang;
	
	
	inputEx.mixin.choice = {
		
		/**
		 * Add a choice
		 * @param {Object} config An object describing the choice to add (e.g. { value: 'second' [, label: 'Second' [, position: 1 || after: 'First' || before: 'Third']] })
		 */
		addChoice: function (config) {
			
			var choice, position, that;
			
			// allow config not to be an object, just a value -> convert it in a standard config object
			if (!lang.isObject(config)) {
				config = { value: config };
			}
			
			choice = {
				value: config.value,
				label: lang.isString(config.label) ? config.label : "" + config.value,
				visible: true
			};
			
			// Create DOM <option> node
			choice.node = this.createChoiceNode(choice);
			
			// Get choice's position
			//   -> don't pass config.value to getChoicePosition !!!
			//     (we search position of existing choice, whereas config.value is a property of new choice to be created...)
			position = this.getChoicePosition({ position: config.position, label: config.before || config.after });
			
			if (position === -1) { //  (default is at the end)
				position = this.choicesList.length;
				
			} else if (lang.isString(config.after)) {
				// +1 to insert "after" position (not "at" position)
				position += 1;
			}
			
			
			// Insert choice in list at position
			this.choicesList.splice(position, 0, choice);
			
			// Append <option> node in DOM
			this.appendChoiceNode(choice.node, position);
			
			// Select new choice
			if (!!config.selected) {
				
				// setTimeout for IE6 (let time to create dom option)
				that = this;
				setTimeout(function () {
					that.setValue(choice.value);
				}, 0);
				
			}
			
			// Return generated choice
			return choice;
			
		},
		
		/**
		 * Remove a choice
		 * @param {Object} config An object targeting the choice to remove (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		removeChoice: function (config) {
			
			var position, choice;
			
			// Get choice's position
			position = this.getChoicePosition(config);
			
			if (position === -1) {
				throw new Error("SelectField : invalid or missing position, label or value in removeChoice");
			}
			
			// Choice to remove
			choice = this.choicesList[position];
			
			// Clear if removing selected choice
			if (this.getValue() === choice.value) {
				this.clear();
			}
			
			// Remove choice in list at position
			this.choicesList.splice(position, 1); // remove 1 element at position
			
			// Remove node from DOM
			this.removeChoiceNode(choice.node);
			
		},
		
		/**
		 * Hide a choice
		 * @param {Object} config An object targeting the choice to hide (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		hideChoice: function (config) {
			
			var position, choice;
			
			position = this.getChoicePosition(config);
			
			if (position !== -1) {
				
				choice = this.choicesList[position];
				
				// test if visible first in case we try to hide twice or more...
				if (choice.visible) {
					
					choice.visible = false;
					
					// Clear if hiding selected choice
					if (this.getValue() === choice.value) {
						this.clear();
					}
					
					// Remove from DOM
					this.removeChoiceNode(choice.node);
					
				}
				
			}
			
		},
		
		/**
		 * Show a choice
		 * @param {Object} config An object targeting the choice to show (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		showChoice: function (config) {
			
			var position, choice;
			
			position = this.getChoicePosition(config);
			
			if (position !== -1) {
				
				choice = this.choicesList[position];
				
				if (!choice.visible) {
					
					choice.visible = true;
					this.appendChoiceNode(choice.node, position);
				
				}
				
			}
			
		},
		
		/**
		 * Disable a choice
		 * @param {Object} config An object targeting the choice to disable (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		disableChoice: function (config, unselect) {
			
			var position, choice;
			
			// Should we unselect choice if disabling selected choice
			if (lang.isUndefined(unselect) || !lang.isBoolean(unselect)) { unselect = true; }
			
			position = this.getChoicePosition(config);
			
			if (position !== -1) {
				
				choice = this.choicesList[position];
				
				this.disableChoiceNode(choice.node);
				
				// Clear if disabling selected choice
				if (unselect && this.getValue() === choice.value) {
					this.clear();
				}
				
			}
			
		},
		
		/**
		 * Enable a choice
		 * @param {Object} config An object targeting the choice to enable (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		enableChoice: function (config) {
			
			var position, choice;
			
			position = this.getChoicePosition(config);
			
			if (position !== -1) {
				
				choice = this.choicesList[position];
				
				this.enableChoiceNode(choice.node);
				
			}
			
		},
		
		/**
		 * Get the position of a choice in choicesList (NOT in the DOM)
		 * @param {Object} config An object targeting the choice (e.g. { position : 1 } || { value: 'second' } || { label: 'Second' })
		 */
		getChoicePosition: function (config) {
			
			var nbChoices, position = -1;
			
			nbChoices = this.choicesList.length;
			
			// Handle position
			if (lang.isNumber(config.position) && config.position >= 0 && config.position < nbChoices) {
				
				position = parseInt(config.position, 10);
				
			} else if (!lang.isUndefined(config.value)) {
				
				// get position of choice with value === config.value
				position = inputEx.indexOf(config.value, this.choicesList, function (value, opt) {
					return opt.value === value;
				});
				
			} else if (lang.isString(config.label)) {
				
				// get position of choice with label === config.label
				position = inputEx.indexOf(config.label, this.choicesList, function (label, opt) {
					return opt.label === label;
				});
				
			}
			
			return position;
		}
		
	};
	
}());