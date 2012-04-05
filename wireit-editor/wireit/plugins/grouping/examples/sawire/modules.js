var modules= [];

modules[modules.length++] = {
    "name":"xpath",
    "container": {
        "xtype": "WireIt.FormContainer",
        "title": "Apply xPath to input",
        "fields": [
        		{ "type": "string", "label": "Expression", "name": "expr", "wirable": true }
        ],
        "terminals": [
        {
            "name": "out",
            "direction": [0, 1],
            "offsetPosition": {
                "left": 86,
                "bottom": -15
            },
            "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
            }
        },
         {"name": "in", "direction": [0,-1], "offsetPosition": {"left": 82, "top": -15 }, "ddConfig": {
              "type": "input",
              "allowedTypes": ["output"]
           },
           "nMaxWires": 1
          }        
        ]
    }
};

modules[modules.length++] ={
    "name": "Group",
    "container" : {"xtype":"WireIt.GroupFormContainer"}
};

modules[modules.length++] = {
   "name": "jsBox",
   "container": {"xtype": "jsBox.Container"}
};

modules[modules.length++]={
    "name":"GetCaseById",
    "container":{
        "xtype": "samodules.GetByIdContainer",
        "title":"Get Case by Id"
    }
};

modules[modules.length++]={
    "name":"GetCustomerById",
    "container":{
        "xtype": "samodules.GetByIdContainer",
        "title":"Get Customer by Id"
    }
};

modules[modules.length++]={
    "name":"GetWorkItemById",
    "container":{
        "xtype": "samodules.GetByIdContainer",
        "title":"Get WorkItem by Id"
    }
};

modules[modules.length++] ={
    "name": "ApplyXSLToWorkItem",
    "container": {
        "xtype": "WireIt.FormContainer",
        "title": "Apply XSL To WorkItem",
        "fields": [
        {
            "type": "text",
                "label": "WorkItem XML",
                "name": "workitemXML",
                "wirable": true
        },
        {
            "type": "text",
                "label": "XSL",
                "value":'<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">\n'+
                '<xsl:template match="node()">\n'+
                '   <xsl:copy>\n'+
                '       <xsl:for-each select="@*">\n'+
                '           <xsl:copy/>\n'+
                '       </xsl:for-each>\n'+
                '        <xsl:apply-templates select="node()"/>\n'+
                '   </xsl:copy>\n'+
                '</xsl:template>\n'+
                '</xsl:stylesheet>',
                "name": "xsl",
                "wirable": false
        }
        ],
        "terminals": [
        {
            "name": "out",
            "direction": [0, 1],
            "offsetPosition": {
                "left": 140,
                "bottom": -15
            },
            "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
            }
        }
        ]
    }
};

modules[modules.length++] ={
    "name": "ExecuteRuleBase",
    "container": {
        "xtype": "WireIt.FormContainer",
        "title": "Execute a RuleBase",
        "fields": [
        {
            "type": "text",
                "label": "WorkItem XML",
                "name": "workitemXML",
                "wirable": true
        },
        {
            "type": "select",
                "label": "RuleBase",
                "name": "rulebase",
				"selectValues": [1,2,3,4],
				"selectOptions": ["StripEntitiesRuleBase","SetTransitionConditionA","MyFirstRuleBase","MySecondRuleBase"],
				"required":true,
                "wirable": false
        }
        ],
		"executionType":"jsBox",
        "terminals": [
        {
            "name": "out",
            "direction": [0, 1],
            "offsetPosition": {
                "left": 140,
                "bottom": -15
            },
            "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
            }
        }
        ]
    }
};


modules[modules.length++] ={
    "name": "SaveWorkItem",
    "container": {
        "xtype": "WireIt.FormContainer",
        "title": "Save WorkItem",
        "fields": [
        {
            "type": "text",
                "label": "WorkItem XML",
                "name": "workitemXML",
                "wirable": true
        }
        ],
		"executionType":"jsBox",
        "terminals": [
        {
            "name": "out",
            "direction": [0, 1],
            "offsetPosition": {
                "left": 140,
                "bottom": -15
            },
            "ddConfig": {
                "type": "output",
                "allowedTypes": ["input"]
            }
        }
        ]
    }
};

modules[modules.length++] ={
    "name": "DisplayCase",
    "container": {
        "xtype": "samodules.DisplayItemContainer",
        "title": "Display Case"
    }
};

modules[modules.length++] ={
    "name": "DisplayCustomer",
    "container": {
        "xtype": "samodules.DisplayItemContainer",
        "title": "Display Customer"
    }
};

modules[modules.length++] ={
    "name": "DisplayWorkItem",
    "container": {
        "xtype": "samodules.DisplayItemContainer",
        "title": "Display WorkItem"
    }
};

var samodules={};

samodules.GetByIdContainer = function(options, layer) {
    options.fields = [{
         "type": "integer",
             "label": "Id",
             "name": "input",
             "wirable": true
         }];
   samodules.GetByIdContainer.superclass.constructor.call(this, options, layer);
   
   this.outputTerminal = this.addTerminal({xtype: "WireIt.util.TerminalOutput", "name": "out"});      
   var width = WireIt.getIntStyle(this.el, "width");   
   WireIt.sn(this.outputTerminal.el, null, {position: "absolute", bottom: "-15px", left: (Math.floor(width/2)-15)+"px"});
};

YAHOO.extend(samodules.GetByIdContainer, WireIt.FormContainer, {});

samodules.DisplayItemContainer= function(options, layer) {
    options.fields= [{
        "type": "text",
            "label": "Raw XML",
            "name": "xml",
            "wirable": true
        }];
    samodules.DisplayItemContainer.superclass.constructor.call(this, options, layer);

    var width = WireIt.getIntStyle(this.el, "width");   
    this.outputTerminal = this.addTerminal({xtype: "WireIt.util.TerminalOutput", "name": "out"});      
    WireIt.sn(this.outputTerminal.el, null, {position: "absolute", bottom: "-15px", left: (Math.floor(width/2)-15)+"px"});
    
};
YAHOO.extend(samodules.DisplayItemContainer, WireIt.FormContainer, {});


var jsBox = {};

/**
 * Container class used by the "jsBox" module (automatically sets terminals depending on the number of arguments)
 * @class Container
 * @namespace jsBox
 * @constructor
 */
jsBox.Container = function(options, layer) {
         
   jsBox.Container.superclass.constructor.call(this, options, layer);
   
   this.buildTextArea(options.codeText || "function(e,c,d) {\n\n  return 0;\n}");
   
   this.createTerminals();
   
   // Reposition the terminals when the jsBox is being resized
   this.ddResize.eventResize.subscribe(function(e, args) {
      this.positionTerminals();
      YAHOO.util.Dom.setStyle(this.textarea, "height", (args[0][1]-70)+"px");
   }, this, true);
};

YAHOO.extend(jsBox.Container, WireIt.Container, {
   
   /**
    * Create the textarea for the javascript code
    * @method buildTextArea
    * @param {String} codeText
    */
   buildTextArea: function(codeText) {

      this.textarea = WireIt.cn('textarea', null, {width: "90%", height: "70px", border: "0", padding: "5px"}, codeText);
      this.setBody(this.textarea);

      YAHOO.util.Event.addListener(this.textarea, 'change', this.createTerminals, this, true);
      
   },
   
   /**
    * Create (and re-create) the terminals with this.nParams input terminals
    * @method createTerminals
    */
   createTerminals: function() {
      
      // Output Terminal
      if(!this.outputTerminal) {
   	   this.outputTerminal = this.addTerminal({xtype: "WireIt.util.TerminalOutput", "name": "out"});      
         this.outputTerminal.jsBox = this;
      }
      
      // Input terminals :
      var match = (this.textarea.value).match((/^[ ]*function[ ]*\((.*)\)[ ]*\{/));
   	var sParamList = match ? match[1] : "";
      var params = sParamList.split(',');
      var nParams = (sParamList=="") ? 0 : params.length;
      
      var curTerminalN = this.nParams || 0;
      if(curTerminalN < nParams) {
         // add terminals
         for(var i = curTerminalN ; i < nParams ; i++) {
            var term = this.addTerminal({xtype: "WireIt.util.TerminalInput", "name": "param"+i});
            //term.jsBox = this;
            WireIt.sn(term.el, null, {position: "absolute", top: "-15px"});
         }
      }
      else if (curTerminalN > nParams) {
         // remove terminals
         for(var i = this.terminals.length-(curTerminalN-nParams) ; i < this.terminals.length ; i++) {
         	this.terminals[i].remove();
         	this.terminals[i] = null;
         }
         this.terminals = WireIt.compact(this.terminals);
      }
      this.nParams = nParams;
   
      this.positionTerminals();

      // Declare the new terminals to the drag'n drop handler (so the wires are moved around with the container)
      this.dd.setTerminals(this.terminals);
   },
   
   /**
    * Reposition the terminals
    * @method positionTerminals
    */
   positionTerminals: function() {
      var width = WireIt.getIntStyle(this.el, "width");

      var inputsIntervall = Math.floor(width/(this.nParams+1));

      for(var i = 1 ; i < this.terminals.length ; i++) {
         var term = this.terminals[i];
         YAHOO.util.Dom.setStyle(term.el, "left", (inputsIntervall*(i))-15+"px" );
         for(var j = 0 ; j < term.wires.length ; j++) {
            term.wires[j].redraw();
         }
      }
      
      // Output terminal
      WireIt.sn(this.outputTerminal.el, null, {position: "absolute", bottom: "-15px", left: (Math.floor(width/2)-15)+"px"});
      for(var j = 0 ; j < this.outputTerminal.wires.length ; j++) {
         this.outputTerminal.wires[j].redraw();
      }
   },
   
   /**
    * Extend the getConfig to add the "codeText" property
    * @method getConfig
    */
   getConfig: function() {
      var obj = jsBox.Container.superclass.getConfig.call(this);
      obj.codeText = this.textarea.value;
      return obj;
   }
   
});

/**
 * ComposedContainer is a class for Container representing Pipes.
 * It automatically generates the inputEx Form from the input Params.
 * @class ComposedContainer
 * @extends WireIt.FormContainer
 * @constructor
 */
jsBox.ComposedContainer = function(options, layer) {
   
   if(!options.fields) {
      
      options.fields = [];
      options.terminals = [];
      var pipe = sawire.editor.getPipeByName(options.title);
      for(var i = 0 ; i < pipe.modules.length ; i++) {
         var m = pipe.modules[i];
         var moduleDefinition =sawire.editor.modulesByName[m.name];
         //console.log(moduleDefinition);
         
         if( m.name == "input") {
            m.value.input.wirable = true;
            options.fields.push(m.value.input);
         }
         else if(m.name == "output") {
            options.terminals.push({
               name: m.value.name,
               "direction": [0,1], 
               "offsetPosition": {"left": options.terminals.length*40, "bottom": -15}, 
               "ddConfig": {
                   "type": "output",
                   "allowedTypes": ["input"]
                }
            });
         }
      }
   }
   
   jsBox.ComposedContainer.superclass.constructor.call(this, options, layer);
};
YAHOO.extend(jsBox.ComposedContainer, WireIt.FormContainer);