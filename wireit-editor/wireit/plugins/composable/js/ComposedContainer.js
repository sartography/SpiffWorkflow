/**
 * ComposedContainer is a class for Container representing Pipes.
 * It automatically generates the inputEx Form from the input Params.
 *
 * @class ComposedContainer
 * @extends WireIt.FormContainer
 * @constructor
 */
WireIt.ComposedContainer = function(options, layer) {
   
   if(!options.fields) {
      
      options.fields = [];
      options.terminals = [];

		var pipe = options.wiring.working;
      
		for(var i = 0 ; i < pipe.modules.length ; i++) {
         var m = pipe.modules[i];
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
   
   WireIt.ComposedContainer.superclass.constructor.call(this, options, layer);
};
YAHOO.extend(WireIt.ComposedContainer, WireIt.FormContainer);
