(function() {

   var lang = YAHOO.lang, Event = YAHOO.util.Event, Dom = YAHOO.util.Dom;

/**
 * An autocomplete field that wraps the YUI autocompleter
 * @class inputEx.AutoComplete
 * @constructor
 * @extends inputEx.StringField
 * @param {Object} options Added options for Autocompleter
 * <ul>
 *  <li>datasource: the datasource</li>
 *  <li>autoComp: autocompleter options</li>
 *   <li>returnValue: function to format the returned value (optional)</li>
 * </ul>
 */
inputEx.AutoComplete = function(options) {
   inputEx.AutoComplete.superclass.constructor.call(this, options);

};

lang.extend(inputEx.AutoComplete, inputEx.StringField, {

   /**
    * Adds autocomplete options
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
      inputEx.AutoComplete.superclass.setOptions.call(this, options);
  
      // Overwrite options
      this.options.className = options.className ? options.className : 'inputEx-Field inputEx-AutoComplete';
      
      // Added options
      this.options.datasource = options.datasource;
      this.options.autoComp = options.autoComp;
      this.options.returnValue = options.returnValue;
      this.options.generateRequest = options.generateRequest;
      this.options.datasourceParameters = options.datasourceParameters;
   },
   
   /**
    * Custom event init
    * <ul>
    *   <li>listen to autocompleter textboxBlurEvent instead of this.el "blur" event</li>
    *   <li>listener to autocompleter textboxBlurEvent added in buildAutocomplete method</li>
    * </ul>
    */
   initEvents: function() {
      inputEx.AutoComplete.superclass.initEvents.call(this);

      // remove standard blur listener
   },

   /**
    * Render the hidden list element
    */
   renderComponent: function() {
   
      // This element wraps the input node in a float: none div
      this.wrapEl = inputEx.cn('div', {className: 'inputEx-StringField-wrapper'});
      
      // Attributes of the input field
      var attributes = {
         type: 'text',
         id: YAHOO.util.Dom.generateId()
      };
      if(this.options.size) attributes.size = this.options.size;
      if(this.options.readonly) attributes.readonly = 'readonly';
      if(this.options.maxLength) attributes.maxLength = this.options.maxLength;

      // Create the node
      this.el = inputEx.cn('input', attributes);
      
      // Create the hidden input
      var hiddenAttrs = {
         type: 'hidden',
         value: ''
      };
      if(this.options.name) hiddenAttrs.name = this.options.name;
      this.hiddenEl = inputEx.cn('input', hiddenAttrs);
      
      // Append it to the main element
      this.wrapEl.appendChild(this.el);
      this.wrapEl.appendChild(this.hiddenEl);
      this.fieldContainer.appendChild(this.wrapEl);
   
      // Render the list :
      this.listEl = inputEx.cn('div', {id: Dom.generateId() });
      this.fieldContainer.appendChild(this.listEl);
       
      Event.onAvailable([this.el, this.listEl], this.buildAutocomplete, this, true);
   },
   
   /**
    * Build the YUI autocompleter
    */
   buildAutocomplete: function() {
      // Call this function only when this.el AND this.listEl are available
      if(!this._nElementsReady) { this._nElementsReady = 0; }
      this._nElementsReady++;
      if(this._nElementsReady != 2) return;

      if(!lang.isUndefined(this.options.datasourceParameters))
      {
         for (param in this.options.datasourceParameters)
         {
            this.options.datasource[param] = this.options.datasourceParameters[param];
         }
      }

      
      // Instantiate AutoComplete
      this.oAutoComp = new YAHOO.widget.AutoComplete(this.el.id, this.listEl.id, this.options.datasource, this.options.autoComp);
      if(!lang.isUndefined(this.options.generateRequest))
      {
          this.oAutoComp.generateRequest = this.options.generateRequest;
      }
      // subscribe to the itemSelect event
      this.oAutoComp.itemSelectEvent.subscribe(this.itemSelectHandler, this, true);
      
      // subscribe to the textboxBlur event (instead of "blur" event on this.el)
      //                                    |-------------- autocompleter ----------|
      //    -> order : "blur" on this.el -> internal callback -> textboxBlur event -> this.onBlur callback
      //    -> so fired after autocomp internal "blur" callback (which would erase typeInvite...)
      this.oAutoComp.textboxBlurEvent.subscribe(this.onBlur, this, true);
   },
   
   /**
    * itemSelect handler
    * @param {} sType
    * @param {} aArgs
    */
   itemSelectHandler: function(sType, aArgs) {
      var aData = aArgs[2];
      this.setValue( this.options.returnValue ? this.options.returnValue(aData) : aData[0] );
   },

   onBlur: function(e){
	 if (this.hiddenEl.value != this.el.value && this.el.value != this.options.typeInvite) this.el.value = this.hiddenEl.value;
	   if(this.el.value == '' && this.options.typeInvite) {
	         Dom.addClass(this.divEl, "inputEx-typeInvite");
			 if (this.el.value == '') this.el.value = this.options.typeInvite;
     }
},
   /**
    * onChange event handler
    * @param {Event} e The original 'change' event
    */
   onChange: function(e) {
      this.setClassFromState();
      // Clear the field when no value 
	 if (this.hiddenEl.value != this.el.value) this.hiddenEl.value = this.el.value;
      lang.later(50, this, function() {
         if(this.el.value == "") {
            this.setValue("");
         }
      });
   },
   
   /**
    * Set the value
    * @param {Any} value Value to set
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   setValue: function(value, sendUpdatedEvt) {
      this.hiddenEl.value = value || "";
      this.el.value  =  value || "";
      // "inherited" from inputex.Field :
      //    (can't inherit of inputex.StringField because would set this.el.value...)
      //
   // set corresponding style
   this.setClassFromState();

   if(sendUpdatedEvt !== false) {
      // fire update event
         this.fireUpdatedEvt();
      }
   },
   
   /**
    * Return the hidden value (stored in a hidden input)
    */
   getValue: function() {
      return this.hiddenEl.value;
   }

});


// Register this class as "autocomplete" type
inputEx.registerType("autocomplete", inputEx.AutoComplete);

})();
