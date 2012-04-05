(function() {

   var lang = YAHOO.lang, Dom = YAHOO.util.Dom, Event = YAHOO.util.Event;


/**
 * InPlaceEditable datatable using inputEx fields
 * @class inputEx.widget.dtInPlaceEdit
 * @extends inputEx.widget.DataTable
 * @constructor
 * @param {Object} options Options
 */
inputEx.widget.dtInPlaceEdit = function(options) {
   inputEx.widget.dtInPlaceEdit.superclass.constructor.call(this, options);
};

lang.extend(inputEx.widget.dtInPlaceEdit, inputEx.widget.DataTable , {
	
	renderDatatable: function() {
		inputEx.widget.dtInPlaceEdit.superclass.renderDatatable.call(this);

		 // Force save on blur event
		this.datatable.onEditorBlurEvent = function(oArgs) {
			if(oArgs.editor.save) {
			    oArgs.editor.save();
			} 
		};
		
		// When the cellEditor fires the "editorSaveEvent"
		this.datatable.subscribe("editorSaveEvent",function(oArgs){
			var record = oArgs.editor.getRecord();		
			// If the record got an id (meaning it isn't a new Row that the user didn't add yet)
			if( !lang.isUndefined(record.getData('id')) ){
				// If the data in the cellEditor changed
				if(oArgs.newData !== oArgs.oldData){
					this.onModifyItem(record, oArgs);
				}
			}
				
		}, this, true);
		
	},


   /**
    * Additional options
    */
   setOptions: function(options) {
     inputEx.widget.dtInPlaceEdit.superclass.setOptions.call(this, options);
     
     this.options.allowModify = false;
		this.options.insertWithDialog = lang.isUndefined(options.insertWithDialog) ? false : options.insertWithDialog; 
   },
   
   /**
    * Init the events
    */
   initEvents: function() {
	  inputEx.widget.dtInPlaceEdit.superclass.initEvents.call(this);
	
     this.requiredFieldsEvt = new YAHOO.util.CustomEvent('requiredFields', this);
	},

	/**
	 * Modify the column definitions to add the inputEx CellEditor
	 */
   setColumnDefs: function() {
		var columndefs = inputEx.widget.dtInPlaceEdit.superclass.setColumnDefs.call(this);
		
		// index fields declaration by keys
		var fieldsByKey = {};
		for(var k = 0 ; k < this.options.fields.length ; k++) {
		   
		   // Retro-compatibility with inputParms
         if (lang.isObject(this.options.fields[k].inputParams)) {
            fieldsByKey[this.options.fields[k].inputParams.name] = this.options.fields[k];
         // New prefered way to use options of a field
         } else {
            fieldsByKey[this.options.fields[k].name] = this.options.fields[k];
         }
		   
		}
		for(var i = 0 ; i < columndefs.length ; i++) {
			var columnDef = columndefs[i];
			if( YAHOO.lang.isUndefined(columnDef.editor) && !!fieldsByKey[columnDef.key] ) {
	          columnDef.editor = new inputEx.widget.CellEditor(fieldsByKey[columnDef.key]);
	      }
		}
		
		return columndefs;
	},

   /**
    * Handling cell click events
    */
   _onCellClick: function(ev,args) {
      var target = Event.getTarget(ev);
      var column = this.datatable.getColumn(target);      
      var rowIndex = this.datatable.getTrIndex(target);
      var record = this.datatable.getRecord(target);

      if (column.key == 'delete') {
			this.onRemoveItem(record,target);	
      }
      else {				
      	this.onCellClick(ev,rowIndex);
      }
   },

   /**
    * Public handler - When clicking on one of the datatable's cells
    */
   onCellClick: function(ev, rowIndex) {
		
		// Get a particular CellEditor
		var elCell = ev.target, oColumn;
		elCell = this.datatable.getTdEl(elCell);
		if(elCell) {
			oColumn = this.datatable.getColumn(elCell);
			if(oColumn && oColumn.editor) {
				var oCellEditor = this.datatable._oCellEditor;
				// Clean up active CellEditor
				if(oCellEditor) {
					// Return if field isn't validated
					if( !oCellEditor._inputExField.validate() ) {
						return;
					}
				}
			}
		}

		// Only if the cell is inputEx valid
		this.datatable.onEventShowCellEditor(ev);
		
   },

	/**
	 * When trying to delete a row
	 */
	onRemoveItem: function(record,target){
		var targetNode = target.childNodes[0];
		
		// Only if the row has an id && isn't already being removed
		if( !lang.isUndefined(record.getData('id')) && this.deleteLinkNode != targetNode ){

         if (confirm(inputEx.messages.confirmDeletion)) {
				this.deleteLinkNode = targetNode;		
				this.deleteLinkNode.innerHTML = '';
				Dom.addClass(this.deleteLinkNode,'inputEx-dtInPlaceEdit-deleteLinkSpinner');
				this.itemRemovedEvt.fire( record );            
         }
		}
	},
	
	/**
	 * When successfully deleted a row
	 */
	onRemoveSuccess: function(record){
		this.datatable.deleteRow(record);
	},
	
	/**
	 * When failed to delete a row
	 */
	onRemoveFailure: function(){
		this.deleteLinkNode.innerHTML = inputEx.messages.deleteText;
		Dom.removeClass(this.deleteLinkNode,'inputEx-dtInPlaceEdit-deleteLinkSpinner');
		this.deleteLinkNode = null;
	},
	
	/**
    * When clicking on the "insert" button to add a new row
    */
	onInsertButton: function(e) {
		
		// If insertWithDialog
		if(this.options.insertWithDialog) {
			inputEx.widget.dtInPlaceEdit.superclass.onInsertButton.call(this, e);
			return;
		}
		
		var tbl = this.datatable;
		
		// Insert a new row
      tbl.addRow({});

		// Select the new row
      var lastRow = tbl.getLastTrEl();
		tbl.selectRow(lastRow);
				
		// Get the last cell's inner div node
		var lastIndex = lastRow.childNodes.length - 1;
		lastCell = lastRow.childNodes[lastIndex].childNodes[0];
		
		// Empty the cell (removing "delete")
		lastCell.innerHTML = '';
		
		// Create an "Add" Button
		this.addButton = inputEx.cn('input', {type:'button',value:inputEx.messages.addButtonText}, null, null);
      Event.addListener(this.addButton, 'click', this.onAddButton, this, true);
      lastCell.appendChild(this.addButton);
		
		// Create a "Cancel" Button
		this.deleteButton = inputEx.cn('input', {type:'button',value:inputEx.messages.cancelText}, null, null);
		Event.addListener(this.deleteButton, 'click', this.onCancelButton, this, true);
      lastCell.appendChild(this.deleteButton);

		// Disable the "Insert Button"
		this.insertButton.disabled = true ;
	},
	
	/**
    * When saving the Dialog (option insertWithDialog)
    */
   onDialogSave: function() {
		var record, newvalues;
		
		// Validate the Form
	  	if ( !this.dialog.getForm().validate() ) return ;
	
		// Insert a new row
      this.datatable.addRow({});

		// Set the Selected Record
		var rowIndex = this.datatable.getRecordSet().getLength() - 1;
		this.selectedRecord = rowIndex;
		
		// Update the row
		newvalues = this.dialog.getValue();
		this.datatable.updateRow( this.selectedRecord , newvalues );
		
		// Get the new record
		record = this.datatable.getRecord(this.selectedRecord);
					
		// Fire the add event
      this.itemAddedEvt.fire(record);
		
		// Hide the dialog 
      this.dialog.hide();
   },
   
	/**
	 * When clicking "Add" button to save a new row
	 */
	onAddButton: function(e) {
		Event.stopEvent(e);	
		var target = Event.getTarget(e),
      record = this.datatable.getRecord(target),
		field, requiredFields = [];

		for(var i=0, fieldsLength = this.options.fields.length; i<fieldsLength; i++){
			field = this.options.fields[i];
			
			// Retro-compatibility with inputParms
         if (lang.isObject(field.inputParams)) {
            
            if( !lang.isUndefined(field.inputParams.required) ){
   				if( lang.isUndefined(record.getData(field.inputParams.name)) ){
   					requiredFields.push(field.inputParams.label);
   				}
   			}

         // New prefered way to set options of a field
         } else {
            
            if( !lang.isUndefined(field.required) ){
   				if( lang.isUndefined(record.getData(field.name)) ){
   					requiredFields.push(field.label);
   				}
   			}
         }
         
			
		}
		
		//If not all the required fields are set
		if(requiredFields.length > 0){
			this.requiredFieldsEvt.fire(requiredFields);			
			return;
		}
		
		this.addButton.value = inputEx.messages.loadingText;
		this.addButton.disabled = true;
		this.itemAddedEvt.fire(record);
	},
	
	/**
	 * When clicking "Cancel" button to cancel a new row
	 */
	onCancelButton: function(e) {
		Event.stopEvent(e);
		var target = Event.getTarget(e);	
		this.datatable.deleteRow(target);
    	this.insertButton.disabled = false ;
	},

	/**
	 * Validate the new record's row : 
	 * You need to call this function when you really added the item with an id
	 * Ie if you trigger an Ajax request to insert your record into database,
	 * you trigger this function only if your request didn't failed
	 */
	onAddSuccess: function(record, oData){

		if(this.options.insertWithDialog) {
			this.datatable.updateRow(record, oData);
			return;
		}
		
		var recordNode = Dom.get(this.datatable.getLastSelectedRecord()),
		childNodes = recordNode.childNodes,
		childNodeIndex = childNodes.length - 1,
		innerDivNode = childNodes[childNodeIndex].childNodes[0];
		
		// Update Row with new record
		this.datatable.updateRow(record, oData);
		// Update the ADD / CANCEL buttons to "delete" text
		innerDivNode.innerHTML = inputEx.messages.deleteText;
		// Unselect Row and enable "Insert" button again
		this.datatable.unselectRow(recordNode);
		this.insertButton.disabled = false ;
	},
   
	/**
	 * When Failed to Add Row
	 */
	onAddFailure: function(){
	
		if(this.options.insertWithDialog) {
			this.datatable.deleteRow(this.selectedRecord);
			return;
		}
		
		this.addButton.value = inputEx.messages.addButtonText;
		this.addButton.disabled = false;
	},
	
	/**
	 * When modifying a row
	 */
	onModifyItem: function(record, oArgs){
		var itemContainer = oArgs.editor.getTdEl().childNodes[0];
		// Add CSS
		Dom.addClass(itemContainer, "inputEx-dtInPlaceEdit-onModifyItem");
		this.itemModifiedEvt.fire(record);
	},
	
	/**
	 * When successfully modified a row
	 */
	onModifySuccess: function(record, oData) {
		var nodes = this.datatable.getElementsByClassName("inputEx-dtInPlaceEdit-onModifyItem");
		
		// Remove CSS
		for(i=0,nodesLength = nodes.length; i<nodesLength; i++){
			Dom.removeClass(nodes[i], "inputEx-dtInPlaceEdit-onModifyItem");
		}
		
		// If we want to update additional columns
		if( !lang.isUndefined(oData) ) {
			// Update Row with new record
			this.datatable.updateRow(record, oData);
		}
		
	}

});




/**
 * The CellEditor class provides functionality for inline editing in datatables
 * using the inputEx field definition.
 *
 * @class inputEx.widget.CellEditor
 * @extends YAHOO.widget.BaseCellEditor 
 * @constructor
 * @param {Object} inputExFieldDef InputEx field definition object
 */
inputEx.widget.CellEditor = function(inputExFieldDef) {
    this._inputExFieldDef = inputExFieldDef;
    this._sId = "yui-textboxceditor" + YAHOO.widget.BaseCellEditor._nCount;
	 YAHOO.widget.BaseCellEditor._nCount++;
    inputEx.widget.CellEditor.superclass.constructor.call(this, "inputEx", {disableBtns:false});
};

// CellEditor extends BaseCellEditor
lang.extend(inputEx.widget.CellEditor, YAHOO.widget.BaseCellEditor,{
	
	
   /**
    * Render the inputEx field editor
    */
   renderForm : function() {
      // Build the inputEx field
      this._inputExField = inputEx(this._inputExFieldDef);
      this.getContainerEl().appendChild(this._inputExField.getEl());
		
		// Locals for Save/Cancel Buttons
		this.LABEL_SAVE = inputEx.messages.saveText;
		this.LABEL_CANCEL = inputEx.messages.cancelText;
   },

   /**
    * Resets CellEditor UI to initial state.
    */
   resetForm : function() {
   	this._inputExField.clear();
		this._inputExField.setValue(this.value);
   },
	
   /**
    * Sets focus in CellEditor.
    */
   focus : function() {
      this._inputExField.focus();
   },

   /**
    * Returns new value for CellEditor.
    */
   getInputValue : function() {	
      return this._inputExField.getValue();
   },

	/**
	 * When clicking the save button but also when clicking out of the cell
	 */
	save: function() {
		// Save only if cell is validated
		if(this._inputExField.validate()) {	    
			inputEx.widget.CellEditor.superclass.save.call(this);	    
		}
	},
	
	cancel: function() {
		inputEx.widget.CellEditor.superclass.cancel.call(this);
	}
	

});

// Copy static members to CellEditor class
lang.augmentObject(inputEx.widget.CellEditor, YAHOO.widget.BaseCellEditor);

})();