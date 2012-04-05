(function() {
   
   var lang = YAHOO.lang;

/**
 * Display a group with inplace edit and custom template
 * @class inputEx.Lens
 * @extends inputEx.Group
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *    <li>lens: html code for the lens. Fields will be displayed in the div elements that has the classname named "field-(field name)"</li>
 *    <li>visus: list of visualization for each field</li>
 * </ul>
 */
inputEx.Lens = function(options) {
   inputEx.Lens.superclass.constructor.call(this, options);
};

lang.extend(inputEx.Lens, inputEx.Group, {
   
   /**
    * Set additional options
    */
	setOptions: function(options) {
		inputEx.Lens.superclass.setOptions.call(this, options);	
		
		var lens = "";
		if( !lang.isString(options.lens) ) {
			for(var i = 0 ; i < this.options.fields.length ; i++) {
				lens += "<div class='field-"+this.options.fields[i].name+"'></div>";
			}
		}
		this.options.lens = lang.isString(options.lens) ? options.lens : lens;
		
		this.options.visus = options.visus;
	},
	
	/**
	 * Render each the fields in each div which class attribute is "field-"+fieldName
	 */
	renderFields: function(parentEl) {
      
			parentEl.innerHTML = this.options.lens;
			
			for(var i = 0 ; i < this.options.fields.length ; i++) {
				var els = YAHOO.util.Dom.getElementsByClassName( "field-"+this.options.fields[i].name, "div", parentEl);
				var el = els[0];
				var params = { parentEl: el, editorField: this.options.fields[i], name: this.options.fields[i].name };
				if(this.options.visus) {
					params.visu = this.options.visus[i];
				}
				var field = new inputEx.InPlaceEdit(params);
				
				this.inputs.push(field);
				if(field.options.name) {
		    	this.inputsNames[field.options.name] = field;
		    }
			  // Subscribe to the field "updated" event to send the group "updated" event
			  field.updatedEvt.subscribe(this.onChange, this, true);
		
			}
  	
   }
	
});



})();