var logicGatesLang = {	
	languageName: "logicGates",
	modules: [
		{
			"name": "AND",
			"category": "gate",
			"description": "AND Gate with 2 inputs",
			"container" : {
				"xtype":"LogicContainer", 
				"icon": "../logicGates/images/gate_and.png",
				"image": "../logicGates/images/gate_and.png",
  				"terminals": [
  					{"name": "_INPUT1", "direction": [-1,0], "offsetPosition": {"left": -16, "top": -2 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
  					{"name": "_INPUT2", "direction": [-1,0], "offsetPosition": {"left": -16, "top": 25 },"ddConfig": {"type": "input","allowedTypes": ["output"]}},
  					{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 65, "top": 12 },"ddConfig": {"type": "output","allowedTypes": ["input"]}}
  				]
			}
		},
		{
		  "name": "OR",	
			"category": "gate",
			"description": "OR Gate with 2 inputs",
			"container": {
		   		"xtype":"LogicContainer", 
		   		"icon": "../logicGates/images/gate_or.png",
		   		"image": "../logicGates/images/gate_or.png",
					"terminals": [
						{"name": "_INPUT1", "direction": [-1,0], "offsetPosition": {"left": -16, "top": -2 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
						{"name": "_INPUT2", "direction": [-1,0], "offsetPosition": {"left": -16, "top": 25 },"ddConfig": {"type": "input","allowedTypes": ["output"]}},
						{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 65, "top": 12 },"ddConfig": {"type": "output","allowedTypes": ["input"]}}
					]
			}
		},
		{
		  "name": "NOT",	
			"category": "gate",
			"description": "NOT Gate with 1 input",
		  "container": {
				"xtype":"LogicContainer", 
			   "icon": "../logicGates/images/gate_not.png",
			   "image": "../logicGates/images/gate_not.png",
				"terminals": [
					{"name": "_INPUT", "direction": [-1,0], "offsetPosition": {"left": -21, "top": 12 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
					{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 70, "top": 12 },"ddConfig": {"type": "output","allowedTypes": ["input"]}}
				]
			}
		},
		{
		   "name": "NAND",
			"category": "gate",
			"description": "NAND Gate with 2 inputs",
		   "container": {
			   "xtype":"LogicContainer", 
			   "icon": "../logicGates/images/gate_nand.png",
			   "image": "../logicGates/images/gate_nand.png",
				"terminals": [
					{"name": "_INPUT1", "direction": [-1,0], "offsetPosition": {"left": -16, "top": -2 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
					{"name": "_INPUT2", "direction": [-1,0], "offsetPosition": {"left": -16, "top": 25 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
					{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 65, "top": 12 }, "ddConfig": {"type": "output","allowedTypes": ["input"]}}
				]
			}
		},
		{
		   "name": "XOR",
			"category": "gate",
			"description": "XOR Gate with 2 inputs",
		   "container": {
		   	"xtype":"LogicContainer", 
		   	"icon": "../logicGates/images/gate_xor.png",
		   	"image": "../logicGates/images/gate_xor.png",
				"terminals": [
					{"name": "_INPUT1", "direction": [-1,0], "offsetPosition": {"left": -16, "top": -2 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
					{"name": "_INPUT2", "direction": [-1,0], "offsetPosition": {"left": -16, "top": 25 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 },
					{"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"left": 65, "top": 12 },"ddConfig": {"type": "output","allowedTypes": ["input"]}}
				]
			}
		},
		{
			"name": "Lightbulb",
			"category": "output",
			"description": "Lamp display",
			"container" : {
				"xtype":"LightbulbContainer", 
				"icon": "../logicGates/images/lightbulb_off.png",
				"image": "../logicGates/images/lightbulb_off.png",
  				"terminals": [ {"name": "_INPUT", "direction": [0,1], "offsetPosition": {"left": 5, "bottom": 20 },"ddConfig": {"type": "input","allowedTypes": ["output"]}, "nMaxWires": 1 } ]
			}
		},
		{
			"name": "Switch",
			"category": "input",
			"description": "Switch",
			"container" : {
				"xtype":"SwitchContainer", 
				"icon": "../logicGates/images/switch_off.png",
				"image": "../logicGates/images/switch_off.png",
  				"terminals": [ {"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"right": 6, "top": 11 },"ddConfig": {"type": "output","allowedTypes": ["input"]}} ]
			}
		},
		{
			"name": "Clock",
			"category": "input",
			"description": "Clock",
			"container" : {
				"xtype":"ClockContainer", 
				"icon": "../logicGates/images/clock_off.png",
				"image": "../logicGates/images/clock_off.png",
  				"terminals": [ {"name": "_OUTPUT", "direction": [1,0], "offsetPosition": {"right": 7, "top": 5 },"ddConfig": {"type": "output","allowedTypes": ["input"]}} ]
			}
		}
	]
};


/********
 * CODE
 ********/

// General logic container
LogicContainer = function(opts, layer) {
	LogicContainer.superclass.constructor.call(this, opts, layer);
	this.logicInputValues = [];
};
YAHOO.lang.extend(LogicContainer, WireIt.ImageContainer, {

	/** 
    * @property xtype
    * @description String representing this class for exporting as JSON
    * @default "WireIt.LogicContainer"
    * @type String
    */
   xtype: "LogicContainer",
	
	setInput: function(bStatus,term) {
		this.logicInputValues[term.name] = bStatus;
		
		if(this.title == "AND") {
			this.setLogic( this.logicInputValues["_INPUT1"] && this.logicInputValues["_INPUT2"]  );
		}
		else if (this.title == "OR") {
			this.setLogic( this.logicInputValues["_INPUT1"] || this.logicInputValues["_INPUT2"]  );
		}
		else if (this.title == "NOT") {
			this.setLogic(!this.logicInputValues["_INPUT"]);
		}
		else if (this.title == "NAND") {
			this.setLogic( !(this.logicInputValues["_INPUT1"] && this.logicInputValues["_INPUT2"])  );
		}
		else if (this.title == "XOR") {
			this.setLogic( (!this.logicInputValues["_INPUT1"] && this.logicInputValues["_INPUT2"]) ||
			  					(this.logicInputValues["_INPUT1"] && !this.logicInputValues["_INPUT2"]) );
		}
	},
	
	setLogic: function(bStatus) {
		this.status = bStatus;
		
		// Set the image
		if(this.imageName) {
			var image = this.imageName+"_"+(bStatus ? "on" : "off")+".png";
			YAHOO.util.Dom.setStyle(this.bodyEl, "background-image", "url(images/"+image+")");
		}
		
		// trigger the output wires !
		for(var i = 0 ; i < this.terminals.length ; i++) {
			var term = this.terminals[i];
			if(term.name == "_OUTPUT") {
				for(var j = 0 ; j < term.wires.length ; j++) {
					var wire = term.wires[j];
					var otherTerm = wire.getOtherTerminal(term);
					if(otherTerm.container) {
						otherTerm.container.setInput(bStatus, otherTerm);
					}
					wire.color = bStatus ? "rgb(173,216,230)" : "rgb(255,255,255)";
					wire.redraw();
				}
			}
		}
	},
	switchStatus: function() {
		this.setLogic(!this.status);
	}
});


ClockContainer = function(opts, layer) {
	ClockContainer.superclass.constructor.call(this, opts, layer);
	this.imageName = "clock";	
	var that = this;
	setInterval(function() { that.switchStatus();	}, 800);
};
YAHOO.lang.extend(ClockContainer, LogicContainer, {
	xtype: "ClockContainer"
});

SwitchContainer = function(opts, layer) {
	SwitchContainer.superclass.constructor.call(this, opts, layer);
	this.imageName = "switch";
	YAHOO.util.Event.addListener(this.bodyEl, "click", this.switchStatus, this, true);
};
YAHOO.lang.extend(SwitchContainer, LogicContainer, {
	xtype: "SwitchContainer"
});

LightbulbContainer = function(opts, layer) {
	LightbulbContainer.superclass.constructor.call(this, opts, layer);
	this.imageName = "lightbulb";
};
YAHOO.lang.extend(LightbulbContainer, LogicContainer, {
	xtype: "LightbulbContainer",
	
	setInput: function(bStatus,term) {
		this.setLogic(bStatus);
	}
	
});

YAHOO.util.Event.onDOMReady( function() { 
	try {
		logicGates = new WireIt.WiringEditor(logicGatesLang); 
	}catch(ex) {
		alert(ex);
	}
});


