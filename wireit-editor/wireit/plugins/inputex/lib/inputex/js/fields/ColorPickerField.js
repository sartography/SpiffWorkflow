(function() {
	
   var widget = YAHOO.widget, Event = YAHOO.util.Event, Dom = YAHOO.util.Dom;
	
/**
 * Create a Color picker input field
 * @class inputEx.ColorPickerField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options for ColorPickerField :
 * <ul>
 * 	<li>showcontrols: show the input values RGB,HSV,RGB hex</li>
 * </ul>
 */
inputEx.ColorPickerField = function(options) {
	inputEx.ColorPickerField.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.ColorPickerField, inputEx.Field, {
   
	/**
	 * Adds the 'inputEx-ColorPickerField' default className
	 * @param {Object} options Options object as passed to the constructor
	 */
   setOptions: function(options) {
   	inputEx.ColorPickerField.superclass.setOptions.call(this, options);
   	
   	// Overwrite options
   	this.options.className = options.className ? options.className : 'inputEx-Field inputEx-ColorPickerField';

		// Color Picker options object
		this.options.colorPickerOptions = YAHOO.lang.isUndefined(options.colorPickerOptions) ? {} : options.colorPickerOptions;
		
		// showcontrols
		this.options.colorPickerOptions.showcontrols = YAHOO.lang.isUndefined(this.options.colorPickerOptions.showcontrols) ? true : this.options.colorPickerOptions.showcontrols;
		
		// default images (color selection images)
		this.options.colorPickerOptions.images = YAHOO.lang.isUndefined(this.options.colorPickerOptions.images) ? { PICKER_THUMB: "../lib/yui/colorpicker/assets/picker_thumb.png", HUE_THUMB: "../lib/yui/colorpicker/assets/hue_thumb.png" } : this.options.colorPickerOptions.images;
		
   },
   
	/**
	 * Render the color button and the colorpicker popup
	 */
	renderComponent: function() {
		
	   // A hidden input field to store the color code 
	   this.el = inputEx.cn('input', {
	      type: 'hidden', 
	      name: this.options.name || '', 
	      value: this.options.value || '#FFFFFF'
	   });
	   	   
      // This element wraps the input node in a float: none div
      this.wrapEl = inputEx.cn('div', {className: 'inputEx-ColorPickerField-wrapper'});
	   this.wrapEl.appendChild(this.el);

		// Create a Menu instance to house the ColorPicker instance
		this.menuElId = Dom.generateId();
		var oColorPickerMenu = new widget.Menu(this.menuElId);
		this.oColorPickerMenu = oColorPickerMenu;

		// Create a Button instance of type "menu"
		this.labelElId = Dom.generateId();
		var oButton = new widget.Button({ 
			type: "menu", 
			className: "inputEx-ColorPicker-Button",
			label: "<em id=\""+this.labelElId+"\" class='inputEx-ColorPicker-Label'>Current color is #FFFFFF.</em>", 
			menu: oColorPickerMenu, 
			container: this.wrapEl
		});
		
		var that = this;
		oButton.on("appendTo", function () {
			oColorPickerMenu.setBody(" ");
			oColorPickerMenu.body.id = Dom.generateId();
			Dom.addClass(oColorPickerMenu.body, that.options.colorPickerOptions.showcontrols ? "inputEx-ColorPicker-Container" : "inputEx-ColorPicker-Container-nocontrols");
			oColorPickerMenu.render(this.get('container'));
		});

		/*
			Add a listener for the "click" event.  This listener will be
			used to defer the creation the ColorPicker instance until the 
			first time the Button's Menu instance is requested to be displayed
			by the user.
		*/
		oButton.on("click", this.onButtonClickOnce, this, true);
		
		this.oButton = oButton;

		this.fieldContainer.appendChild(this.wrapEl);
	},
	
	onButtonClickOnce: function(event) {
		
		// Remove this event listener so that this code runs only once
		this.oButton.unsubscribe("click", this.onButtonClickOnce, this);
		
		this.oColorPicker = new widget.ColorPicker(this.oColorPickerMenu.body.id, this.options.colorPickerOptions);
		
		if(this.options.value) {
			this.oColorPicker.set("hex", this.options.value.substr(1));
		}

		/*
			Add a listener for the ColorPicker instance's "rgbChange" event
			to update the background color and text of the Button's 
			label to reflect the change in the value of the ColorPicker.
		*/
		this.oColorPicker.on("rgbChange", this.onRgbChange, this, true);
	},
	
	onRgbChange: function(p_oEvent) {
		var sColor = "#" + this.oColorPicker.get("hex");
		this.oButton.set("value", sColor);
		var el = Dom.get(this.labelElId);
		Dom.setStyle(el, "backgroundColor", sColor);
		el.innerHTML = "Current color is " + sColor;
		this.el.value = sColor;
		
		// timer to filter very close events (updatedEvt is sent only 50ms after the onRgbChange event)
		if(this.rgbChangeTimeout) {
			clearTimeout(this.rgbChangeTimeout);
		}
		var that = this;
		this.rgbChangeTimeout = setTimeout(function() {
			that.onRgbChangeTimeout();
		}, 50);
	},
	
	onRgbChangeTimeout: function() {
		this.fireUpdatedEvt();
	},
	
	/**
	 * Set the value
	 * @param {String} value Color to set
	 * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
	 */
	setValue: function(value, sendUpdatedEvt) {
	   this.el.value = value;
		
		if(this.oButton) {
			this.oButton.set("value", value);
			var el = Dom.get(this.labelElId);
			if(el) {
				Dom.setStyle(el, "backgroundColor", value);
				el.innerHTML = "Current color is " + value;
			}
			else {
				Event.onAvailable(this.labelElId, function() {
					Dom.setStyle(this, "backgroundColor", value);
					this.innerHTML = "Current color is " + value;
				});
			}
		}
	
		if(this.oColorPicker) {
			this.oColorPicker.set("hex", value.substr(1));
		}

		// Call Field.setValue to set class and fire updated event
		inputEx.ColorPickerField.superclass.setValue.call(this,value, sendUpdatedEvt);
	},
	   
	/**
	 * Return the color value
	 * @return {String} Color value
	 */
	getValue: function() {
	   return this.el.value;
	}
	  
}); 
	
	
// Register this class as "color" type
inputEx.registerType("colorpicker", inputEx.ColorPickerField, []);
	
})();