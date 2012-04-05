(function() {

   var lang = YAHOO.lang;

/**
 * Copy of the original inputEx.Field class that we're gonna override to extend it.
 * @class BaseField
 * @namespace inputEx
 */
inputEx.BaseField = inputEx.Field;

/**
 * Class to make inputEx Fields "wirable".Re-create inputEx.Field adding the wirable properties
 * @class Field
 * @namespace inputEx
 * @extends inputEx.BaseField
 */
inputEx.Field = function(options) {
   inputEx.Field.superclass.constructor.call(this,options);
};

lang.extend(inputEx.Field, inputEx.BaseField, {

   /**
    * Adds a wirable option to every field
    * @method setOptions
    */
   setOptions: function(options) {
      inputEx.Field.superclass.setOptions.call(this, options);
      
      this.options.wirable = lang.isUndefined(options.wirable) ? false : options.wirable;
      this.options.container = options.container;
      //options.container = null;
   },
   
   /**
    * Adds a terminal to each field
    * @method render
    */
   render: function() {
      inputEx.Field.superclass.render.call(this);
      
      if(this.options.wirable) {
         this.renderTerminal();
      }
   },
   
   /**
    * Render the associated input terminal
    * @method renderTerminal
    */
   renderTerminal: function() {

      var wrapper = inputEx.cn('div', {className: 'WireIt-InputExTerminal'});
      this.divEl.insertBefore(wrapper, this.fieldContainer);

      this.terminal = new WireIt.Terminal(wrapper, {
         name: this.options.name, 
         direction: [-1,0],
         fakeDirection: [0, 1],
         ddConfig: {
            type: "input",
            allowedTypes: ["output"]
         },
      nMaxWires: 1 }, this.options.container);

      // Reference to the container
      if(this.options.container) {
         this.options.container.terminals.push(this.terminal);
      }

      // Register the events
      this.terminal.eventAddWire.subscribe(this.onAddWire, this, true);
      this.terminal.eventRemoveWire.subscribe(this.onRemoveWire, this, true);
    },

	/**
	 * Set the container for this field
	 */
	setContainer: function(container) {
		this.options.container = container;
		if(this.terminal) {
			this.terminal.container = container;
			if( WireIt.indexOf(this.terminal, container.terminals) == -1 ) {
				container.terminals.push(this.terminal);
			}
		}		
	},

	/**
	 * also change the terminal name when changing the field name
	 */
	setFieldName: function(name) {
		if(this.terminal) {
			this.terminal.name = name;
			this.terminal.el.title = name;
		}
	},

    /**
     * Remove the input wired state on the 
     * @method onAddWire
     */
    onAddWire: function(e, params) {
       this.options.container.onAddWire(e,params);

       this.disable();
       this.el.value = "[wired]";
    },

    /**
     * Remove the input wired state on the 
     * @method onRemoveWire
     */
    onRemoveWire: function(e, params) { 
       this.options.container.onRemoveWire(e,params);

       this.enable();
       this.el.value = "";
    }

});

inputEx.Field.groupOptions = inputEx.BaseField.groupOptions.concat([
	{ type: 'boolean', label: 'Wirable', name: 'wirable', value: false}
]);

})();