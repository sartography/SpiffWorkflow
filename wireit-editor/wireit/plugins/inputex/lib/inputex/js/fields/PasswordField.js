(function() {
	
   var Event=YAHOO.util.Event,lang=YAHOO.lang;
	
/**
 * Create a password field.
 * @class inputEx.PasswordField
 * @extends inputEx.StringField
 * @constructor
 * @param {Object} options inputEx.Field options object
 * <ul>
 *   <li>confirmPasswordField: the PasswordField instance to compare to when using 2 password fields for password creation (please use the setConfirmationField method)</li>
 *   <li>strengthIndicator: display a widget to indicate password strength (default false)</li>
 *   <li>capsLockWarning: display a warning if CapsLock is on (default false)</li>
 *   <li>confirm: id of the field to compare to</li>
 * </ul>
 */
inputEx.PasswordField = function(options) {
	inputEx.PasswordField.superclass.constructor.call(this,options);
};

/**
 * Keep track of all instances, indexed by ids, for the password confirmation field
 */
inputEx.PasswordField.byId = {}; 

lang.extend(inputEx.PasswordField, inputEx.StringField, {
   
	/**
	 * Add the password regexp, strengthIndicator, capsLockWarning
	 * @param {Object} options Options object as passed to the constructor
	 */
	setOptions: function(options) {
	   inputEx.PasswordField.superclass.setOptions.call(this, options);
	   
   	this.options.className = options.className ? options.className : "inputEx-Field inputEx-PasswordField";
	   
	   // Add the password regexp (overridable)
	   this.options.regexp = options.regexp || inputEx.regexps.password;
	  
		// display a strength indicator
		this.options.strengthIndicator = YAHOO.lang.isUndefined(options.strengthIndicator) ? false : options.strengthIndicator;
		
		// capsLockWarning
		this.options.capsLockWarning = YAHOO.lang.isUndefined(options.capsLockWarning) ? false : options.capsLockWarning;
		
		// confirm option, pass the id of the password field to confirm
		inputEx.PasswordField.byId[options.id] = this;
		var passwordField;
		if(options.confirm && (passwordField = inputEx.PasswordField.byId[options.confirm]) ) {
			this.setConfirmationField(passwordField);
		}
	},
	
	/**
	 * Set the el type to 'password'
	 */
	renderComponent: function() {
	   // IE doesn't want to set the "type" property to 'password' if the node has a parent
	   // even if the parent is not in the DOM yet !!
	   
      // This element wraps the input node in a float: none div
      this.wrapEl = inputEx.cn('div', {className: 'inputEx-StringField-wrapper'});
	      
		// Attributes of the input field
	   var attributes = {};
	   attributes.type = 'password';
	   attributes.size = this.options.size;
	   if(this.options.name) attributes.name = this.options.name;
	
	   // Create the node
		this.el = inputEx.cn('input', attributes);
		
		//inputEx.PasswordField.byId
		
		// Append it to the main element
		this.wrapEl.appendChild(this.el);
      this.fieldContainer.appendChild(this.wrapEl);
		
		// Caps lock warning
		if(this.options.capsLockWarning) {
		   this.capsLockWarning = inputEx.cn('div',{className: 'capsLockWarning'},{display: 'none'},inputEx.messages.capslockWarning);
		   this.wrapEl.appendChild(this.capsLockWarning);
	   }
	   
	   // Password strength indicator
		if(this.options.strengthIndicator) {
		   this.strengthEl = inputEx.cn('div', {className: 'inputEx-Password-StrengthIndicator'}, null, inputEx.messages.passwordStrength);
		   this.strengthBlocks = [];
		   for(var i = 0 ; i < 4 ; i++) {
		      this.strengthBlocks[i] = inputEx.cn('div', {className: 'inputEx-Password-StrengthIndicatorBlock'});
		      this.strengthEl.appendChild( this.strengthBlocks[i] );
		   }
		   this.wrapEl.appendChild(this.strengthEl);
		}
	},
	   
	/**
	 * Set this field as the confirmation for the targeted password field:
	 * @param {inputEx.PasswordField} passwordField The target password field
	 */
	setConfirmationField: function(passwordField) {
	   this.options.confirmPasswordField = passwordField;
	   this.options.messages.invalid = inputEx.messages.invalidPasswordConfirmation;
	   this.options.confirmPasswordField.options.confirmationPasswordField = this;
	},
	
	/**
	 * The validation adds the confirmation password field support
	 */
	validate: function() {
	   if(this.options.confirmPasswordField) {
	      if(this.options.confirmPasswordField.getValue() != this.getValue() ) {
	         return false;
	      }
	   }
	   return inputEx.PasswordField.superclass.validate.call(this);
	},
	
	/**
	 * Change the state string
	 */
	getStateString: function(state) {
	   if(state == inputEx.stateInvalid && this.options.minLength && this.el.value.length < this.options.minLength) {  
	      return inputEx.messages.invalidPassword[0]+this.options.minLength+inputEx.messages.invalidPassword[1];
      }
	   return inputEx.StringField.superclass.getStateString.call(this, state);
	},
	
	/**
	 * Update the state of the confirmation field
	 * @param {Event} e The original input event
	 */
	onInput: function(e) {
	   inputEx.PasswordField.superclass.onInput.call(this,e);
	   if(this.options.confirmationPasswordField) {
	      this.options.confirmationPasswordField.setClassFromState();
	   }
	},
	
	/**
	 * callback to display the capsLockWarning
	 */
	onKeyPress: function(e) {
	   inputEx.PasswordField.superclass.onKeyPress.call(this,e);
	   
	   if(this.options.capsLockWarning) {
         var ev = e ? e : window.event;
         if (!ev) {
            return;
         }
         var targ = ev.target ? ev.target : ev.srcElement;
      
         // get key pressed
         var which = -1;
         if (ev.which) {
            which = ev.which;
         } else if (ev.keyCode) {
            which = ev.keyCode;
         }
         // get shift status
         var shift_status = false;
         if (ev.shiftKey) {
            shift_status = ev.shiftKey;
         } else if (ev.modifiers) {
            shift_status = !!(ev.modifiers & 4);
         }
         var displayWarning = ((which >= 65 && which <=  90) && !shift_status) ||
                              ((which >= 97 && which <= 122) && shift_status);
         this.setCapsLockWarning(displayWarning);
      }
      
	},
	
	/**
	 * onkeyup callback to update the strength indicator
	 */
	onKeyUp: function(e) {
 	   inputEx.PasswordField.superclass.onKeyUp.call(this,e);
       if(this.options.strengthIndicator) {
          lang.later( 0, this, this.updateStrengthIndicator);
       }
     },
     
     /**
      * Show or hide the caps lock warning given the status
      */
     setCapsLockWarning: function(status) {
        this.capsLockWarning.style.display = status ? '' : 'none';
     },
     
     /**
      * Update the strength indicator (called by onKeyPress)
      */
     updateStrengthIndicator: function() {
  	     var strength = inputEx.PasswordField.getPasswordStrength(this.getValue());
        for(var i = 0 ; i < 4 ; i++) {
           var on = (strength >= i*25) && (strength>0);
           YAHOO.util.Dom.setStyle(this.strengthBlocks[i],"background-color", on ? "#4AE817" : "#FFFFFF");
		  }
     }
   
	
});

/**
 * Return an integer within [0,100] that quantify the password strength
 * Function taken from Mozilla Code: (changed a little bit the values)
 * http://lxr.mozilla.org/seamonkey/source/security/manager/pki/resources/content/password.js
 */
inputEx.PasswordField.getPasswordStrength = function(pw) {
    // Here is how we weigh the quality of the password
    // number of characters
    // numbers
    // non-alpha-numeric chars
    // upper and lower case characters

    //length of the password
    var pwlength=(pw.length);
    //if (pwlength>5)
    //     pwlength=5;
    if (pwlength>7)
         pwlength=7;

    //use of numbers in the password
    var numnumeric = pw.replace (/[0-9]/g, "");
    var numeric=(pw.length - numnumeric.length);
    if (numeric>3)
        numeric=3;

    //use of symbols in the password
    var symbols = pw.replace (/\W/g, "");
    var numsymbols=(pw.length - symbols.length);
    if (numsymbols>3)
        numsymbols=3;

    //use of uppercase in the password
    var numupper = pw.replace (/[A-Z]/g, "");
    var upper=(pw.length - numupper.length);
    if (upper>3)
        upper=3;

    //var pwstrength=((pwlength*10)-20) + (numeric*10) + (numsymbols*15) + (upper*10);
    var pwstrength=((pwlength*10)-20) + (numeric*10) + (numsymbols*20) + (upper*10);

    // make sure we're give a value between 0 and 100
    if ( pwstrength < 0 ) { pwstrength = 0; }
    if ( pwstrength > 100 ) { pwstrength = 100;}
    return pwstrength;
};

	
// Specific message for the password field
inputEx.messages.invalidPassword = ["The password schould contain at least "," numbers or characters"];
inputEx.messages.invalidPasswordConfirmation = "Passwords are different !";
inputEx.messages.capslockWarning = "Warning: CapsLock is on";
inputEx.messages.passwordStrength = "Password Strength";

// Register this class as "password" type
inputEx.registerType("password", inputEx.PasswordField, [
   {type: 'boolean', label: 'Strength indicator', name: 'strengthIndicator', value: false },
   {type: 'boolean', label: 'CapsLock warning', name: 'capsLockWarning', value: false }
]);
	
})();