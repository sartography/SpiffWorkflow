(function() {
	
   var lang = YAHOO.lang;
	
/**
 * Wrapper for the TinyMCE Editor
 * @class inputEx.TinyMCEField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *   <li>opts: the options to be added when calling the TinyMCE constructor</li>
 * </ul>
 */
inputEx.TinyMCEField = function(options) {
   inputEx.TinyMCEField.superclass.constructor.call(this,options);
};
lang.extend(inputEx.TinyMCEField, inputEx.Field, {   
   /**
    * Set the default values of the options
    * @param {Object} options Options object as passed to the constructor
    */
  	setOptions: function(options) {
  	   inputEx.TinyMCEField.superclass.setOptions.call(this, options);
  	   
  	   this.options.opts = options.opts || {};
   },
   
	/**
	 * Render the field using the YUI Editor widget
	 */	
	renderComponent: function() {
	   if(!inputEx.TinyMCEfieldsNumber) { inputEx.TinyMCEfieldsNumber = 0; }
	   
	   var id = "inputEx-TinyMCEField-"+inputEx.TinyMCEfieldsNumber;
		this.id = id;
	   var attributes = {id:id, className: "mceAdvanced"};
      if(this.options.name) { attributes.name = this.options.name; }

	   this.el = inputEx.cn('textarea', attributes);
	   
	   inputEx.TinyMCEfieldsNumber += 1;
	   this.fieldContainer.appendChild(this.el);
	

		var defaultOpts = {
			mode : "textareas",
			language : "fr",
			theme : "advanced",
			
			plugins: "paste", // past plugin for raw text pasting
			paste_auto_cleanup_on_paste : true,
			paste_remove_styles: true,
			paste_remove_styles_if_webkit: true,
			paste_strip_class_attributes: true,
			theme_advanced_buttons1 : "formatselect,fontselect,fontsizeselect,|,bold,italic,underline,strikethrough,|,forecolor,backcolor",
			theme_advanced_buttons2 : "justifyleft,justifycenter,justifyright,justifyfull,|,outdent,indent,blockquote,hr,|,bullist,numlist,|,link,unlink,image,|,removeformat,code,|,undo,redo",
			theme_advanced_buttons3: "",
			theme_advanced_toolbar_location : "top",
			theme_advanced_toolbar_align : "left",
			height: "200",
			verify_html : true,
			cleanup_on_startup : true,
			cleanup:true
		};
		
		this.editor = new tinymce.Editor(this.id, defaultOpts);

		// Adds an observer to the onInit event using the render method
		this.editorReady = false;		
		var that = this;
		this.editor.onInit.add(function(ed) {
			that.editorReady = true;
		});

		this.editor.render();
	},
	
	/**
	 * Set the html content
	 * @param {String} value The html string
	 * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
	 */
	setValue: function(value, sendUpdatedEvt) {
		
	   if(this.editorReady) {
			this.editor.setContent(value, {format : 'raw'});
      }
		else {
			this.editor.onInit.add(function(ed) {
				ed.setContent(value, {format : 'raw'});
			});
		}
	   
   	if(sendUpdatedEvt !== false) {
   	   // fire update event
         this.fireUpdatedEvt();
      }
	},
	
	/**
	 * Get the html string
	 * @return {String} the html string
	 */
	getValue: function() {
		if(this.editorReady) {
			return this.editor.getContent();
		}
		else {
		 	return null;	
		}
	}
	
	
});
	
// Register this class as "tinymce" type
inputEx.registerType("tinymce", inputEx.TinyMCEField, []);
	
})();