/**
 * Tweaking the TimeField to make a Time Range (two TimeFields)
 *    - doesn't show seconds
 *    - Minutes by group of 5
 */
inputEx.TimeRange = function(options) {
   
   var h1 = [], h2 = [], i, m = [], s;
   for(i = 0 ; i < 25 ; i++) { 
		s="";
		if ( i<10 ){ s="0"; } 
		s+= i;
		h2.push({ value: s });
   	if ( i<24 ){ h1.push({ value: s }); } // First block of hours musn't contain 24
	}
	m = [{ value: "00" },{ value: "05" },{ value: "10" },{ value: "15" },{ value: "20" },{ value: "25" },{ value: "30" },{ value: "35" },{ value: "40" },{ value: "45" },{ value: "50" },{ value: "55" }];
	
   options.fields = [
      {type: 'select', choices: h1 },
      {type: 'select', choices: m },
      {type: 'select', choices: h2 },
      {type: 'select', choices: m }
   ];

   options.separators = options.separators || [false,"H","&nbsp; à &nbsp;","H",false];
   inputEx.TimeRange.superclass.constructor.call(this,options);

	// Hook toogleEndMinutes to the updatedEvt of the 3d select
	// Like that when the user selects/unselects 24h the minutes will toogle accordingly
	var that = this;
	this.inputs[2].updatedEvt.subscribe(function(){
		that.toogleEndMinutes();
	});
	
};

YAHOO.lang.extend(inputEx.TimeRange, inputEx.CombineField, {   
   /**
    * Returns an array like ["HH:MM","HH:MM"]
    */
   getValue: function() {
      var values = inputEx.TimeRange.superclass.getValue.call(this);

		var returnedValue = [];
		returnedValue.push(values[0]+":"+values[1]);
		returnedValue.push(values[2]+":"+values[3]);
		
      return returnedValue;
   },

   /**
    * Set the value 
    * @param {array} array with 4 Hour strings in display order (format ["HH","MM", "HH","MM"])
    * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
    */
   setValue: function(arr, sendUpdatedEvt) {
		var values = arr[0].split(":").concat(arr[1].split(":"));
      inputEx.TimeRange.superclass.setValue.call(this, values, sendUpdatedEvt);
		this.toogleEndMinutes();
   },

	/**
	 * Disable the last selector and set it to "00" when the third one's value is 24
	 * (it will be inccorect to have an end superior to 24:00)
	 */
	toogleEndMinutes: function(){		
		var endHours = this.inputs[2];
		var endMinutes = this.inputs[3];
		
		if( endHours.getValue() == '24' ){ endMinutes.setValue("00"); endMinutes.disable();}
		else{ endMinutes.enable(); }		
	},

	validate: function(){
		var values = this.getValue();
		
		var hm = values[1].split(":");
		if(hm[0] == '24' && hm[1] != '00'){
			return false;
		}
		
		if(values[0] >= values[1]){
			return false;	
		}
		
		return true;
	}

});

inputEx.registerType("timerange", inputEx.TimeRange);
