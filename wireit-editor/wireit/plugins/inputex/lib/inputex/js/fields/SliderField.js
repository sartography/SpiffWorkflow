(function () {
     var lang=YAHOO.lang;
     
/**
 * Create a slider using YUI widgets
 * @class inputEx.SliderField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.SliderField = function(options) {
   inputEx.SliderField.superclass.constructor.call(this,options);
};

YAHOO.lang.extend(inputEx.SliderField, inputEx.Field, {
   /**
    * Set the classname to 'inputEx-SliderField'
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
      inputEx.SliderField.superclass.setOptions.call(this, options);
      
      this.options.className = options.className ? options.className : 'inputEx-SliderField';
   	   
      this.options.minValue = lang.isUndefined(options.minValue) ? 0 : options.minValue;
      this.options.maxValue = lang.isUndefined(options.maxValue) ? 100 : options.maxValue;
      
      this.options.displayValue = lang.isUndefined(options.displayValue) ? true : options.displayValue;
   },
      
   /**
    * render a slider widget
    */
   renderComponent: function() {
            
      this.sliderbg = inputEx.cn('div', {id: YAHOO.util.Dom.generateId(), className: 'inputEx-SliderField-bg'});
      this.sliderthumb = inputEx.cn('div', {className: 'inputEx-SliderField-thumb'} );      
      this.sliderbg.appendChild(this.sliderthumb);
      this.fieldContainer.appendChild(this.sliderbg);
      
      if(this.options.displayValue) {
         this.valueDisplay = inputEx.cn('div', {className: 'inputEx-SliderField-value'}, null, String(this.options.minValue) );
         this.fieldContainer.appendChild(this.valueDisplay);
      }
      
      this.fieldContainer.appendChild( inputEx.cn('div',null,{clear: 'both'}) );
            
      this.slider = YAHOO.widget.Slider.getHorizSlider(this.sliderbg, this.sliderthumb, 0,100);
   },
   
   initEvents: function() {
      
      // Fire the updated event when we released the slider
      // the slider 'change' event would generate too much events (if used in a group, it gets validated too many times)
      this.slider.on('slideEnd', this.fireUpdatedEvt, this, true);
      
      // Update the displayed value
      if(this.options.displayValue) {
         this.updatedEvt.subscribe( function(e,params) {
            var val = params[0];
            this.valueDisplay.innerHTML = val;
         }, this, true);
      }
   },
   
   /**
    * Function to set the value
    * @param {Any} value The new value
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */  
   setValue: function(val, sendUpdatedEvt) {
      
      var v = val;
      if(v < this.options.minValue) {
         v = this.options.minValue;
      }
      if(v > this.options.maxValue) {
         v = this.options.maxValue;
      }
      
      var percent = Math.floor(v-this.options.minValue)*100/this.options.maxValue;
      
      this.slider.setValue(percent);
      
      inputEx.SliderField.superclass.setValue.call(this, val, sendUpdatedEvt);
   },

   /**
    * Get the value from the slider
    * @return {int} The integer value
    */
   getValue: function() {
      var val = Math.floor(this.options.minValue+(this.options.maxValue-this.options.minValue)*this.slider.getValue()/100);
      return val;
   }
    
});

// Register this class as "slider" type
inputEx.registerType("slider", inputEx.SliderField, [
   { type: 'integer', label: 'Min. value',  name: 'minValue', value: 0 },
   { type: 'integer', label: 'Max. value', name: 'maxValue', value: 100 }
]);

})();
