(function() {

   var lang = YAHOO.lang, Event = YAHOO.util.Event;

/**
 * inputEx.DateSplitField
 * @class inputEx.DateSplitField
 * @extends inputEx.CombineField
 */
inputEx.DateSplitField = function(options) {
   	
   if(!options.dateFormat) {options.dateFormat = inputEx.messages.defaultDateFormat; }
   
   var formatSplit = options.dateFormat.split("/");
   this.yearIndex = inputEx.indexOf('Y',formatSplit);
   this.monthIndex = inputEx.indexOf('m',formatSplit);
   this.dayIndex = inputEx.indexOf('d',formatSplit);
   
   options.fields = [];
   for(var i = 0 ; i < 3 ; i++) {
      if(i == this.dayIndex) {
         options.fields.push({type: 'integer', typeInvite: inputEx.messages.dayTypeInvite, size: 2 });
      }
      else if(i == this.yearIndex) {
         options.fields.push({type: 'integer', typeInvite: inputEx.messages.yearTypeInvite, size: 4 });
      }
      else {
         options.fields.push({type: 'integer', typeInvite: inputEx.messages.monthTypeInvite, size: 2 });
      }
   }

   options.separators = options.separators || [false,"&nbsp;","&nbsp;",false];
   
	inputEx.DateSplitField.superclass.constructor.call(this,options);

   this.initAutoTab();
};

lang.extend(inputEx.DateSplitField, inputEx.CombineField, {
   
   /**
	 * Set the value. Format the date according to options.dateFormat
	 * @param {Date} val Date to set
	 * @param {boolean} [sendUpdatedEvt] (optional) Wether this setValue should fire the updatedEvt or not (default is true, pass false to NOT send the event)
	 */
   setValue: function(value, sendUpdatedEvt) {
      var values = [];
      
      // !value catches "" (empty field), and invalid dates
      if(!value || !lang.isFunction(value.getTime) || !lang.isNumber(value.getTime()) ) {
         values[this.monthIndex] = "";
         values[this.yearIndex] = "";
         values[this.dayIndex] = "";
      } else {
         for(var i = 0 ; i < 3 ; i++) {
            values.push( i == this.dayIndex ? value.getDate() : (i==this.yearIndex ? value.getFullYear() : value.getMonth()+1 ) );
         }
      }
      inputEx.DateSplitField.superclass.setValue.call(this, values, sendUpdatedEvt);
   },
   
   getValue: function() {
      if (this.isEmpty()) return "";
      
      var values = inputEx.DateSplitField.superclass.getValue.call(this);
      
      return new Date(values[this.yearIndex], values[this.monthIndex]-1, values[this.dayIndex] );
   },
   
   validate: function() {
      var subFieldsValidation = inputEx.DateSplitField.superclass.validate.call(this);
      if (!subFieldsValidation) return false;
      
      var values = inputEx.DateSplitField.superclass.getValue.call(this);
      var day = values[this.dayIndex];
      var month = values[this.monthIndex];
      var year = values[this.yearIndex];
      
      var val = this.getValue();
      //console.log("datesplit value = ",val);
      
      // 3 empty fields
      if (val == "") return true;
      
      // if a field is empty, it will be set by default (day : 31, month:12, year: 1899/1900)
      //   -> val == "" MUST be checked first !
      if (day == "" || month == "" || year == "") return false;
      
      if (year < 0 || year > 9999 || day < 1 || day > 31 || month < 1 || month > 12) return false;
      
      // val == any date -> true
      // val == "Invalid Date" -> false
      return (val != "Invalid Date");
   },
   
	isEmpty: function() {
	   var values = inputEx.DateSplitField.superclass.getValue.call(this);
	   return (values[this.monthIndex] == "" && values[this.yearIndex] == "" &&  values[this.dayIndex] == "");
	},
	
	initAutoTab: function() {
	   // "keypress" event codes for numeric keys (keyboard & numpad) 
	   //  (warning : "keydown" codes are different with numpad)
	   var numKeyCodes = [48,49,50,51,52,53,54,55,56,57];
	   
      // verify charCode (don't auto tab when pressing "tab", "arrow", etc...)
	   var checkNumKey = function(charCode) {
   	   for (var i=0, length=numKeyCodes.length; i < length; i++) {
   	      if (charCode == numKeyCodes[i]) return true;
   	   }
   	   return false;       
	   };
	   
	   // Function that checks charCode and execute tab action
	   var that = this;
	   var autoTab = function(inputIndex) {
         // later to let input update its value
   	   lang.later(0, that, function() {
      	   var input = that.inputs[inputIndex];
      	   
      	   // check input.el.value (string) because getValue doesn't work
      	   // example : if input.el.value == "06", getValue() == 6 (length == 1 instead of 2)
      	   if (input.el.value.length == input.options.size) {
      	      that.inputs[inputIndex+1].focus();
      	   }
   	   });
	   };
	   
	   // add listeners on inputs
	   Event.addListener(this.inputs[0].el, "keypress", function(e) {
	      if (checkNumKey(Event.getCharCode(e))) {
            autoTab(0);
         }
   	}, this, true);
	   Event.addListener(this.inputs[1].el, "keypress", function(e) {
	      if (checkNumKey(Event.getCharCode(e))) {
            autoTab(1);
         }
   	}, this, true);
	}
   
});

inputEx.messages.monthTypeInvite = "Month";
inputEx.messages.dayTypeInvite = "Day";
inputEx.messages.yearTypeInvite = "Year";

// Register this class as "datesplit" type
inputEx.registerType("datesplit", inputEx.DateSplitField);

})();