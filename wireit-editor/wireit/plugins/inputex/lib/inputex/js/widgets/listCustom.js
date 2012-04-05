(function() {

   var lang = YAHOO.lang;
   var inputEx = YAHOO.inputEx;
   
inputEx.widget.ListCustom = function(options) {
  
	this.listSelectOptions = options.listSelectOptions;
	this.maxItems = options.maxItems;
	this.maxItemsAlert = options.maxItemsAlert;

	inputEx.widget.ListCustom.superclass.constructor.call(this,options);

	this.selects = [];
};
YAHOO.lang.extend(inputEx.widget.ListCustom,inputEx.widget.DDList,{
/**
    * Add an item to the list
    * @param {String|Object} item Either a string with the given value or an object with "label" and "value" attributes
    */
   addItem: function(item) {

      if (this.maxItems && this.items.length >= this.maxItems){
				this.maxItemsAlert ? this.maxItemsAlert.call() : alert("You're limited to "+this.maxItems+" items");
			  return;	
			}
			
      var label = (typeof item == "object") ? item.label : item	;
      var li = inputEx.cn('li', {className: 'inputEx-DDList-item'});
      var span = inputEx.cn('span', null, null, label)

      if(this.listSelectOptions){
        var select = new inputEx.SelectField(this.listSelectOptions); 
        this.selects.push(select);
        li.appendChild(select.el);
        item.getValue = function(){
				  return {select: select.getValue(), label: this.label, value: this.value};
				}
				item.setValue = function(obj){
				  span.innerHTML = obj.label;
				  this.label = obj.label;
				  this.value = obj.value;
				  select.setValue(obj.select);
				}
		  } else {
			  item.getValue = function(){
					result = {};
					if(this.value) result.value = this.value;
					if(this.label) result.label = this.label;
					return result;
				}				
			  item.setValue = function(obj){
				  span.innerHTML = obj.label;
				  this.label = obj.label;
				  this.value = obj.value;
				}
			}
      li.appendChild(span);
 

      // Option for the "remove" link (default: true)
		if(!!this.options.allowDelete){
			var removeLink = inputEx.cn('div', {className:"removeButton"}, null, ""); 
	      li.appendChild( removeLink );
	      Event.addListener(removeLink, 'click', function(e) {
	         var a = Event.getTarget(e);
	         var li = a.parentNode;
	         this.removeItem( inputEx.indexOf(li,this.ul.childNodes) );
	      }, this, true);
      }
      // Don't want any drag and drop
      //var dditem = new inputEx.widget.DDListItem(li);
      //
      
      this.items.push( item );

      this.ul.appendChild(li);
   },
   getValue: function(){
		 var results = [];
		 for(var i in this.items){
		   results.push(this.items[i].getValue());
		 }
		 return results;
	 },
   setValue: function(objs){	  
			if(this.items.length > objs.length){
			  for (var i = 0; i< this.items.length -objs.length; i++){
				  this.removeItem(this.items.length-1-i);
				}
			}
			for (i in objs){
				if (this.items[i]){
				 this.items[i].setValue(objs[i]);
				} else {
				 this.addItem(objs[i]);
				}
			} 
	 }
}); 

})();
