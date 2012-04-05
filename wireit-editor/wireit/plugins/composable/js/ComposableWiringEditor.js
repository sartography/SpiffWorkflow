/**
 * Extend the WiringEditor with composable wirings
 * @module composable-plugin
 */

/**
 * The ComposableWiringEditor 
 *
 * @class ComposableWiringEditor
 * @extends WireIt.ComposableWiringEditor
 * @constructor
 */
WireIt.ComposableWiringEditor = function(options) {
	
	// Add the "input" and "output" modules
	options.modules = WireIt.ComposableWiringEditor.modules.concat(options.modules);
	
   WireIt.ComposableWiringEditor.superclass.constructor.call(this, options);
};

/**
 * Default "input" and "output" modules
 * @static
 */
WireIt.ComposableWiringEditor.modules = [
	{
      "name": "input",
      "container": {
         "xtype": "WireIt.FormContainer",
   		"title": "input",
   		"fields": [
   			{"type": "type", "label": "Value", "name": "input", "wirable": false, "value": { "type":"string", "typeInvite": "input name" } }
   		],
   		"terminals": [
			   {"name": "out", "direction": [0,1], "offsetPosition": {"left": 86, "bottom": -15}, "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
             }
            }
		   ]
      }
   },
   
   {
      "name": "output",
      "container": {
         "xtype": "WireIt.FormContainer",
   		"title": "output",
   		"fields": [ 
   			{"type": "string", "label": "name", "name": "name", "wirable": false }
   		],
	   	"terminals": [
   		   {"name": "in", "direction": [0,-1], "offsetPosition": {"left": 82, "top": -15 }, "ddConfig": {
                "type": "input",
                "allowedTypes": ["output"]
             },
             "nMaxWires": 1
            }
   		]
      }
   }
];


YAHOO.lang.extend(WireIt.ComposableWiringEditor, WireIt.WiringEditor, {

	/**
	 * @property composedCategory
	 */
   composedCategory: "Composed",

	/**
	 * Customize the load success handler for the composed module list
	 */
	onLoadSuccess: function(wirings) {
		
		
		// Reset the internal structure
		this.pipes = wirings;
		this.pipesByName = {};
	
		// Build the "pipesByName" index
		for(var i = 0 ; i < this.pipes.length ; i++) {
          this.pipesByName[ this.pipes[i].name] = this.pipes[i];
		}
		
		//  Customize to display composed module in the left list
		this.updateComposedModuleList();
	
    	this.updateLoadPanelList();

		// Check for autoload param and display the loadPanel otherwise
		if(!this.checkAutoLoad()) { 
    		this.loadPanel.show();
		}
		
	},
	
	/**
	 * All the saved wirings are reusable modules :
	 */
	updateComposedModuleList: function() {
		
		// Remove all previous module with the ComposedModule class
		var el = YAHOO.util.Dom.get("module-category-Composed");
		if( el ) {
			// Purge element (remove listeners on el and childNodes recursively)
	      YAHOO.util.Event.purgeElement(el, true);
			el.innerHTML = "";
		}
		
		
		if(YAHOO.lang.isArray(this.pipes)) {
	       for(var i = 0 ; i < this.pipes.length ; i++) {
	          var module = this.pipes[i];
	
				 var m = {
					name: module.name,
					category: this.composedCategory,
					container: {
		            "xtype": "WireIt.ComposedContainer",
		            "title": module.name,
				  		"wiring": this.pipes[i]
		         }
				 };
				 YAHOO.lang.augmentObject(m, this.pipes[i]);
				
				 this.modulesByName[module.name] = m;
					
				 this.addModuleToList(m);
			}
		}
		
	}
	
});
