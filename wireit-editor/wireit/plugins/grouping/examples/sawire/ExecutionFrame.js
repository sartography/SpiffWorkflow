/**
 * An "ExecutionFrame" is the equivalent to the jsBox layer.
 * It contains a set module instances and a set of wires linking them.
 * @class ExecutionFrame
 * @constructor
 * @param {Object} wiringConfig The wiring config
 */
var ExecutionFrame = function(wiringConfig, frameLevel, parentFrame, parentIndex) {
   
   // save the initial config
   this.wiringConfig = wiringConfig;
   
   // save the parent frame
   this.frameLevel = frameLevel || 0;
   this.parentFrame = parentFrame;
   this.parentIndex = parentIndex;
   
   // Will contains the execution values (this.execValues[module][outputName] = the value)
   this.execValues = {};
   
};

ExecutionFrame.setExecutionStateForContainer =  function(container, state){
    var bodyEl= container.bodyEl;
      if( bodyEl ) {
         if( state != "js-execution-starting") YAHOO.util.Dom.removeClass(bodyEl, "js-execution-starting");
         if( state != "js-execution-ok") YAHOO.util.Dom.removeClass(bodyEl, "js-execution-ok");
         if( state != "js-execution-failed") YAHOO.util.Dom.removeClass(bodyEl, "js-execution-failed");
         if( state ) YAHOO.util.Dom.addClass(bodyEl, state);
      }    
};

ExecutionFrame.clearExecutionStateForContainer =  function(container){
    ExecutionFrame.setExecutionStateForContainer(container);
};

ExecutionFrame.prototype = {
   
   /**
    * @method run
    * @param {Object} params The input parameters
    */
   run: function(params) {
      
      //console.log("running frame "+this.wiringConfig.name, " with params ", params);
      
      var modules = this.wiringConfig.working.modules,
          i;
      
      try {

         var moduleIdsToExecute = [];
         for( i = 0; i < modules.length; i++) {
            if( this.mayEval(i) ) {
               //console.log("mayEval:", modules[i]);
               moduleIdsToExecute.push(i);
            }
         }

         //console.log("moduleIdsToExecute", moduleIdsToExecute);


         for( i = 0 ; i < moduleIdsToExecute.length ; i++) {
            this.execute(moduleIdsToExecute[i],params);
         }

      }
      catch(ex) {
         console.log("Error while running: ", ex);
      }
      
      
   },
   
   
   mayEval: function(moduleId) {
      var t = this.wiringConfig.working.modules[moduleId].name;

      //console.log("mayEval", this.wiringConfig.working.modules[moduleId]);

      if( t == "callback") {
         return true;
      }
      else if(t == "comment") {
         return false;
      }
      else {// jsBox or ComposedModules or output

         // runnable if:
         //    all wires which target is this moduleId have a source output evaluated.
         var wires = this.wiringConfig.working.wires;
         for(var i = 0 ; i < wires.length ; i++) {
            var wire = wires[i];
            if(wire.tgt.moduleId == moduleId) {
               if(!this.execValues[wire.src.moduleId] || typeof this.execValues[wire.src.moduleId][wire.src.terminal] == "undefined") {
                  //console.log("mayEval not eval because of ", wire.src, this.execValues);
                  return false;
               }
            }
         }
         
         return true;
      }
      
   },
   
   
   executeModules: function(moduleId, srcTerminal) {
      
         //console.log("executeModules", moduleId, srcTerminal);
         var params = this.execValues[moduleId][srcTerminal];
      
      // Execute the modules linked to the callbackFunction
      var i, wires = this.wiringConfig.working.wires;
      for(i = 0 ; i < wires.length ; i++)  {
         var wire = wires[i];
         if(wire.src.moduleId == moduleId && wire.src.terminal == srcTerminal ) {
            if( this.mayEval(wire.tgt.moduleId) ) {
               this.execute(wire.tgt.moduleId, params);
            }
         }
      }
      
      
   },
   
   
   execute: function(moduleId,params) {

      var moduleBodyEl;
      try {
         
      
      var module = this.wiringConfig.working.modules[moduleId];
      var t = module.name;
      if( this.frameLevel == 0) {
          moduleBodyEl= sawire.editor.layer.containers[moduleId].bodyEl;
          if(moduleBodyEl) {
              YAHOO.util.Dom.addClass(moduleBodyEl, 'js-execution-starting'); 
          }
      }
      
      //console.log("execute", module);
      if( t == "GetWorkItemById" ) {
          var id= module.value.input;
          if( id == "[wired]" ) {
               var wires = this.wiringConfig.working.wires;
               var paramValue;
               for(var i = 0 ; i < wires.length ; i++) {
                  var wire = wires[i];
                  if(wire.tgt.moduleId == moduleId) {
                     id = this.execValues[wire.src.moduleId][wire.src.terminal];
                     break;
                  }
              }              
          }          
          value= "<smf:workitem version='54'><smf:id>"+id+"</smf:id><smf:caseId>"+id+"</smf:caseId></smf:workitem>";
          // store the value
          this.execValues[moduleId] = {
             out: value
          };

          this.executeModules(moduleId, "out");
      }
      else if( t == "GetCaseById" ) {
          var id= module.value.input;
          if( id == "[wired]" ) {
               var wires = this.wiringConfig.working.wires;
               var paramValue;
               for(var i = 0 ; i < wires.length ; i++) {
                  var wire = wires[i];
                  if(wire.tgt.moduleId == moduleId) {
                     id = this.execValues[wire.src.moduleId][wire.src.terminal];
                     break;
                  }
              }              
          }
          value= "<smf:case><smf:id>"+id+"</smf:id><smf:customerId>"+id+"</smf:customerId>/smf:case>";
          // store the value
          this.execValues[moduleId] = {
             out: value
          };

          this.executeModules(moduleId, "out");
      }
      else if( t == "GetCustomerById" ) {
          var id= module.value.input;
          if( id == "[wired]" ) {
               var wires = this.wiringConfig.working.wires;
               var paramValue;
               for(var i = 0 ; i < wires.length ; i++) {
                  var wire = wires[i];
                  if(wire.tgt.moduleId == moduleId) {
                     id = this.execValues[wire.src.moduleId][wire.src.terminal];
                     break;
                  }
              }              
          }          
          value= "<smf:customer><smf:id>"+id+"</smf:id></smf:customer>";
          // store the value
          this.execValues[moduleId] = {
             out: value
          };

          this.executeModules(moduleId, "out");
      }
      else if( t == "DisplayWorkItem" || t == "DisplayCase" || t =="DisplayCustomer") {
          //var params = [];
          var xml= module.value.xml;
          if( xml == "[wired]") {
              var wires = this.wiringConfig.working.wires;
              var paramValue;
              for(var i = 0 ; i < wires.length ; i++) {
                 var wire = wires[i];
                 if(wire.tgt.moduleId == moduleId) {
                    xml = this.execValues[wire.src.moduleId][wire.src.terminal];
                    break;
                 }
             }
          }
                    
          alert(t+":"+xml);
          
          // store the value
          this.execValues[moduleId] = {
             out: xml
          };
          
          this.executeModules(moduleId, "out");
      }
      else if( t == "ApplyXSLToWorkItem") {
          var workItemXml= module.value.workitemXML;
          if( workItemXml == "[wired]") {
              var wires = this.wiringConfig.working.wires;
              var paramValue;
              for(var i = 0 ; i < wires.length ; i++) {
                 var wire = wires[i];
                 if(wire.tgt.moduleId == moduleId) {
                    workItemXml = this.execValues[wire.src.moduleId][wire.src.terminal];
                    break;
                 }
             }
          }
          var dom= xmlParse(workItemXml);
          var xslDom= xmlParse(module.value.xsl);
          var xslResult= xsltProcess(dom.firstChild, xslDom.firstChild);
          
          // store the value
          this.execValues[moduleId] = {
             out: xslResult
          };
          
          this.executeModules(moduleId, "out");
      }
      else if(t == "ExecuteRuleBase" ) {
          var workItemXml= module.value.workitemXML;
          if( workItemXml == "[wired]") {
              var wires = this.wiringConfig.working.wires;
              var paramValue;
              for(var i = 0 ; i < wires.length ; i++) {
                 var wire = wires[i];
                 if(wire.tgt.moduleId == moduleId) {
                    workItemXml = this.execValues[wire.src.moduleId][wire.src.terminal];
                    break;
                 }
             }
          }
          //execute the rulebase call...
          
          // store the value
          this.execValues[moduleId] = {
             out: workItemXml
          };
          
          this.executeModules(moduleId, "out");
      }
      else if( t == "xpath" ) {
          var expression= module.value.expr;
          var xml;
          var doExpressionSearch= false;
          if( expression == "[wired]") {
              doExpressionSearch= true;
          }
          var wires = this.wiringConfig.working.wires;
          var paramValue;
          for(var i = 0 ; i < wires.length ; i++) {
             var wire = wires[i];
             if(wire.tgt.moduleId == moduleId) {
                 if(wire.tgt.terminal=="expr" && doExpressionSearch) {
                     expression = this.execValues[wire.src.moduleId][wire.src.terminal];
                 }
                 else if ( wire.tgt.terminal=="in") {
                     xml = this.execValues[wire.src.moduleId][wire.src.terminal];
                 }  
             } 
         }
          
         var dom= xmlParse(xml);
         var xpathExpr=  xpathParse(expression);
         var value= xpathExpr.evaluate(new ExprContext(dom)).stringValue();
          this.execValues[moduleId] = {
             out: value
          };

          this.executeModules(moduleId, "out");
      }      
      else if(t == "extJsBox") {
         
         //console.log("execute jsbox ", module.config.codeText);
         
         // build the params list
         var args = [];
         var wires = this.wiringConfig.working.wires;
         for(var i = 0 ; i < wires.length ; i++) {
            var wire = wires[i];
            if(wire.tgt.moduleId == moduleId) {
               var paramId = parseInt(wire.tgt.terminal.substr(5,wire.tgt.terminal.length-5)); 
               args[args.length++]=this.execValues[wire.src.moduleId][wire.src.terminal]; 
            }
         }

         
         // "execution"
         var code = "var tempJsBoxFunction = (function(arg0,arg1){"+module.config.codeText+"})";
         eval(code);
         var evalResult = tempJsBoxFunction.apply(window, args);

         // store the value
         this.execValues[moduleId] = {
            out: evalResult
         };

         
         this.executeModules(moduleId, "out");
         
      }      
      else if(t == "input") {
         
         var inputName = module.value.input.name;
         
         // "execution"
         var value = (!!params && typeof params[inputName] != "undefined") ? params[inputName] : module.value.input.value;

         // store the value
         this.execValues[moduleId] = {
            out: value
         };

         this.executeModules(moduleId, "out");
         
      }
      else if(t == "callback") {
         
         // "execution"
         var that = this;
         // TODO: do the slice thing for parameters
         var value = function(a,b,c,d,e,f,g,h) {
            //console.log("running callback function", a, that, moduleId);
            // store the value
            that.execValues[moduleId] = {
               output: [a,b,c,d,e,f,g,h]
            };
            
            that.executeModules(moduleId, "output");
         };

         // store the value
         this.execValues[moduleId] = {
            callbackFunction: value
         };
         
         
         this.executeModules(moduleId, "callbackFunction");
         
      }
      else if(t == "jsBox") {
         
         //console.log("execute jsbox ", module.config.codeText);
         
         // build the params list
         var params = [];
         var wires = this.wiringConfig.working.wires;
         for(var i = 0 ; i < wires.length ; i++) {
            var wire = wires[i];
            if(wire.tgt.moduleId == moduleId) {
               var paramId = parseInt(wire.tgt.terminal.substr(5,wire.tgt.terminal.length-5)); 
               var paramValue = this.execValues[wire.src.moduleId][wire.src.terminal];
               params[paramId] = paramValue;
            }
         }

         // "execution"
         var code = "var tempJsBoxFunction = ("+module.config.codeText+")";
         eval(code);
         var evalResult = tempJsBoxFunction.apply(window, params);

         // store the value
         this.execValues[moduleId] = {
            out: evalResult
         };

         
         this.executeModules(moduleId, "out");
         
      }
      else if(t == "output") {
         if(!this.parentFrame) return;
         
         var outputName = module.value.name;
         
         if(typeof params == "undefined") {
            throw new Error("Undefined output '"+outputName+"' at frame "+this.wiringConfig.name+" (lvl: "+this.frameLevel+")");
         }         
         
         // store the value in the parentFrame !
         if(!this.parentFrame.execValues[this.parentIndex]) {
            this.parentFrame.execValues[this.parentIndex] = {};
         }
         this.parentFrame.execValues[this.parentIndex][outputName] = params;
         //console.log("setting output value : ", outputName, " to ", params);
         
         this.parentFrame.executeModules(this.parentIndex, outputName);
      }
      else if(t =="Group") {
          var wiringConfig = {
             name: t,
             working: module.config.groupConfig
          };
          var f = new ExecutionFrame(wiringConfig, this.frameLevel+1, this, moduleId);
          // build the params list
          var params = {};
          // Copy the default parameters value
          for(var key in module.value) {
             if(module.value.hasOwnProperty(key)) {
                var paramValue= module.value[key];
                params[key] = paramValue;
                if( paramValue == "[wired]") {
                      var wires = this.wiringConfig.working.wires;
                      for(var i = 0 ; i < wires.length ; i++) {
                         var wire = wires[i];
                         if(wire.tgt.moduleId == moduleId) {
                            paramValue = this.execValues[wire.src.moduleId][wire.src.terminal];
                            break;
                         }
                     }
                  }
                var mappedField= module.config.groupConfig.map.containerMap.fields[key];
                if( mappedField ) {
                    module.config.groupConfig.modules[mappedField.containerId].value[mappedField.name]= paramValue;
                }
             }
          }
          // Overwrite with the wires values
          var wires = this.wiringConfig.working.wires;
          for(var i = 0 ; i < wires.length ; i++) {
             var wire = wires[i];
             if(wire.tgt.moduleId == moduleId) {
                var paramName = wire.tgt.terminal;
                var paramValue = this.execValues[wire.src.moduleId][wire.src.terminal];
                params[paramName] = paramValue;
             }
          }
          
          module.config.groupConfig.map
          
          f.run(params);   
          
            
          // store the value
          var result= {};
          for(var termId in module.config.terminals){
              var term= module.config.terminals[termId];
              if( term.ddConfig.type == "output") {
                  var terminalReference= module.config.groupConfig.map.containerMap.terminals[term.name];
                  result[term.name]=f.execValues[terminalReference.containerId][terminalReference.name];
              }
          }
          

          
          this.execValues[moduleId] = result;
          
          this.executeModules(moduleId, "out");               
      }
      else {
         // HERE, WE HAVE A COMPOSED MODULE
         
         alert(t);
         var wiringText = sawire.editor.pipesByName[t].working;
         var wiringConfig = {
            name: t,
            working: YAHOO.lang.JSON.parse(wiringText)
         };
         var f = new ExecutionFrame(wiringConfig, this.frameLevel+1, this, moduleId);
         // build the params list
         var params = {};
         // Copy the default parameters value
         for(var key in module.value) {
            if(module.value.hasOwnProperty(key)) {
               params[key] = module.value[key];
            }
         }
         // Overwrite with the wires values
         var wires = this.wiringConfig.working.wires;
         for(var i = 0 ; i < wires.length ; i++) {
            var wire = wires[i];
            if(wire.tgt.moduleId == moduleId) {
               var paramName = wire.tgt.terminal;
               var paramValue = this.execValues[wire.src.moduleId][wire.src.terminal];
               params[paramName] = paramValue;
            }
         }
         f.run(params);
      }
      if(this.frameLevel ==0 &&  moduleBodyEl) {
          YAHOO.util.Dom.addClass(moduleBodyEl, 'js-execution-ok'); 
      }      
      
      }
      catch(ex){
         console.log("error while executing module", module, ex);
         if(moduleBodyEl) {
             YAHOO.util.Dom.addClass(moduleBodyEl, 'js-execution-failed'); 
         }
      }
      
   }
   
};