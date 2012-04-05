(function() {
	
   var lang = YAHOO.lang;
	
/**
 * Wrapper for the Rich Text Editor from YUI
 * @class inputEx.RTEField
 * @extends inputEx.Field
 * @constructor
 * @param {Object} options Added options:
 * <ul>
 *   <li>opts: the options to be added when calling the RTE constructor (see YUI RTE)</li>
 *   <li>editorType: if == 'simple', the field will use the SimpleEditor. Any other value will use the Editor class.</li>
 * </ul>
 */
inputEx.RTEField = function(options) {
   inputEx.RTEField.superclass.constructor.call(this,options);
};
lang.extend(inputEx.RTEField, inputEx.Field, {   
   /**
    * Set the default values of the options
    * @param {Object} options Options object as passed to the constructor
    */
  	setOptions: function(options) {
  	   inputEx.RTEField.superclass.setOptions.call(this, options);
  	   
  	   this.options.opts = options.opts || {};
  	   this.options.editorType = options.editorType;
   },
   
	/**
	 * Render the field using the YUI Editor widget
	 */	
	renderComponent: function() {
	   if(!inputEx.RTEfieldsNumber) { inputEx.RTEfieldsNumber = 0; }
	   
	   var id = "inputEx-RTEField-"+inputEx.RTEfieldsNumber;
	   var attributes = {id:id};
      if(this.options.name) { attributes.name = this.options.name; }
      
	   this.el = inputEx.cn('textarea', attributes);
	   
	   inputEx.RTEfieldsNumber += 1;
	   this.fieldContainer.appendChild(this.el);
	
	   //This is the default config
	   var _def = {
	       height: '300px',
	       width: '580px',
	       dompath: true,
	       filterWord:true // get rid of the MS word junk
	   };
	   //The options object
	   var o = this.options.opts;
	   //Walk it to set the new config object
	   for (var i in o) {
	        if (lang.hasOwnProperty(o, i)) {
	            _def[i] = o[i];
	        }
	   }
	   //Check if options.editorType is present and set to simple, if it is use SimpleEditor instead of Editor
	   var editorType = ((this.options.editorType && (this.options.editorType == 'simple')) ? YAHOO.widget.SimpleEditor : YAHOO.widget.Editor);
	
	   //If this fails then the code is not loaded on the page
	   if (editorType) {
	       this.editor = new editorType(id, _def);
	       this.editor.render();
	   } else {
	    alert('Editor is not on the page');
	   }
	   
	   
	   /**
   	 * Filters out msword html comments, classes, and other junk
   	 * (complementary with YAHOO.widget.SimpleEditor.prototype.filter_msword, when filterWord option is true)
   	 * @param {String} value The html string
   	 * @return {String} The html string
   	 */
   	this.editor.filter_msword = function(html) {
   	   
   	   html = editorType.prototype.filter_msword.call(this,html);
   	   
   	   // if we don't filter ms word junk
   	   if (!this.get('filterWord')) {
   	      return html;
   	   }

   	   html = html.replace( /<!--[^>][\s\S]*-->/gi, ''); // strip (meta-)comments
         html = html.replace( /<\/?meta[^>]*>/gi, ''); // strip meta tags
         html = html.replace( /<\/?link[^>]*>/gi, ''); // strip link tags
         html = html.replace( / class=('|")?MsoNormal('|")?/gi, ''); // strip MS office class
         html = YAHOO.lang.trim(html); // trim spaces
         
         return html;
   	};
   	
	},
	
	/**
	 * Set the html content
	 * @param {String} value The html string
	 * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
	 */
	setValue: function(value, sendUpdatedEvt) {
	   if(this.editor) {
	      var iframeId = this.el.id+"_editor";
	      
	      // if editor iframe not rendered
	      if (!YAHOO.util.Dom.get(iframeId)) {
	         // put value in textarea : will be processed by this.editor._setInitialContent (clean html, etc...)
	         this.el.value = value;
	         
	      } else {
	         this.editor.setEditorHTML(value);
         }
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
	   
	   var html;
	   
	   try {
	      // trigger HTML cleaning (strip MS word or internal junk)
	      // + save to hidden textarea (required for classic HTML 'submit')
	      html = this.editor.saveHTML();
	      return html;
	   }
	   catch(ex) { return null; }
	}
	
	
});
	
// Register this class as "html" type
inputEx.registerType("html", inputEx.RTEField, []);
	
})();