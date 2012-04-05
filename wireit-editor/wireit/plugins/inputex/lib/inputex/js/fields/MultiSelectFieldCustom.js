(function() {   
	
	var inputEx = YAHOO.inputEx;

  /**
 * Create a multi Select field customized
 * @class inputEx.MultiSelectFieldCustom
 * @extends inputEx.MultiSelectField
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *	  <li>maxItems: the number of Items</li>
 *	  <li>maxItemsAlert: a function executed when the maxItems is reach</li>
 *	  <li>listSelectOptions : the options for a select field inside of the custom list</li>
 * </ul>
 */


inputEx.MultiSelectFieldCustom = function(options) {
	this.options = this.options || {};
  this.listSelectOptions= options.listSelectOptions;
  this.maxItems = options.maxItems;	
  this.maxItemsAlert = options.maxItemsAlert;
	inputEx.MultiSelectFieldCustom.superclass.constructor.call(this,options);
	
};
YAHOO.lang.extend(inputEx.MultiSelectFieldCustom, inputEx.MultiSelectField,{
   /**
    * renderComponent : override the MultiSelectField renderComponent function
    * <ul>
    *   <li>Use the custom ddlist </li>
    *   <li>put options for select fields in the ddList Custom</li>
    * </ul>
    */

   renderComponent: function() {
      inputEx.MultiSelectField.superclass.renderComponent.call(this);
      
      this.ddlist = new inputEx.widget.ListCustom({parentEl: this.fieldContainer,listSelectOptions: this.listSelectOptions, maxItems: this.maxItems, maxItemsAlert: this.maxItemsAlert });
      
   },   
   onItemRemoved: function(e,params) {
      var itemValue = params[0];
      var index = inputEx.indexOf(itemValue.value || itemValue, this.options.selectValues);
      this.el.childNodes[index].disabled = false;
      this.fireUpdatedEvt();
   },
   setValue: function(obj, sendUpdatedEvt) {
      
      this.ddlist.setValue(obj);
      
      // Re-enable all options
      for(var i = 0 ; i < this.el.childNodes.length ; i++) {
         this.el.childNodes[i].disabled = false;
      }
      // disable selected options
      for(i = 0 ; i < obj.length ; i++) {
         var index = inputEx.indexOf(obj[i].value || obj[i], this.options.selectValues);
         this.el.childNodes[index].disabled = true;
      }
	   
	   if(sendUpdatedEvt !== false) {
	      // fire update event
         this.fireUpdatedEvt();
      }
	},
	addItem: function(item) {
      this.el.selectedIndex = item.getId()+1;
       
      this.onAddNewItem();
   },
   
});

})();
