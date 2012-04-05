(function() {
    var util = YAHOO.util,lang = YAHOO.lang;
    var Event = util.Event, Dom = util.Dom, Connect = util.Connect,JSON = lang.JSON,widget = YAHOO.widget;

/**
 * Handles a Group
 * @class WireIt.Group
 */    
WireIt.Group = function(grouper, layer, serialisedGroup) {
	
	this.containers  = [];
	this.groups = [];
	this.properties = {};
	
	this.layer = layer;
	this.grouper = grouper;
	
	this.events = {};
	
	this.events.containerAdded = new YAHOO.util.CustomEvent("containerAdded");    
	this.events.containerRemoved = new YAHOO.util.CustomEvent("containerRemoved");    
	this.events.groupAdded = new YAHOO.util.CustomEvent("groupAdded");
	this.events.groupRemoved = new YAHOO.util.CustomEvent("groupRemoved");
	this.events.groupEmptied = new YAHOO.util.CustomEvent("groupEmptied");
	
	this.events.stateChanged = new YAHOO.util.CustomEvent("stateChanged");
	this.stateChangeFunc = function (eventName, objects)  { 
		this.events.stateChanged.fire({"event" : eventName, "objects" : objects});
   };
	    
	this.events.containerAdded.subscribe(this.stateChangeFunc, this, true);
	this.events.containerRemoved.subscribe(this.stateChangeFunc, this, true);
	this.events.groupAdded.subscribe(this.stateChangeFunc, this, true);
	this.events.groupRemoved.subscribe(this.stateChangeFunc, this, true);
	
	this.events.containerRemoved.subscribe(this.checkGroupEmpty, this, true);
	this.events.groupRemoved.subscribe(this.checkGroupEmpty, this, true);
	
	this.collapsing = false;
	
	//If a container is removed from the layer then remove it from the currently selected groups
	layer.eventRemoveContainer.subscribe(function(eventName, containers) 
	    {
		if (!this.collapsing)
		    this.removeContainer.call(this, containers[0]);
	    }, this, true);
    };
    


WireIt.Group.prototype = {
	
	collapse: function(expanded)
	{
	    if (lang.isValue(this.groupContainer))
		return this.groupContainer; //This group is already collapsed
	    
	    for (var gI in this.groups)
	    {
		var go = this.groups[gI];
		go.group.collapse.call(go.group, true);
	    }
	    
	    var map = WireIt.GroupUtils.getMap(this);
	    var collapsedConfig = WireIt.GroupUtils.getCollapsedConfig(this, map);
	    var containers = [];
	    WireIt.GroupUtils.addAllContainers(this, containers);
	    var sGroup = WireIt.GroupUtils.serialiseGroup(this, containers);
	    
	    var modules = WireIt.GroupUtils.getInternalModuleConfig(containers, collapsedConfig.center);
	    var getInternalContainerId = function(container) {
		    return containers.indexOf(container);
		};
	    
	    var getExternalTerminalName = function(type, index, name) {
		    var submap;
		    
		    if (type == "container")
			submap = map.containerMap;
		    else
			submap = map.groupMap;

		    
		    var terminal = submap[index].terminals[name];
		    
		    if (lang.isObject(terminal)) {
				return terminal.externalName;
			}
		    else {
				var field = submap[index].fields[name];
			
				if (lang.isObject(field) && field.fieldConfig.wirable)
			    	return field.externalName;
		    	}
		    
			};
	    
	    var wires = WireIt.GroupUtils.getWireConfig(this, getInternalContainerId, getExternalTerminalName);

	    var gc = this.layer.addContainer(
				    {
						"xtype": "WireIt.GroupFormContainer",
						"title": "Group",    

						"collapsible": false,
						"fields": collapsedConfig.fields,
						"terminals" : collapsedConfig.terminals,
						"legend": null,
						"getBaseConfigFunction" : this.grouper.baseConfigFunction,
						groupConfig : {"group" : sGroup, "center": collapsedConfig.center, "modules" : modules, "wires" : wires.internal, "map" : WireIt.GroupUtils.getExternalToInternalMap(map)},
						position : collapsedConfig.position
				    }
			    )
	    
	    this.addExternalWires(gc, wires.external);
	    //TODO: place in tempory vars since removing from layer could remove from group in future

	    this.collapsing = true;

	    var index;
	    for (index in this.containers)
		this.layer.removeContainer(this.containers[index].container);
		
	    for (index in this.groups)
		WireIt.GroupUtils.removeGroupFromLayer(this.groups[index].group, this.layer);

	    this.collapsing = false;

	    gc.group = this
	    this.containers = [];
	    this.groups = [];
	    this.groupContainer = gc;
	    this.properties.expanded = lang.isValue(expanded) ? expanded : false;
	    
	    return gc;
	},

	checkGroupEmpty: function() {
	   //Check the group is empty
	   if (!lang.isValue(this.groupContainer) && this.containers.length == 0 && this.groups.length == 0) {
			this.events.groupEmptied.fire(this);
	   }
	},

	expand: function()
	{
	    if (lang.isValue(this.groupContainer))
	    {
		this.groupContainer.expand();
	    }
	},
	
	addContainer: function(container, overrides)
	{
	    if (!lang.isObject(overrides))
		    overrides = {"fields" : {}, "terminals" : {}};
		    
	    var co = {"container" : container, "overrides" : overrides}
	    
	    this.containers.push(co);
	    container.group = this;
	    
	    container.eventAddWire.subscribe(this.stateChangeFunc, this, true);
	    container.eventRemoveWire.subscribe(this.stateChangeFunc, this, true);
	    
	    this.events.containerAdded.fire(co);
	},
	
	addGroup: function(group, overrides)
	{
	    if (!lang.isObject(overrides))
		    overrides = {"fields" : {}, "terminals" : {}};
	    
	    var go = {"group" : group, "overrides" : overrides}
	    this.groups.push(go);
	    group.group = this;
	    
	    //Listen to the inner group's state change (so we can fire our one)
	    group.events.stateChanged.subscribe(this.stateChangeFunc, this, true);
	    group.events.groupEmptied.subscribe(function() { this.removeGroup(group); }, this, true);
	    this.events.containerAdded.fire(go);
	},
	
	removeContainer: function(container, index)
	{
	    if (!lang.isValue(index))
		index = WireIt.GroupUtils.firstTestSucess(this.containers, function (co) { return co.container == container; });
	
	    if (index != -1)
	    {
		this.containers.splice(index, 1);
		
		container.group = null;
		this.events.containerRemoved.fire(container);
	    }
	},
	
	removeGroup: function(group, index)
	{
	    if (!lang.isValue(index))
		index = WireIt.GroupUtils.firstTestSucess(this.groups, function (go) { return go.group == group });
	
	    if (index != -1)
	    {
		group.group = null;
		this.events.groupRemoved.fire(this.groups.splice(index, 1));
	    }
	},
	
	unGroup: function()
	{
	    if (lang.isValue(this.groupContainer))
	    {
		this.expand();
	    }
	    
	    var temp = {};
	    temp.containers = [];
	    lang.augmentObject(temp.containers, this.containers);
	    temp.groups = [];
	    lang.augmentObject(temp.groups, this.groups);
	    
	    
	    {
		for (var cI in temp.containers)
		{
		    var co = temp.containers[cI];

		    this.removeContainer(co.container);

		    if (lang.isValue(this.group))
			this.group.addContainer(co.container, co.overrides); //TODO: name conflicts?
		}
		
		for (var gI in temp.groups)
		{
		    var go = temp.groups[gI];
		    
		    this.removeGroup(go.group);
		    
		    if (lang.isValue(this.group))
			this.group.addGroup(go.group, go.overrides);
		}
	    }
	    
	    if (lang.isValue(this.group))
	    {
		this.group.removeGroup(this);
		this.group = null;
	    }
	    else
		this.layer.removeGroup(this);
		
	    this.events.stateChanged.fire(this);
	},
	
	generateUI: function(map, changedCallback)
	{
	    if (!lang.isValue(map))
		map = WireIt.GroupUtils.getMap(this)
	    
	    listRows = [];
	    var configUITerminalMap = {};
	    var configUIFieldMap = {};
	    var layer = this.layer;
	    var self = this;
	    
	    var addRemapInput = function(name, moduleId, showOn, showCancel, defaultVisible, defaultName, visibleReadOnly, showSide, defaultSide)
		{
		    var addTds = function(row) {
			    tds = [];
			    
			    for(var i = 0; i < 4; i++)
			    {
				var td = WireIt.cn("td")
				tds.push(td);
				row.appendChild(td);
			    }
			    
			    return tds;
			}
		    
		    var row = WireIt.cn("tr")
		    row.onmouseover = showOn
		    row.onmouseout = showCancel
		    
		    var focusable = []
		    
		    var visible = WireIt.cn("input", {"type" : "checkbox"});
		    visible.checked = (typeof defaultVisible == "undefined") ? "" : defaultVisible;
		    visible.disabled = visibleReadOnly
		    focusable.push(visible);
		    
		    var externalName = WireIt.cn("input", {"type" : "text"});
		    externalName.value = (typeof defaultName == "undefined") ? "" : defaultName
		    focusable.push(externalName);
		    
		    var tds = addTds(row);
		    
		    tds[0].innerHTML = name;
		    tds[1].appendChild(visible);
		    tds[2].appendChild(externalName);
		    
		    if (showSide)
		    {
			var sideSelect = WireIt.cn("select");
			sideSelect.appendChild(WireIt.cn("option", {value: "top"}, {}, "Top"));
			sideSelect.appendChild(WireIt.cn("option", {value: "bottom"}, {}, "Bottom"));
			sideSelect.appendChild(WireIt.cn("option", {value: "left"}, {}, "Left"));
			sideSelect.appendChild(WireIt.cn("option", {value: "right"}, {}, "Right"));
			
			if (lang.isValue(defaultSide))
			    sideSelect.value = defaultSide;
			
			focusable.push(sideSelect)
			
			tds[3].appendChild(sideSelect);
		    }
		    else
		    {
			tds[3].align = "center";
			tds[3].innerHTML = "---";
		    }
		    /*
		    var showButton = WireIt.cn("button", {}, {}, "Show")
		    showButton.onmousedown = showOn
		    showButton.onmouseup = showCancel; 
		    showButton.onmouseout = showCancel;
		    
		    tds[5].appendChild(showButton);*/
		    listRows.push(row)

		    for (var i in focusable)
		    {
			var f = focusable[i];
			f.onfocus = showOn
			f.onblur = showCancel
			f.onchange = changedCallback;
		    }

		    return {"visible": visible, "externalName":  externalName, "side" : sideSelect};
		}
	
	
	    var addTerminal = function(internalName, tMap, override, moduleId, fieldTerminals, showOn, showOff)
		{
		    var visibleReadOnly = false;
		    var defaultVisible = false;
		    var nameReadOnly = false;
		    
		    var fieldTerminal = fieldTerminals[internalName];
		    if (!lang.isValue(fieldTerminal))
		    {
			var fragment = addRemapInput(internalName, moduleId, function() { showOn(moduleId) }, function() { showOff(moduleId) }, 
			    tMap.visible || override.visible,  lang.isValue(override.rename) ? override.rename : "", 
			    lang.isValue(tMap.forceVisible) ? tMap.forceVisible : false,
			    true, override.side);
		    
			//if (!lang.isValue(configUITerminalMap[moduleId]))
			// configUITerminalMap[moduleId] = {};
			    
			//configUITerminalMap[moduleId][internalName] = fragment;
			return fragment;
		    }
		}
	    
	    var addField = function(internalName, fMap, override, moduleId, fieldTerminals, showOn, showOff)
		{
		    var visibleReadOnly = false;
		    var defaultVisible = false;
		    if (fMap.fieldConfig.wirable)
		    {
			fieldTerminals[internalName] = true;
		    }
		    
		    
		    var fragment = addRemapInput(internalName, moduleId, function() { showOn(moduleId) }, function() { showOff(moduleId) }, 
			override.visible || fMap.visible, lang.isValue(override.rename) ? override.rename : "", 
			lang.isValue(fMap.forceVisible) ? fMap.forceVisible : false);
		    
		    //if (!lang.isValue(configUIFieldMap[moduleId]))
		    //	configUIFieldMap[moduleId] = {};
			    
		    //configUIFieldMap[moduleId][internalName] = fragment
		    return fragment
		}
	    
	    var containerUIMap = [];
	    var groupUIMap = [];
	    
	    var addControls = function (fieldsAndTerminals, overrides, results, showOnByIndex, showOffByIndex)
	    {
		for (var cI in fieldsAndTerminals)
		{
		    var c = fieldsAndTerminals[cI];
		    var fieldTerminals = {};
		    var index = cI;
		    
		    var fields = {}
		    var terminals = {}
		    
		    for (var fName in c.fields)
		    {
			var fMap = c.fields[fName];
			var fieldValue= overrides[cI].container.getValue();
			if( fieldValue[fName] == undefined || ( fieldValue[fName] != undefined && fieldValue[fName] != "[wired]") ) { // Skip wired fields, we won't want them exposed.
			    fields[fName] = addField(fName, fMap, WireIt.GroupUtils.valueOr(overrides[cI].overrides.fields[fName], {}), cI, fieldTerminals, showOnByIndex, showOffByIndex);
		    }
		    }
		    
		    for (var tName in c.terminals)
		    {
			var tMap = c.terminals[tName];
			
			var tFragment = addTerminal(tName, tMap, WireIt.GroupUtils.valueOr(overrides[cI].overrides.terminals[tName], {}), cI, fieldTerminals, showOnByIndex, showOffByIndex);
			
			if (lang.isValue(tFragment))
			    terminals[tName] = tFragment;
		    }
		    
		    results.push({"fields" : fields, "terminals" : terminals});
		}
	    };
	    
	    
	    addControls(map.containerMap, this.containers, containerUIMap, function(index) 
		{ 
		    self.layer.setSuperHighlighted([self.containers[index].container]) 
		}, function(index) 
		    { 
			self.layer.unsetSuperHighlighted(); 
		    }
		);
		
	    addControls(map.groupMap, this.groups, groupUIMap, function(index) 
		{ 
		    var containers = [];
		    WireIt.GroupUtils.applyToContainers(self.groups[index].group, true, function(c) { containers.push(c) });
		    self.layer.setSuperHighlighted(containers);
		    
		}, function(index) 
		    { 
			self.layer.unsetSuperHighlighted();
		    }
		);
	    
	    //this.configUITerminalMap = configUITerminalMap;
	    //this.configUIFieldMap = configUIFieldMap;
		
	    return { 
		    "listRows" : listRows,
		    "containerUIMap": containerUIMap,
		    "groupUIMap": groupUIMap
		};
	},
	
	getAndCheckOverrides: function(containerUIMap, groupUIMap)
	{
	    var tempGroup = {};
	    lang.augmentObject(tempGroup, this);
	    tempGroup.containers = [];
	    //lang.augmentObject(tempGroup.containers, this.containers);
	    tempGroup.groups = [];
	    //lang.augmentObject(tempGroup.groups, this.groups);
	    
	    var overrides = WireIt.GroupUtils.getOverridesFromUI(containerUIMap, groupUIMap);
	    
	    for (var cI in this.containers)
	    {
		var co = {};
		co.container = this.containers[cI].container;
		co.overrides = overrides.containerOverrides[cI];
		
		tempGroup.containers[cI] = co;
	    }
	    for (var gI in this.groups)
	    {
		var go = {};
		go.group = this.groups[gI].group;
		go.overrides = overrides.groupOverrides[gI];
		
		tempGroup.groups[gI] = go;
	    }
   
	    var map;
	    
	  try {
			map = WireIt.GroupUtils.getMap(tempGroup);
	  }
	  catch (err) {
			if (lang.isObject(err) && lang.isValue(err.type) && err.type == "MappingError") {
		    return {"overrides" : overrides, "valid" : false, "error" : err};
			}
			else
		    	throw err
	  }
	    
	  return {"overrides" : overrides, "valid" : true};
	},
	
	setGroupOptions: function(overrides)
	{
	    for (var cI in overrides.containerOverrides)
	    {
		var o =  overrides.containerOverrides[cI];
		
		this.containers[cI].overrides = o;
	    }
	    
	    for (var gI in overrides.groupOverrides)
	    {
		var o =  overrides.groupOverrides[cI];
		
		this.groups[gI].overrides = o;
	    }
	},
	
	addExternalWires: function(groupContainer, wireMap)
	{
		var layer = this.layer;
	
		for (var wI in wireMap)
		{
		    var w = wireMap[wI];
		    
		    var groupFragment = {};
		    groupFragment.moduleId = this.layer.containers.indexOf(groupContainer);
		    groupFragment.terminal = w.externalName;

		    var externalFragment = {};
		    externalFragment.moduleId = this.layer.containers.indexOf(w.externalTerminal.container);
		    externalFragment.terminal = w.externalTerminal.options.name;
		    
		    
		    var wireConfig = { }
		    
		    if (w.groupIsSource)
		    {
				wireConfig.src = groupFragment;
				wireConfig.tgt = externalFragment;
		    }
		    else
		    {
				wireConfig.src = externalFragment;
				wireConfig.tgt = groupFragment;
		    }
		    
		    this.layer.addWire(wireConfig);
		}
	}
    }
})();