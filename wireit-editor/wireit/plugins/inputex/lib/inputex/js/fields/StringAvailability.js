(function() {
	
   var Event=YAHOO.util.Event,DOM=YAHOO.util.Dom,lang=YAHOO.lang;

/**
 * String field that sends an Ajax request to check if it is available
 * @class inputEx.StringAvailability
 * @extends inputEx.StringField
 * @constructor
 * @param {Object} options 
 */
inputEx.StringAvailability = function(options) {
	inputEx.StringAvailability.superclass.constructor.call(this,options);
};

lang.extend(inputEx.StringAvailability, inputEx.StringField, {
   
	/**
	 * @param {Object} options Options object as passed to the constructor
	 */
	setOptions: function(options) {
	   inputEx.StringAvailability.superclass.setOptions.call(this, options);
		
		// Server URI
		this.options.uri = options.uri;
				
		// Messages
		this.options.messages.stringLoading = (options.messages && options.messages.stringLoading) ? options.messages.stringLoading : inputEx.messages.stringLoading;
		this.options.messages.stringAvailable = (options.messages && options.messages.stringAvailable) ? options.messages.stringAvailable : inputEx.messages.stringAvailable;
		this.options.messages.stringUnAvailable = (options.messages && options.messages.stringUnAvailable) ? options.messages.stringUnAvailable : inputEx.messages.stringUnAvailable;
		
		// Must hide default Msg to do it custom
		this.options.showMsg = false;
	},
	
	renderComponent: function() {
		inputEx.StringAvailability.superclass.renderComponent.call(this);		
		
		this.availabilityDiv = inputEx.cn('div', {'className':'availabilityDiv'});
		this.availabilityDivIcon = inputEx.cn('div', {'className':'icon'});
		this.availabilityDivText = inputEx.cn('div', {'className':'text'});
		
		this.availabilityDiv.appendChild(this.availabilityDivIcon);
		this.availabilityDiv.appendChild(this.availabilityDivText);
		this.availabilityDiv.appendChild(inputEx.cn('div', {'className':'clear'}));
		
	},
	
	render: function() {
		inputEx.StringAvailability.superclass.render.call(this);
		
		// Must do it after renderComponent else this.fieldContainer isn't attached to a DOM element
		DOM.insertAfter(this.availabilityDiv, this.fieldContainer);
	},
	
	onKeyPress: function() {
		// Must do this to wait that value is updated (for the getValue())
		lang.later(0, this, function(){
			
		// If field is empty
		if(this.getValue() === ''){
			this.stopTimer();
			this.setAvailabilityState(this.options.required ? "required" : "none");
			return;
		}

		this.resetTimer();
		this.setAvailabilityState("loading");
		
		});
	},
	
	resetTimer: function() {
		this.stopTimer();
		this.startTimer();
	},
	
	startTimer: function() {
		var that = this;
		this.timerId = setTimeout(function(){
			that.getAvailability(that.getValue());
		},500);
	},
	
	stopTimer: function() {
		if(this.timerId){
			clearTimeout(this.timerId);
			delete this.timerId;
		}
	},
	
	/**
	 * What to do when the string is available
	 */
	onAvailable: function(){
		this.setAvailabilityState("available");
		this.isAvailable = true;
	},
	
	/**
	 * What to do when the string is NOT available
	 */
	onUnavailable: function(){
		this.setAvailabilityState("unavailable");
		this.isAvailable = false;
	},
	
	setAvailabilityState: function(state) {
		
		if(state === "none"){
			this.availabilityDivText.innerHTML = '';
			DOM.setAttribute(this.availabilityDiv, 'class', 'availabilityDiv');
			this.availabilityDiv.style.display = 'none';
			return;
		}
		else if(state === "loading"){
			this.availabilityDivText.innerHTML = this.options.messages.stringLoading;
		}
		else if(state === "available"){
			this.availabilityDivText.innerHTML = this.options.messages.stringAvailable;
		}
		else if(state === "unavailable"){
			this.availabilityDivText.innerHTML = this.options.messages.stringUnAvailable;
		}
		else if(state === "required"){
			this.availabilityDivText.innerHTML = this.options.messages.required;
		}
		
		DOM.setAttribute(this.availabilityDiv, 'class', 'availabilityDiv '+state);
		this.availabilityDiv.style.display = 'block';

	},
	
	
	setClassFromState: function(){
		inputEx.StringAvailability.superclass.setClassFromState.call(this);		
		
		var state = this.getState();
		
		if(state === "required"){
			this.setAvailabilityState(state);
		}
	},
	
	validate: function(){
		var valid = inputEx.StringAvailability.superclass.validate.call(this);
		if(!lang.isUndefined(this.isAvailable)){
			valid = this.isAvailable && valid;
		}
		
		return valid;
	},
	
	/**
	 * Perform the Ajax request
	 */
	getAvailability: function(string) {
		// TODO split params ? &
		YAHOO.util.Connect.asyncRequest('GET', this.options.uri+'?availabilityRequest='+string, {
			success: function(o) {
				var obj = lang.JSON.parse(o.responseText);
				if(obj === "true" || !!obj){
					this.onAvailable();
				}
				else if(obj === "false" || !obj){
					this.onUnavailable();
				}
				else{
					this.failure(o);
				}
			},
			failure: function(o) {
				// TODO ?
			},
			scope: this
		});
	}
	   
});


// Specific message for the stringAvailability field
inputEx.messages.stringLoading = "Checking if available ...";
inputEx.messages.stringAvailable = "This ressource is available";
inputEx.messages.stringUnAvailable = "This ressource is not available";

// Register this class as "string-availability" type
inputEx.registerType("string-availability", inputEx.StringAvailability);


})();