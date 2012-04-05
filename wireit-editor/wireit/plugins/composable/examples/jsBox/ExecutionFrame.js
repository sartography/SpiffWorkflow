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

      if(t == "input" || t == "callback") {
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
      
      try {
         
      
      var module = this.wiringConfig.working.modules[moduleId];
      var t = module.name;
      
      //console.log("execute", module);

      if(t == "input") {
         
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
      else {
         // HERE, WE HAVE A COMPOSED MODULE
         var wiringText = jsBox.editor.pipesByName[t].working;
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
      
      }
      catch(ex){
         console.log("error while executing module", module, ex);
      }
      
   }
   
};
