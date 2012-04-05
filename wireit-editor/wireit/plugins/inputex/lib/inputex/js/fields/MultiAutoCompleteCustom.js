(function() {  
	var inputEx = YAHOO.inputEx;
  var Event = YAHOO.util.Event;
  var lang = YAHOO.lang;
  
  /**
 * Create a multi autocomplete field customized
 * @class inputEx.MultiAutoCompleteCustom
 * @extends inputEx.MultiAutoComplete
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *	  <li>maxItems: the number of Items</li>
 *	  <li>maxItemsAlert: a function executed when the maxItems is reach</li>
 * </ul>
 */
  
inputEx.MultiAutoCompleteCustom = function(options) {
  this.maxItems = options.maxItems;	
  this.maxItemsAlert = options.maxItemsAlert;
	inputEx.MultiSelectFieldCustom.superclass.constructor.call(this,options);
  //Event.removeBlurListener(this.el, this.onBlur);	

};
YAHOO.lang.extend(inputEx.MultiAutoCompleteCustom, inputEx.MultiAutoComplete,{
   /**
    * renderComponent : override the MultiAutocomplete renderComponent function
    * <ul>
    *   <li>Use the custom ddlist </li>
    *   <li>render a Button "Add" to add non-autocomplete elements to the list</li>
    * </ul>
    */

   renderComponent: function() {
      inputEx.MultiAutoComplete.superclass.renderComponent.call(this);
      this.buttonAdd = inputEx.cn('button',{},{},'Add');
      Event.addListener(this.buttonAdd, 'click',this.onAdd,this,true)
      this.el.parentNode.appendChild(this.buttonAdd);

      
      this.ddlist = new inputEx.widget.ListCustom({parentEl: this.fieldContainer,maxItems: this.maxItems, maxItemsAlert: this.maxItemsAlert});
      this.ddlist.itemRemovedEvt.subscribe(function() {
         this.setClassFromState();
         this.fireUpdatedEvt();
      }, this, true);
      this.ddlist.listReorderedEvt.subscribe(this.fireUpdatedEvt, this, true);
   },    
   /**
    * onAdd : fired when someone click on the field button
    * <ul>
    *   <li>Add an element to the list from the value of the field </li>
    * </ul>
    */
   onAdd:function(e,a){
		 this.ddlist.addItem({label: this.el.value});
		 this.el.value = "";
		 this.hiddenEl.value = "";
   	this.fireUpdatedEvt();

	 },
	 
	    /**
    * onChange : Override the onChange of MultiAutoocmplete to fix a bug with the blurEvent in InputEx 0.5.0
    * <ul>
    *   <li>Add an element to the list from the value of the field </li>
    * </ul>
    */
   onChange: function(e) {
      this.setClassFromState();
      // Clear the field when no value 
	    if (this.hiddenEl.value != this.el.value) this.hiddenEl.value = this.el.value;
   },
	    /**
    * onBlur : Override the onBlur of MultiAutocomplete to fix a bug with the blurEvent in InputEx 0.5.0
    */   
   onBlur: function(e){
		 //the onBlur from an old version of inputex took in the AutoComplete.js file
	   if (this.hiddenEl.value != this.el.value && this.el.value != this.options.typeInvite) this.el.value = this.hiddenEl.value;
	     if(this.el.value == '' && this.options.typeInvite) {
	          Dom.addClass(this.divEl, "inputEx-typeInvite");
			   if (this.el.value == '') this.el.value = this.options.typeInvite;
      }
  }

});
})();
