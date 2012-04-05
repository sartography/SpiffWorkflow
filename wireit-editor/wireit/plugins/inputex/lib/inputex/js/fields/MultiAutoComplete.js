(function() {

   var lang = YAHOO.lang;

/**
 * Create a multi autocomplete field
 * @class inputEx.MultiAutoComplete
 * @extends inputEx.AutoComplete
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 * </ul>
 */
inputEx.MultiAutoComplete = function(options) {
	inputEx.MultiAutoComplete.superclass.constructor.call(this,options);
 };
lang.extend(inputEx.MultiAutoComplete, inputEx.AutoComplete, {
   
   /**
    * Build the DDList
    */
   renderComponent: function() {
      inputEx.MultiAutoComplete.superclass.renderComponent.call(this);
      
      this.ddlist = new inputEx.widget.DDList({parentEl: this.fieldContainer});
      this.ddlist.itemRemovedEvt.subscribe(function() {
         this.setClassFromState();
         this.fireUpdatedEvt();
      }, this, true);
      this.ddlist.listReorderedEvt.subscribe(this.fireUpdatedEvt, this, true);
   },  
   
   /**
    * Additional options
    */
   setOptions: function(options) {
      inputEx.MultiAutoComplete.superclass.setOptions.call(this, options);
      
      // Method to format the ddlist item labels
      this.options.returnLabel = options.returnLabel;
   },
   
   /**
    * Handle item selection in the autocompleter to add it to the list
    */
   itemSelectHandler: function(sType, aArgs) {
   	var aData = aArgs[2];
   	var value = lang.isFunction(this.options.returnValue) ? this.options.returnValue(aData) : aData[0];
   	var label = lang.isFunction(this.options.returnLabel) ? this.options.returnLabel(aData) : value;   	
   	this.ddlist.addItem({label: label, value: value});
   	this.el.value = "";
   	this.fireUpdatedEvt();
   },
   
   /**
    * Set the value
    * @param {String} value The value to set
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   setValue: function(value, sendUpdatedEvt) {
      this.ddlist.setValue(value);
      
      // set corresponding style
	   this.setClassFromState();
	   
	   if(sendUpdatedEvt !== false) {
	      // fire update event
         this.fireUpdatedEvt();
      }
   },
   
   /**
    * Return the value
    * @return {Any} an array of selected values
    */
   getValue: function() {
      return this.ddlist.getValue();
   },
   
   /**
    * Return (stateEmpty|stateRequired) if the value equals the typeInvite attribute
    */
   getState: function() { 
      var val = this.getValue();
      
	   // if nothing in the list
	   if( val.length === 0) {
	      return this.options.required ? inputEx.stateRequired : inputEx.stateEmpty;
	   }
      
	   return this.validate() ? inputEx.stateValid : inputEx.stateInvalid;
	},
	
	/**
    * TODO : how to validate ?
    */
   validate: function() { 
      return true;
   },
   
   /**
    * onChange event handler
    * @param {Event} e The original 'change' event
    */
	onChange: function(e) {
	   // erase inherited version, so don't trash previous value if input is empty
	}
   
   
});

// Register this class as "multiautocomplete" type
inputEx.registerType("multiautocomplete", inputEx.MultiAutoComplete);

})();