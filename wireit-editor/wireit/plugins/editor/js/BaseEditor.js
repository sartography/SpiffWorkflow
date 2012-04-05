/**
 * WireIt editor
 * @module editor-plugin
 */
(function() {
    var util = YAHOO.util,lang = YAHOO.lang;
    var Event = util.Event, Dom = util.Dom, Connect = util.Connect,JSON = lang.JSON,widget = YAHOO.widget;

/**
 * The BaseEditor class provides a full page interface 
 * @class BaseEditor	
 * @namespace WireIt
 * @constructor
 * @param {Object} options (layoutOptions,propertiesFields,accordionViewParams)
 */
WireIt.BaseEditor = function(options) {
	
	/**
    * Container DOM element
    * @property el
    */
   this.el = Dom.get(options.parentEl);
	
	// set the default options
   this.setOptions(options);

   // Rendering
   this.render();
	
};

/**
 * Default options for the BaseEditor
 */
WireIt.BaseEditor.defaultOptions = {
	layoutOptions: {
	 	units: [
	   	{ position: 'top', height: 57, body: 'top'},
	      { position: 'left', width: 200, resize: true, body: 'left', gutter: '5px', collapse: true, 
	        collapseSize: 25, header: 'Modules', scroll: true, animate: true },
	      { position: 'center', body: 'center', gutter: '5px' },
	      { position: 'right', width: 320, resize: true, body: 'right', gutter: '5px', collapse: true, 
	        collapseSize: 25, /*header: 'Properties', scroll: true,*/ animate: true }
	   ]
	},

	propertiesFields: [
		{"type": "string", "name": "name", label: "Title", typeInvite: "Enter a title" },
		{"type": "text", "name": "description", label: "Description", cols: 30, rows: 4}
	],
	
	accordionViewParams: {
		collapsible: true, 
		expandable: true, // remove this parameter to open only one panel at a time
		width: 'auto', 
		expandItem: 0, 
		animationSpeed: '0.3', 
		animate: true, 
		effect: YAHOO.util.Easing.easeBothStrong
	}
};

WireIt.BaseEditor.prototype = {

	/**
	 * @method setOptions
	 * @param {Object} options
	 */
	setOptions: function(options) {

	    /**
	     * @property options
	     * @type {Object}
	     */
	    this.options = {};
	
		 // inputEx configuration of fields in the properties panel
	    this.options.propertiesFields = options.propertiesFields || WireIt.BaseEditor.defaultOptions.propertiesFields;

		 // YUI layout options
	    this.options.layoutOptions = options.layoutOptions || WireIt.BaseEditor.defaultOptions.layoutOptions;
		
		 // AccordionView
	 	 this.options.accordionViewParams = options.accordionViewParams || WireIt.BaseEditor.defaultOptions.accordionViewParams;
	},
	
	/**
	 * Render the layout & panels
	 */
  	render: function() {

		 // Render the help panel
	    this.renderHelpPanel();

	    /**
	     * @property layout
	     * @type {YAHOO.widget.Layout}
	     */
	    this.layout = new widget.Layout(this.el, this.options.layoutOptions);
	    this.layout.render();

		 // Right accordion
	    this.renderPropertiesAccordion();

	    // Render buttons
	    this.renderButtons();

	 	 // Saved status
		 this.renderSavedStatus();

	    // Properties Form
	    this.renderPropertiesForm();

  },

	/**
	 * Render the help dialog
	 */
	renderHelpPanel: function() {
		/**
	     * @property helpPanel
	     * @type {YAHOO.widget.Panel}
	     */
	    this.helpPanel = new widget.Panel('helpPanel', {
	        fixedcenter: true,
	        draggable: true,
	        visible: false,
	        modal: true
	     });
	     this.helpPanel.render();
	},

	/**
	 * Render the alert panel
	 */
 	renderAlertPanel: function() {
		
 	 /**
     * @property alertPanel
     * @type {YAHOO.widget.Panel}
     */
		this.alertPanel = new widget.Panel('WiringEditor-alertPanel', {
         fixedcenter: true,
         draggable: true,
         width: '500px',
         visible: false,
         modal: true
      });
      this.alertPanel.setHeader("Message");
      this.alertPanel.setBody("<div id='alertPanelBody'></div><button id='alertPanelButton'>Ok</button>");
      this.alertPanel.render(document.body);
		Event.addListener('alertPanelButton','click', function() {
			this.alertPanel.hide();
		}, this, true);
	},
	
	 /**
	  * Toolbar
	  * @method renderButtons
	  */
	 renderButtons: function() {
	    var toolbar = Dom.get('toolbar');
	    // Buttons :
	    var newButton = new widget.Button({ label:"New", id:"WiringEditor-newButton", container: toolbar });
	    newButton.on("click", this.onNew, this, true);

	    var loadButton = new widget.Button({ label:"Load", id:"WiringEditor-loadButton", container: toolbar });
	    loadButton.on("click", this.load, this, true);

	    var saveButton = new widget.Button({ label:"Save", id:"WiringEditor-saveButton", container: toolbar });
	    saveButton.on("click", this.onSave, this, true);

	    var deleteButton = new widget.Button({ label:"Delete", id:"WiringEditor-deleteButton", container: toolbar });
	    deleteButton.on("click", this.onDelete, this, true);

	    var helpButton = new widget.Button({ label:"Help", id:"WiringEditor-helpButton", container: toolbar });
	    helpButton.on("click", this.onHelp, this, true);
	 },


	/**
	 * @method renderSavedStatus
	 */
	renderSavedStatus: function() {
		this.savedStatusEl = WireIt.cn('div', {className: 'savedStatus', title: 'Not saved'}, {display: 'none'}, "*");
		Dom.get('toolbar').appendChild(this.savedStatusEl);
	},

	 /**
	  * @method onSave
	  */
	 onSave: function() {
	    this.save();
	 },

	/**
	 * Save method (empty)
	 */
	save: function() {
		// override
	},

	/**
	 * Displays a message
	 */
	alert: function(txt) {
		if(!this.alertPanel){ this.renderAlertPanel(); }
		Dom.get('alertPanelBody').innerHTML = txt;
		this.alertPanel.show();
	},

	 /**
	  * Create a help panel
	  * @method onHelp
	  */
	 onHelp: function() {
	    this.helpPanel.show();
	 },

	
	/**
	 * Render the accordion using yui-accordion
  	 */
	renderPropertiesAccordion: function() {
		this.accordionView = new YAHOO.widget.AccordionView('accordionView', this.options.accordionViewParams);
	},
 
	 /**
	  * Render the properties form
	  * @method renderPropertiesForm
	  */
	 renderPropertiesForm: function() {
	    this.propertiesForm = new inputEx.Group({
	       parentEl: YAHOO.util.Dom.get('propertiesForm'),
	       fields: this.options.propertiesFields
	    });

		this.propertiesForm.updatedEvt.subscribe(function() {
			this.markUnsaved();
		}, this, true);
	 },

	/** 
	 * Hide the save indicator
	 */
	markSaved: function() {
		this.savedStatusEl.style.display = 'none';
	},
	
	/** 
	 * Show the save indicator
	 */
	markUnsaved: function() {
		this.savedStatusEl.style.display = '';
	},

	/** 
	 * Is saved ?
	 */
	isSaved: function() {
		return (this.savedStatusEl.style.display == 'none');
	}
	
};


})();