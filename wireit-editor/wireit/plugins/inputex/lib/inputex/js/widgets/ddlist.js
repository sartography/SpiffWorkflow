(function() {

   var DD = YAHOO.util.DragDropMgr, Dom = YAHOO.util.Dom, Event = YAHOO.util.Event, lang = YAHOO.lang;
   
/**
 * DDProxy for DDList items (used by DDList)
 * @class inputEx.widget.DDListItem
 * @extends YAHOO.util.DDProxy
 * @constructor
 * @param {String} id
 */
inputEx.widget.DDListItem = function(id) {

    inputEx.widget.DDListItem.superclass.constructor.call(this, id);

    // Prevent lateral draggability
    this.setXConstraint(0,0);

    this.goingUp = false;
    this.lastY = 0;
};

YAHOO.extend(inputEx.widget.DDListItem, YAHOO.util.DDProxy, {

   /**
    * Create the proxy element
    */
   startDrag: function(x, y) {
        // make the proxy look like the source element
        var dragEl = this.getDragEl();
        var clickEl = this.getEl();
        Dom.setStyle(clickEl, "visibility", "hidden");
        this._originalIndex = inputEx.indexOf(clickEl ,clickEl.parentNode.childNodes);
        dragEl.className = clickEl.className;
        dragEl.innerHTML = clickEl.innerHTML;
    },

    /**
     * Handle the endDrag and eventually fire the listReordered event
     */
    endDrag: function(e) {
        Dom.setStyle(this.id, "visibility", "");
        
        // Fire the reordered event if position in list has changed
        var clickEl = this.getEl();
        var newIndex = inputEx.indexOf(clickEl ,clickEl.parentNode.childNodes);
        if(this._originalIndex != newIndex) {
           this._list.onReordered(this._originalIndex, newIndex);
        }
    },

    /**
     * @method onDragDrop
     */
    onDragDrop: function(e, id) {

        // If there is one drop interaction, the li was dropped either on the list,
        // or it was dropped on the current location of the source element.
        if (DD.interactionInfo.drop.length === 1) {

            // The position of the cursor at the time of the drop (YAHOO.util.Point)
            var pt = DD.interactionInfo.point; 

            // The region occupied by the source element at the time of the drop
            var region = DD.interactionInfo.sourceRegion; 

            // Check to see if we are over the source element's location.  We will
            // append to the bottom of the list once we are sure it was a drop in
            // the negative space (the area of the list without any list items)
            if (!region.intersect(pt)) {
                var destEl = Dom.get(id);
                if (destEl.nodeName.toLowerCase() != "li") {
                   var destDD = DD.getDDById(id);
                   destEl.appendChild(this.getEl());
                   destDD.isEmpty = false;
                   DD.refreshCache();
                }
            }

        }
    },

    /**
     * Keep track of the direction of the drag for use during onDragOver
     */
    onDrag: function(e) {
        var y = Event.getPageY(e);

        if (y < this.lastY) {
            this.goingUp = true;
        } else if (y > this.lastY) {
            this.goingUp = false;
        }

        this.lastY = y;
    },

    /**
     * @method onDragOver
     */
    onDragOver: function(e, id) {
    
        var srcEl = this.getEl();
        var destEl = Dom.get(id);

        // We are only concerned with list items, we ignore the dragover
        // notifications for the list.
        if (destEl.nodeName.toLowerCase() == "li") {
            var orig_p = srcEl.parentNode;
            var p = destEl.parentNode;

            if (this.goingUp) {
                p.insertBefore(srcEl, destEl); // insert above
            } else {
                p.insertBefore(srcEl, destEl.nextSibling); // insert below
            }

            DD.refreshCache();
        }
    }
});


/**
 * Create a sortable list 
 * @class inputEx.widget.DDList
 * @constructor
 * @param {Object} options Options:
 * <ul>
 *	   <li>id: id of the ul element</li>
 *	   <li>value: initial value of the list</li>
 * </ul>
 */
inputEx.widget.DDList = function(options) {
   
   this.ul = inputEx.cn('ul');
   
   this.items = [];
   
   this.setOptions(options);

   /**
	 * @event YAHOO custom event fired when an item is removed
	 * @param {Any} itemValue value of the removed item
	 */
	this.itemRemovedEvt = new YAHOO.util.CustomEvent('itemRemoved', this);
	
	/**
	 * @event YAHOO custom event fired when the list is reordered
	 */
   this.listReorderedEvt = new YAHOO.util.CustomEvent('listReordered', this);
   

   // append it immediatly to the parent DOM element
	if(options.parentEl) {
	   if( lang.isString(options.parentEl) ) {
	     Dom.get(options.parentEl).appendChild(this.ul);  
	   }
	   else {
	      options.parentEl.appendChild(this.ul);
      }
	}
	
};

inputEx.widget.DDList.prototype = {
	
   /**
    * Set the options 
    */
   setOptions: function(options) {
	   	this.options = {};
   		this.options.allowDelete = lang.isUndefined(options.allowDelete) ? true : options.allowDelete; 
	
		   if(options.id) {
		      this.ul.id = options.id;
		   }

		   if(options.value) {
		      this.setValue(options.value);
		   }

   },	

   /**
    * Add an item to the list
    * @param {String|Object} item Either a string with the given value or an object with "label" and "value" attributes
    */
   addItem: function(item) {
      var li = inputEx.cn('li', {className: 'inputEx-DDList-item'});
      li.appendChild( inputEx.cn('span', null, null, (typeof item == "object") ? item.label : item) );

      // Option for the "remove" link (default: true)
		if(!!this.options.allowDelete){
			var removeLink = inputEx.cn('a', null, null, "remove"); 
	      li.appendChild( removeLink );
	      Event.addListener(removeLink, 'click', function(e) {
	         var a = Event.getTarget(e);
	         var li = a.parentNode;
	         this.removeItem( inputEx.indexOf(li,this.ul.childNodes) );
	      }, this, true);
      }

      var dditem = new inputEx.widget.DDListItem(li);
      dditem._list = this;
      
      this.items.push( (typeof item == "object") ? item.value : item );
      
      this.ul.appendChild(li);
   },
   
   /**
    * private method to remove an item
    * @param {Integer} index index of item to be removed
    * @private
    */
   _removeItem: function(i) {
      
      var itemValue = this.items[i];
   
      this.ul.removeChild(this.ul.childNodes[i]);
      
      this.items[i] = null;
      this.items = inputEx.compactArray(this.items);
      
      return itemValue;
   },
   
   /**
    * Method to remove an item (_removeItem function + event firing)
    * @param {Integer} index Item index
    */
   removeItem: function(index) {
      var itemValue = this._removeItem(index);
      
      // Fire the itemRemoved Event
      this.itemRemovedEvt.fire(itemValue);
   },
   
   /**
    * Called by the DDListItem when an item as been moved
    */
   onReordered: function(originalIndex, newIndex) {
      if(originalIndex < newIndex) {
         this.items.splice(newIndex+1,0, this.items[originalIndex]);
         this.items[originalIndex] = null;
      }
      else {
         this.items.splice(newIndex,0, this.items[originalIndex]);
         this.items[originalIndex+1] = null;
      }      
      this.items = inputEx.compactArray(this.items);
      
      this.listReorderedEvt.fire();
   },
   
   /**
    * Return the current value of the field
    * @return {Array} array of values
    */
   getValue: function() {
      return this.items;
   },
   
   /**
    * Update the value of a given item
    * @param {Integer} index Item index
    * @param {Any} value New value
    */
   updateItem: function(index,value) {
      this.items[index] = value;
      this.ul.childNodes[index].childNodes[0].innerHTML = value;
   },
   
   /**
    * Set the value of the list
    * @param {Array} value list of values
    */
   setValue: function(value) {
      // if trying to set wrong value (or ""), reset
      if (!lang.isArray(value)) {
         value = [];
      }
      
      var oldNb = this.ul.childNodes.length;
      var newNb = value.length;
      
      for(var i = 0 ; i < newNb ; i++) {
         if(i < oldNb) {
            this.updateItem(i, value[i]);
         }
         else {
            this.addItem(value[i]);
         }
      }
      
      // remove extra li items if any
      for(var j = newNb; j < oldNb; j++) {
         this._removeItem(newNb); // newNb is always the index of first li to remove (not j !)
      }
   }
   
};


})();