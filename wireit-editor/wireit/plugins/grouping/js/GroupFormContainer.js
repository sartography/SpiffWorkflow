(function() {
   
   var util = YAHOO.util,lang = YAHOO.lang;
   var Dom = util.Dom, Event = util.Event, CSS_PREFIX = "WireIt-";

/**
 * Class used to build a container with inputEx forms
 * @class FormContainer
 * @namespace WireIt
 * @extends WireIt.Container
 * @constructor
 * @param {Object}   options  Configuration object (see properties)
 * @param {WireIt.Layer}   layer The WireIt.Layer (or subclass) instance that contains this container
 */
WireIt.GroupFormContainer = function(options, layer) {
   /*var fieldConfigs = WireIt.GroupUtils.fieldConfigsFromModules(options.groupConfig.modules, options.getBaseConfigFunction);
   
   var intermediate = WireIt.GroupUtils.generateFields(fieldConfigs, {fields: {}, terminals: {}}, {fields: {"0email" : true}, terminals: {}}); //TODO: wrong arguments
   options.fields = intermediate.fields;
   var terminalConfigs = WireIt.GroupUtils.terminalConfigsFromModules(options.groupConfig.modules, options.getBaseConfigFunction);
   
   options.terminals = WireIt.GroupUtils.generateTerminals(terminalConfigs , {fields: {}, terminals: {}}, {fields: {}, terminals: {}}, intermediate.usedTerminalNames);
    */ 
   WireIt.GroupFormContainer.superclass.constructor.call(this, options, layer);
   this.getBaseConfig = this.options.getBaseConfigFunction;
   
   this.positionTerminals();
};

YAHOO.lang.extend(WireIt.GroupFormContainer, WireIt.FormContainer, {
   
   /**
    * @method setOptions
    */
   setOptions: function(options) {
      WireIt.GroupFormContainer.superclass.setOptions.call(this, options);
      
      this.options.getBaseConfigFunction = options.getBaseConfigFunction
      this.options.groupConfig = options.groupConfig;
   },

   /**
    * The render method is overrided to call renderForm
    * @method render
    */
   render: function() {
      WireIt.GroupFormContainer.superclass.render.call(this);
      this.renderExpand();
   },

    positionTerminals: function()
    {
	var terminals = {};
	
	for (var i in this.options.terminals)
	{
	    var elem = this.options.terminals[i];
	    
	    var side = elem.side;
	    if (!lang.isValue(side))
		side = "top";

	    if (!lang.isArray(terminals[side]))
		terminals[side] = [];
		
	    terminals[side].push(elem);
	}

	var terminal_width = 30;

	var getRange = function(N) { return terminal_width * (N-1);  };

	var positionByNumber = function(n,N, size) {
			// n is expected to run from 0 to N-1, where N is the number of terminals on an edge
			var range = getRange(N);
			var half_range = range / 2;
			var pos = size / 2;
			pos -= half_range - n*terminal_width;
			var offset = terminal_width / 2;
			return pos-offset; // position in centre of terminal
		};

	var height = this.el.offsetHeight;
	var width = this.el.offsetWidth;	    
	var horizontalMax = Math.max(WireIt.GroupUtils.valueOr(terminals["top"], []).length, WireIt.GroupUtils.valueOr(terminals["bottom"], []).length);
	var verticalMax = Math.max(WireIt.GroupUtils.valueOr(terminals["left"], []).length, WireIt.GroupUtils.valueOr(terminals["right"], []).length);

	if (height < getRange(verticalMax))
	{
	    this.bodyEl.style.minHeight = new String(getRange(verticalMax)) + "px";
	    height = this.el.offsetHeight;
	}

	if (width < getRange(horizontalMax))
	{
	    this.bodyEl.style.minWidth = new String(getRange(horizontalMax)) + "px";
	    width = this.el.offsetWidth;
	}

	for (var side in terminals)
	{
	    var sTerminals = terminals[side];
	    var count = sTerminals.length;
	    
	    var variable, fixed, size;
	    
	    
	    if (side == "left" || side == "right")
	    {
		variable = "top";
		size = height;
	    } else
	    {
		variable = "left";
		size = width;
	    }
	    
	    fixed = side;
	    
	    for (var i = 0; i < count; i++)
	    {
		var terminal = this.getTerminal(sTerminals[i].name);
		var pos = new Object();
		pos[fixed] = -15;
		pos[variable] = new String(positionByNumber(i, count, size));
		    
		terminal.setPosition(pos);
	    }
	}
    },

   renderExpand: function() {
        this.unGroupButton = WireIt.cn('div', {className: 'WireIt-Container-ungroupbutton'} );
        Event.addListener(this.unGroupButton, "click", this.expand, this, true);

        this.ddHandle.appendChild(this.unGroupButton)
    },

    expand: function() 
    {
	//For each module add it to the layer
	//For each wire wire up the new containers
	//For each internal group add to layer groups, remap from serialised 
	//For each wire on group container make wire to new containers
	//Remove group container
	
	//var expandedContainers = WireIt.GroupUtils.expand(this.options.groupConfig, this, this.layer);
	
	var mapModuleId = function(offset, moduleId)
	    {
		return parseInt(offset)+parseInt(moduleId);
	    };
	
	var offset = this.layer.containers.length;
	
	var thisConfig = this.getConfig();
	var position = [thisConfig.position[0], thisConfig.position[1]];
	
	var expandedContainers = [];
	
	for (var mI in this.options.groupConfig.modules)
	{
	    var m = this.options.groupConfig.modules[mI];
	    
	    var baseContainerConfig = this.getBaseConfig(m.name);
	    var newConfig = YAHOO.lang.JSON.parse( YAHOO.lang.JSON.stringify( m.config ) ) //TODO: nasty deep clone, probably breaks if you have DOM elements in your config or something
	    YAHOO.lang.augmentObject(newConfig , baseContainerConfig);
	    newConfig.title = m.name;
	    var newPos = this.translatePosition(newConfig.position, position);
	    newConfig.position = newPos;
	    var container = this.layer.addContainer(newConfig);
	    //Dom.addClass(container.el, "WiringEditor-module-"+m.name);
	    container.setValue(m.value);
	    
	    expandedContainers.push(container);
	}

	var deserialise = function(sGroup, groupToSet)
	{
	    var group = groupToSet;
	    if (!lang.isValue(group))
		group = new WireIt.Group(this.group.grouper, this.layer)
		
	    group.properties = sGroup.properties; //TODO: copy rather than reference?
	    
	    if (lang.isValue(sGroup.groupContainer))
	    {
		group.groupContainer = expandedContainers[sGroup.groupContainer];
		group.groupContainer.group = group;
	    }
	    else
	    {
		group.containers = [];
		group.groups = [];
		
		for (var cI in sGroup.containers)
		{
		    var co = sGroup.containers[cI];
		    var c = expandedContainers[co.container];
		    
		    group.containers.push({"container" : c, "overrides" : co.overrides});
		    c.group = this.group;
		}

		for (var gI in sGroup.groups)
		{
		    var go = sGroup.groups[gI]
		    var g = deserialise.call(this, go.group);
		    
		    group.groups.push({"group" : g, "overrides" : go.overrides});
		    g.group = this.group;
		}
	    }
	    
	    return group;
	}

	var group = deserialise.call(this, this.options.groupConfig.group, this.group);
/*
	for (var cI in expandedContainers)
	{
	    var c = expandedContainers[cI]
	    c.group = this.innerGroup;
	}*/

	var getTerminalByName = function (terminals, name)
	    {
		for (var tI in terminals)
		{
		    var t = terminals[tI];
		    
		    if (t.options.name == name)
			return t;
		}
	    };
	var self = this;
	var reconnectTerminal = function(terminal, internalId, internalName)
	    {
		for (var wI in terminal.wires)
		{
		    var w = terminal.wires[wI];
		    
		    var wire = {}
			    
		    var thisC = {"moduleId" : mapModuleId(offset, internalId), "terminal" : internalName}
		    
		    if (w.terminal1 == terminal)
		    {
			wire.src = thisC
			wire.tgt = {"moduleId" : self.layer.containers.indexOf(w.terminal2.container), "terminal" : w.terminal2.options.name}
		    }
		    else
		    {
			wire.tgt = thisC
			wire.src = {"moduleId" : self.layer.containers.indexOf(w.terminal1.container), "terminal" : w.terminal1.options.name}		    
		    }
		    
		    self.layer.addWire(wire);
		}
	    };
	
	var reconnect = function (tfMap, getInternalConfig, offset)
	{
	    for (var fName in tfMap.fields)
	    {
		var fMap = tfMap.fields[fName];
		var f = self.form.inputsNames[fName];
		var internal = getInternalConfig(fMap.containerId, fMap.name);
		
		internal.setValue(f.getValue());
		
		if (lang.isObject(f.terminal))
		    reconnectTerminal(f.terminal, mapModuleId(offset, fMap.containerId), fMap.name);
	    }
	    
	    for (var tName in tfMap.terminals)
	    {
		var tMap = tfMap.terminals[tName];
		var t = getTerminalByName(self.terminals, tName);
		
		reconnectTerminal(t, mapModuleId(offset, tMap.containerId), tMap.name);
	    }
	}
	
	reconnect(this.options.groupConfig.map.containerMap, function(id, name) { return group.containers[id].container.form.inputsNames[name]; }, 0);
	reconnect(this.options.groupConfig.map.groupMap, function(id, name) { return group.groups[id].group.groupContainer.form.inputsNames[name] }, group.containers.length);
	//Deserialise groups
	
	//Set Field values
	/*
	for (var fName in this.form.inputsNames)
	{
	    var f = this.form.inputsNames[fName];
	    var internal = WireIt.GroupUtils.getInternalField(this.options.groupConfig, fName);
	    
	    var container = expandedContainers[internal.moduleId];
	    
	    container.form.inputsNames[internal.name].setValue(f.getValue());
	}
	*/
	for (var wI in this.options.groupConfig.wires)
	{
	    var w = this.options.groupConfig.wires[wI]

	    this.layer.addWire(
		{
			"src":{
				"moduleId": mapModuleId(offset, w.src.moduleId),
				"terminal": w.src.terminal
			},
			"tgt":{
				"moduleId": mapModuleId(offset, w.tgt.moduleId),
				"terminal": w.tgt.terminal
			}
		}
	    );
	}
	
	
	//Remap current external wires to their corresponding internal containers
	/*
	for (var tI in this.terminals)
	{
	    var t = this.terminals[tI]
	    
	    for (var wI in t.wires)
	    {
			var w = t.wires[wI]
			
			var internal = WireIt.GroupUtils.getInternalTerminal(this.options.groupConfig, t.options.name);
			
			var wire = {}
			
			var thisC = {"moduleId" : mapModuleId(offset, internal.moduleId), "terminal" : internal.name}
			
			if (w.terminal1 == t)
			{
			    wire.src = thisC
			    wire.tgt = {"moduleId" : this.layer.containers.indexOf(w.terminal2.container), "terminal" : w.terminal2.options.name}
			}
			else
			{
			    wire.tgt = thisC
			    wire.src = {"moduleId" : this.layer.containers.indexOf(w.terminal1.container), "terminal" : w.terminal1.options.name}		    
			}
			
			this.layer.addWire(wire);
	    }
	}

	*/
	this.layer.removeContainer(this);

	this.group.groupContainer = null;

	var POPIgI = 0;
	for (POPIgI = 0; POPIgI < group.groups.length; POPIgI++)
	{
	    var g = group.groups[POPIgI].group;
	    
	    if (g.properties.expanded && lang.isValue(g.groupContainer))
		g.groupContainer.expand();
	}
	
	this.group.grouper.showGroup.call(this.group.grouper, this.group);
    },

    translatePosition: function(modulePosition, position)
    {
	return [ Math.max(0, modulePosition[0]+position[0]), Math.max(0, modulePosition[1]+position[1]) ];
    },

    getConfig : function()
    {
	var config = WireIt.GroupFormContainer.superclass.getConfig.call(this);
	lang.augmentObject(config, {"fields" : this.options.fields, "terminals" : this.options.terminals, "groupConfig" : this.options.groupConfig});
	
	return config;
    }

   /**
    * @method getValue
    */
/*   getValue: function() {
      return this.group;
   },
  */ 
   /**
    * @method setValue
    */
   /*setValue: function(val) {
      this.group = val;
    
      //Terminals
      this.removeAllTerminals();
      this.initTerminals(val.terminals);
      this.dd.setTerminals(this.terminals);
      
    //Fields - have to go after terminal stuff since fields create their own terminals and above stuff would destroy them
      this.options.fields = val.fields;
      this.form.destroy();
      this.renderForm();      
   }*/
   
});
})();