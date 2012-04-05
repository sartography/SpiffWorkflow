(function() {

/**
 * @class list of PairField where where the returned value is converted to an object
 * @extends inputEx.ListField
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.ObjectField = function(options) {
	options.elementType = {
		type: 'combine', 
		fields: [
		   {type: 'string', size: 10 },
		   {type:'string', size: 10 }
		]
	};
	inputEx.ObjectField.superclass.constructor.call(this, options);
};

YAHOO.extend(inputEx.ObjectField, inputEx.ListField, {

   /**
    * Convert the array of 2d elements to an javascript object 
    */
   getValue: function() {
   	var v = inputEx.ObjectField.superclass.getValue.call(this);
   	var obj = {};
   	for(var i = 0 ; i < v.length ; i++) {
   		obj[ v[i][0] ] = v[i][1];
   	}
   	return obj;
   },

   /**
    * Convert the object into a list of pairs
    */
   setValue: function(v) {
   	var val = [];
   	for(var key in v) {
   		if( v.hasOwnProperty(key) ) {
   			val.push([key, v[key]]);
   		}
   	}
   	inputEx.ObjectField.superclass.setValue.call(this,val);
   }
});

/**
 * Register this class as "object" type
 */
inputEx.registerType('object', inputEx.ObjectField);

})();