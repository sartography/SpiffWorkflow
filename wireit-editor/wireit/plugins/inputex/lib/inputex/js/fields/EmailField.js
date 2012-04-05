(function() {

/**
 * Field that adds the email regexp for validation. Result is always lower case.
 * @class inputEx.EmailField
 * @extends inputEx.StringField
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.EmailField = function(options) {
   inputEx.EmailField.superclass.constructor.call(this,options);
};
YAHOO.lang.extend(inputEx.EmailField, inputEx.StringField, {
   
   /**
    * Set the email regexp and invalid message
    * @param {Object} options Options object as passed to the constructor
    */
   setOptions: function(options) {
      inputEx.EmailField.superclass.setOptions.call(this, options);

      // Overwrite options
      this.options.messages.invalid = inputEx.messages.invalidEmail;
      this.options.regexp = inputEx.regexps.email;
		
		// Validate the domain name ( false by default )
		this.options.fixdomain = (YAHOO.lang.isUndefined(options.fixdomain) ? false : !!options.fixdomain);
   },
   
	validateDomain : function() {
		
		var i, j, val, domain, domainList, domainListLength, groupDomain, groupDomainLength;
		
		val = this.getValue();
		domain = val.split('@')[1];
		
		// List of bad emails (only the first one in each array is the valid one)
		domainList = [
		
			// gmail.com
			["gmail.com","gmail.com.br","_gmail.com","g-mail.com","g.mail.com","g_mail.com","gamail.com","gamil.com","gemail.com","ggmail.com","gimail.com","gmai.com","gmail.cim","gmail.co","gmaill.com","gmain.com","gmaio.com","gmal.com","gmali.com","gmeil.com","gmial.com","gmil.com","gtmail.com","igmail.com","gmail.fr"],
		
			// hotmail.co.uk
			["hotmail.co.uk","hotmail.com.uk"],
		
			// hotmail.com
			["hotmail.com","hotmail.com.br","hotmail.br","0hotmail.com","8hotmail.com","_hotmail.com","ahotmail.com","ghotmail.com","gotmail.com","hatmail.com","hhotmail.com","ho0tmail.com","hogmail.com","hoimail.com","hoitmail.com","homail.com","homtail.com","hootmail.com","hopmail.com","hoptmail.com","hormail.com","hot.mail.com","hot_mail.com","hotail.com","hotamail.com","hotamil.com","hotemail.com","hotimail.com","hotlmail.com","hotmaail.com","hotmael.com","hotmai.com","hotmaial.com","hotmaiil.com","hotmail.acom","hotmail.bom","hotmail.ccom","hotmail.cm","hotmail.co","hotmail.coml","hotmail.comm","hotmail.con","hotmail.coom","hotmail.copm","hotmail.cpm","hotmail.lcom","hotmail.ocm","hotmail.om","hotmail.xom","hotmail2.com","hotmail_.com","hotmailc.com","hotmaill.com","hotmailo.com","hotmaio.com","hotmaiol.com","hotmais.com","hotmal.com","hotmall.com","hotmamil.com","hotmaol.com","hotmayl.com","hotmeil.com","hotmial.com","hotmil.com","hotmmail.com","hotmnail.com","hotmsil.com","hotnail.com","hotomail.com","hottmail.com","hotymail.com","hoymail.com","hptmail.com","htmail.com","htomail.com","ohotmail.com","otmail.com","rotmail.com","shotmail.com","hotmain.com"],
		
			// hotmail.fr
			["hotmail.fr","hotmail.ffr","hotmail.frr","hotmail.fr.br","hotmail.br","0hotmail.fr","8hotmail.fr","_hotmail.fr","ahotmail.fr","ghotmail.fr","gotmail.fr","hatmail.fr","hhotmail.fr","ho0tmail.fr","hogmail.fr","hoimail.fr","hoitmail.fr","homail.fr","homtail.fr","hootmail.fr","hopmail.fr","hoptmail.fr","hormail.fr","hot.mail.fr","hot_mail.fr","hotail.fr","hotamail.fr","hotamil.fr","hotemail.fr","hotimail.fr","hotlmail.fr","hotmaail.fr","hotmael.fr","hotmai.fr","hotmaial.fr","hotmaiil.fr","hotmail.frl","hotmail.frm","hotmail2.fr","hotmail_.fr","hotmailc.fr","hotmaill.fr","hotmailo.fr","hotmaio.fr","hotmaiol.fr","hotmais.fr","hotmal.fr","hotmall.fr","hotmamil.fr","hotmaol.fr","hotmayl.fr","hotmeil.fr","hotmial.fr","hotmil.fr","hotmmail.fr","hotmnail.fr","hotmsil.fr","hotnail.fr","hotomail.fr","hottmail.fr","hotymail.fr","hoymail.fr","hptmail.fr","htmail.fr","htomail.fr","ohotmail.fr","otmail.fr","rotmail.fr","shotmail.fr","hotmain.fr"],
		
			// yahoo.co.in
			["yahoo.co.in","yaho.co.in","yahoo.co.cn","yahoo.co.n","yahoo.co.on","yahoo.coin","yahoo.com.in","yahoo.cos.in","yahoo.oc.in","yaoo.co.in","yhoo.co.in"],
		
			// yahoo.com.br
			["yahoo.com.br","1yahoo.com.br","5yahoo.com.br","_yahoo.com.br","ayhoo.com.br","tahoo.com.br","uahoo.com.br","yagoo.com.br","yahho.com.br","yaho.com.br","yahoo.cm.br","yahoo.co.br","yahoo.com.ar","yahoo.com.b","yahoo.com.be","yahoo.com.ber","yahoo.com.bl","yahoo.com.brr","yahoo.com.brv","yahoo.com.bt","yahoo.com.nr","yahoo.coml.br","yahoo.con.br","yahoo.om.br","yahool.com.br","yahooo.com.br","yahoou.com.br","yaoo.com.br","yaroo.com.br","yhaoo.com.br","yhoo.com.br","yuhoo.com.br"],
		
			// yahoo.com
			["yahoo.com","yahoomail.com","_yahoo.com","ahoo.com","ayhoo.com","eyahoo.com","hahoo.com","sahoo.com","yahho.com","yaho.com","yahol.com","yahoo.co","yahoo.con","yahoo.vom","yahoo0.com","yahoo1.com","yahool.com","yahooo.com","yahoou.com","yahoow.com","yahopo.com","yaloo.com","yaoo.com","yaroo.com","yayoo.com","yhaoo.com","yhoo.com","yohoo.com"],
		
			// yahoo.fr
			["yahoo.fr","yahoomail.fr","_yahoo.fr","ahoo.fr","ayhoo.fr","eyahoo.fr","hahoo.fr","sahoo.fr","yahho.fr","yaho.fr","yahol.fr","yahoo.co","yahoo.con","yahoo.vom","yahoo0.fr","yahoo1.fr","yahool.fr","yahooo.fr","yahoou.fr","yahoow.fr","yahopo.fr","yaloo.fr","yaoo.fr","yaroo.fr","yayoo.fr","yhaoo.fr","yhoo.fr","yohoo.fr"],
		
			// wanadoo.fr
			["wanadoo.fr","wanadoo.frr","wanadoo.ffr","wanado.fr","wanadou.fr","wanadop.fr","wandoo.fr","wanaoo.fr","wannadoo.fr","wanadoo.com","wananadoo.fr","wanadoo.fe","wanaddo.fr","wanadoo.orange","waqnadoo.fr","wandaoo.fr","wannado.fr"],
			
			// msn.com
			["msn.com","mns.com","msn.co"],
			
			// aol.com
			["aol.com","aoel.com","aol.co"]
		];
		
		// Loop 1
		for(i=0, domainListLength = domainList.length; i<domainListLength; i++ ) {
			groupDomain = domainList[i];
			
			// Loop 2
			for(j=0, groupDomainLength = groupDomain.length; j<groupDomainLength; j++ ) {

				// First domain of array
				if( groupDomain.indexOf(domain) === 0) {
					
					// If domain matches the first value of the array it means its valid
					if ( domain === groupDomain[j] ) {
						return true;
					}
				}
				else if ( domain === groupDomain[j] ) {
					var linkId = YAHOO.util.Dom.generateId();
					var that = this;
					
					// Add a listener to the link to allow the user to replace his bad email by clicking the link
					YAHOO.util.Event.addListener(linkId, 'click', function(e){
						YAHOO.util.Event.stopEvent(e);
						var reg = new RegExp(domain, "i");
						var fixedVal = val.replace(reg, groupDomain[0]);
						that.setValue( fixedVal );
					});
					
					// Display the message with the link
					this.options.messages.invalid = inputEx.messages.didYouMeant+"<a href='' id='"+linkId+"' style='color:blue;'>@"+groupDomain[0]+" ?</a>";
					
					// field isnt valid
					return false;
				}
			}
		}
		
		// field is valid
		return true;
	},
	
   validate: function() {
	   var result = inputEx.EmailField.superclass.validate.call(this);
		
		// If we want the domain validation
		if ( !!this.options.fixdomain ) {
	   	this.options.messages.invalid = inputEx.messages.invalidEmail;
			return result && this.validateDomain();
		} else {
			return result;
		}
   },

   /**
    * Set the value to lower case since email have no case
    * @return {String} The email string
    */
   getValue: function() {
      
      var value;
      
      value = inputEx.EmailField.superclass.getValue.call(this);
      
      return inputEx.removeAccents(value.toLowerCase());
   }

});
   
// Specific message for the email field
inputEx.messages.invalidEmail = "Invalid email, ex: sample@test.com";

inputEx.messages.didYouMeant = "Did you mean : ";

// Register this class as "email" type
inputEx.registerType("email", inputEx.EmailField, []);

})();