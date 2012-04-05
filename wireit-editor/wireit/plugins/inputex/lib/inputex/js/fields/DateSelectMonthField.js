(function () {
	
	var lang = YAHOO.lang;
	
	/**
	 * A field to enter a date with 2 strings and a select
	 * @class inputEx.DateSelectMonthField
	 * @extends inputEx.CombineField
	 */
	inputEx.DateSelectMonthField = function (options) {
		
		var formatSplit, selectOptions, i, j, monthsNb;
		
		if (!options.dateFormat) {
			options.dateFormat = inputEx.messages.defaultDateFormat;
		}
		
		formatSplit = options.dateFormat.split("/");
		
		this.yearIndex = inputEx.indexOf('Y', formatSplit);
		this.monthIndex = inputEx.indexOf('m', formatSplit);
		this.dayIndex = inputEx.indexOf('d', formatSplit);
		
		options.fields = [];
		
		for (i = 0 ; i < 3 ; i += 1) {
			
			if (i === this.dayIndex) {
				options.fields.push({ type: 'string', typeInvite: inputEx.messages.dayTypeInvite, size: 2 });
			}
			else if (i === this.yearIndex) {
				options.fields.push({ type: 'string', typeInvite: inputEx.messages.yearTypeInvite, size: 4 });
			}
			else {
				
				selectOptions = [{ value: -1, label: inputEx.messages.selectMonth }];
				
				for (j = 0, monthsNb = inputEx.messages.months.length; j < monthsNb; j += 1) {
					selectOptions.push({ value: j, label: inputEx.messages.months[j] });
				}
				
				options.fields.push({ type: 'select', choices: selectOptions, value: -1 });
			}
			
		}
		
		options.separators = options.separators || [false, "&nbsp;", "&nbsp;", false];
		
		inputEx.DateSelectMonthField.superclass.constructor.call(this, options);
	};
	
	lang.extend(inputEx.DateSelectMonthField, inputEx.CombineField, {
		
		setValue: function (value, sendUpdatedEvt) {
			
			var values, i;
			
			values = [];
			
			// !value catches "" (empty field), other tests invalid dates (Invalid Date, or NaN)
			if (!value || !(value instanceof Date) || !lang.isNumber(value.getTime())) {
				values[this.monthIndex] = -1;
				values[this.yearIndex] = "";
				values[this.dayIndex] = "";
			} else {
				for (i = 0 ; i < 3 ; i += 1) {
					values.push(i === this.dayIndex ? value.getDate() : (i === this.yearIndex ? value.getFullYear() : value.getMonth()));
				}
			}
			inputEx.DateSelectMonthField.superclass.setValue.call(this, values, sendUpdatedEvt);
		},
		
		getValue: function () {
			
			var values;
			
			if (this.isEmpty()) {
				return "";
			}
			
			values = inputEx.DateSelectMonthField.superclass.getValue.call(this);
			
			// if selected month index is -1, new Date(..) would create a valid date with month == December !!!)
			if (values[this.monthIndex] === -1) {
				return new Date(NaN, NaN, NaN); // -> Invalid Date (Firefox) or NaN (IE) (both instanceof Date ...)
			}
			
			return new Date(parseInt(values[this.yearIndex], 10), values[this.monthIndex], parseInt(values[this.dayIndex], 10));
		},
		
		validate: function () {
			
			var val = this.getValue();
			
			// empty field
			if (val === '') {
				// validate only if not required
				return !this.options.required;
			}
			
			// val is :
			//  -> a Date, when valid
			//  -> an Invalid Date (== "Invalid Date"), when invalid on FF
			//  -> NaN, when invalid on IE
			//
			// These 3 cases would pass the "val instanceof Date" test, 
			// but last 2 cases return NaN on val.getDate(), so "isFinite" test fails.
			return (val instanceof Date && lang.isNumber(val.getTime()));
		},
		
		isEmpty: function () {
			var values = inputEx.DateSelectMonthField.superclass.getValue.call(this);
			return (values[this.monthIndex] === -1 && values[this.yearIndex] === "" &&  values[this.dayIndex] === "");
		}
		
	});
	
	inputEx.messages.selectMonth = "- Select Month -";
	inputEx.messages.dayTypeInvite = "Day";
	inputEx.messages.yearTypeInvite = "Year";
	
	// Register this class as "dateselectmonth" type
	inputEx.registerType("dateselectmonth", inputEx.DateSelectMonthField);
	
}());