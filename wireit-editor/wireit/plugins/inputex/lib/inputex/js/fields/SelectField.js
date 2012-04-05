(function () {

	var Event = YAHOO.util.Event, lang = YAHOO.lang;

	/**
	 * Create a select field
	 * @class inputEx.SelectField
	 * @extends inputEx.Field
	 * @constructor
	 * @param {Object} options Added options:
	 * <ul>
	 *    <li>choices: contains the list of choices configs ([{value:'usa'}, {value:'fr', label:'France'}])</li>
	 * </ul>
	 */
	inputEx.SelectField = function (options) {
		inputEx.SelectField.superclass.constructor.call(this, options);
	};

	lang.extend(inputEx.SelectField, inputEx.Field, {
		
		/**
		 * Set the default values of the options
		 * @param {Object} options Options object as passed to the constructor
		 */
		setOptions: function (options) {
		
			var i, length;
		
			inputEx.SelectField.superclass.setOptions.call(this, options);
		
			this.options.choices = lang.isArray(options.choices) ? options.choices : [];
		
			// Retro-compatibility with old pattern (changed since 2010-06-30)
			if (lang.isArray(options.selectValues)) {
			
				for (i = 0, length = options.selectValues.length; i < length; i += 1) {
				
					this.options.choices.push({
						value: options.selectValues[i],
						label: "" + ((options.selectOptions && !lang.isUndefined(options.selectOptions[i])) ? options.selectOptions[i] : options.selectValues[i])
					});
				
				}
			}
		
		},
	
		/**
		 * Build a select tag with options
		 */
		renderComponent: function () {
		
			var i, length;
		
			// create DOM <select> node
			this.el = inputEx.cn('select', {
			
				id: this.divEl.id ? this.divEl.id + '-field' : YAHOO.util.Dom.generateId(),
				name: this.options.name || ''
			
			});
		
			// list of choices (e.g. [{ label: "France", value:"fr", node:<DOM-node>, visible:true }, {...}, ...])
			this.choicesList = [];
		
			// add choices
			for (i = 0, length = this.options.choices.length; i < length; i += 1) {
				this.addChoice(this.options.choices[i]);
			}
		
			// append <select> to DOM tree
			this.fieldContainer.appendChild(this.el);
		},
	
		/**
		 * Register the "change" event
		 */
		initEvents: function () {
			Event.addListener(this.el, "change", this.onChange, this, true);
			Event.addFocusListener(this.el, this.onFocus, this, true);
			Event.addBlurListener(this.el, this.onBlur, this, true);
		},
	
		/**
		 * Set the value
		 * @param {String} value The value to set
		 * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
		 */
		setValue: function (value, sendUpdatedEvt) {
		
			var i, length, choice, firstIndexAvailable, choiceFound = false;
		
			for (i = 0, length = this.choicesList.length; i < length ; i += 1) {
			
				if (this.choicesList[i].visible) {
				
					choice = this.choicesList[i];
				
					if (value === choice.value) {
					
						choice.node.selected = "selected";
						choiceFound = true;
						break; // choice node already found
					
					} else if (lang.isUndefined(firstIndexAvailable)) {
					
						firstIndexAvailable = i;
					}
				
				}
			
			}
			
			// select value from first choice available when
			// value not matching any visible choice
			//
			// if no choice available (-> firstIndexAvailable is undefined), skip value setting
			if (!choiceFound && !lang.isUndefined(firstIndexAvailable)) {
				
				choice = this.choicesList[firstIndexAvailable];
				choice.node.selected = "selected";
				value = choice.value;
				
			}
			
			// Call Field.setValue to set class and fire updated event
			inputEx.SelectField.superclass.setValue.call(this, value, sendUpdatedEvt);
		},
	
		/**
		 * Return the value
		 * @return {Any} the selected value
		 */
		getValue: function () {
		
			var choiceIndex;
			
			if (this.el.selectedIndex >= 0) {
				
				choiceIndex = inputEx.indexOf(this.el.childNodes[this.el.selectedIndex], this.choicesList, function (node, choice) {
					return node === choice.node;
				});
			
				return this.choicesList[choiceIndex].value;
				
			} else {
				
				return "";
				
			}
		},
	
		/**
		 * Disable the field
		 */
		disable: function () {
			this.el.disabled = true;
		},

		/**
		 * Enable the field
		 */
		enable: function () {
			this.el.disabled = false;
		},
		
		createChoiceNode: function (choice) {
			
			return inputEx.cn('option', {value: choice.value}, null, choice.label);
			
		},
		
		removeChoiceNode: function (node) {
			
			// remove from selector
			// 
			//   -> style.display = 'none' would work only on FF (when node is an <option>)
			//   -> other browsers (IE, Chrome...) require to remove <option> node from DOM
			//
			this.el.removeChild(node);
			
		},
		
		disableChoiceNode: function (node) {
			
			node.disabled = "disabled";
			
		},
		
		enableChoiceNode: function (node) {
			
			node.removeAttribute("disabled");
			
		},
		
		/**
		 * Attach an <option> node to the <select> at the specified position
		 * @param {HTMLElement} node The <option> node to attach to the <select>
		 * @param {Int} position The position of the choice in choicesList (may not be the "real" position in DOM)
		 */
		appendChoiceNode: function (node, position) {
			
			var domPosition, i;
			
			// Compute real DOM position (since previous choices in choicesList may be hidden)
			domPosition = 0;
			
			for (i = 0; i < position; i += 1) {
				
				if (this.choicesList[i].visible) {
					
					domPosition += 1;
					
				}
				
			}
			
			// Insert in DOM
			if (domPosition < this.el.childNodes.length) {
				
				YAHOO.util.Dom.insertBefore(node, this.el.childNodes[domPosition]);
				
			} else {
				
				this.el.appendChild(node);
				
			}
		}
		
	});
	
	// Augment prototype with choice mixin (functions : addChoice, removeChoice, etc.)
	lang.augmentObject(inputEx.SelectField.prototype, inputEx.mixin.choice);
	
	
	// Register this class as "select" type
	inputEx.registerType("select", inputEx.SelectField, [
		{
			type: 'list',
			name: 'choices',
			label: 'Choices',
			elementType: {
				type: 'group',
				fields: [
					{ label: 'Value', name: 'value', value: '' }, // not required to allow '' value (which is default)
					{ label: 'Label', name: 'label' } // optional : if left empty, label is same as value
				]
			},
			value: [],
			required: true
		}
	]);

}());