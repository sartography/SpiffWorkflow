(function () {
	
	/**
	 * Utilities to run inputEx examples
	 */
	
	// Decode html entities
	var html_entity_decode = function (text) {
		text = text.replace(/&quot;/g,'"'); // 34 22
		text = text.replace(/&amp;/g,'&'); // 38 26	
		text = text.replace(/&#39;/g,"'"); // 39 27
		text = text.replace(/&lt;/g,'<'); // 60 3C
		text = text.replace(/&gt;/g,'>'); // 62 3E
		text = text.replace(/&circ;/g,'^'); // 94 5E
		text = text.replace(/&lsquo;/g,'‘'); // 145 91
		text = text.replace(/&rsquo;/g,'’'); // 146 92
		text = text.replace(/&ldquo;/g,'“'); // 147 93
		text = text.replace(/&rdquo;/g,'”'); // 148 94
		text = text.replace(/&bull;/g,'•'); // 149 95
		text = text.replace(/&ndash;/g,'–'); // 150 96
		text = text.replace(/&mdash;/g,'—'); // 151 97
		text = text.replace(/&tilde;/g,'˜'); // 152 98
		text = text.replace(/&trade;/g,'™'); // 153 99
		text = text.replace(/&scaron;/g,'š'); // 154 9A
		text = text.replace(/&rsaquo;/g,'›'); // 155 9B
		text = text.replace(/&oelig;/g,'œ'); // 156 9C
		text = text.replace(/&#357;/g,''); // 157 9D
		text = text.replace(/&#382;/g,'ž'); // 158 9E
		text = text.replace(/&Yuml;/g,'Ÿ'); // 159 9F
		text = text.replace(/&nbsp;/g,' '); // 160 A0
		text = text.replace(/&iexcl;/g,'¡'); // 161 A1
		text = text.replace(/&cent;/g,'¢'); // 162 A2
		text = text.replace(/&pound;/g,'£'); // 163 A3
		text = text.replace(/&curren;/g,' '); // 164 A4
		text = text.replace(/&yen;/g,'¥'); // 165 A5
		text = text.replace(/&brvbar;/g,'¦'); // 166 A6
		text = text.replace(/&sect;/g,'§'); // 167 A7
		text = text.replace(/&uml;/g,'¨'); // 168 A8
		text = text.replace(/&copy;/g,'©'); // 169 A9
		text = text.replace(/&ordf;/g,'ª'); // 170 AA
		text = text.replace(/&laquo;/g,'«'); // 171 AB
		text = text.replace(/&not;/g,'¬'); // 172 AC
		text = text.replace(/&shy;/g,'­'); // 173 AD
		text = text.replace(/&reg;/g,'®'); // 174 AE
		text = text.replace(/&macr;/g,'¯'); // 175 AF
		text = text.replace(/&deg;/g,'°'); // 176 B0
		text = text.replace(/&plusmn;/g,'±'); // 177 B1
		text = text.replace(/&sup2;/g,'²'); // 178 B2
		text = text.replace(/&sup3;/g,'³'); // 179 B3
		text = text.replace(/&acute;/g,'´'); // 180 B4
		text = text.replace(/&micro;/g,'µ'); // 181 B5
		text = text.replace(/&para/g,'¶'); // 182 B6
		text = text.replace(/&middot;/g,'·'); // 183 B7
		text = text.replace(/&cedil;/g,'¸'); // 184 B8
		text = text.replace(/&sup1;/g,'¹'); // 185 B9
		text = text.replace(/&ordm;/g,'º'); // 186 BA
		text = text.replace(/&raquo;/g,'»'); // 187 BB
		text = text.replace(/&frac14;/g,'¼'); // 188 BC
		text = text.replace(/&frac12;/g,'½'); // 189 BD
		text = text.replace(/&frac34;/g,'¾'); // 190 BE
		text = text.replace(/&iquest;/g,'¿'); // 191 BF
		text = text.replace(/&Agrave;/g,'À'); // 192 C0
		text = text.replace(/&Aacute;/g,'Á'); // 193 C1
		text = text.replace(/&Acirc;/g,'Â'); // 194 C2
		text = text.replace(/&Atilde;/g,'Ã'); // 195 C3
		text = text.replace(/&Auml;/g,'Ä'); // 196 C4
		text = text.replace(/&Aring;/g,'Å'); // 197 C5
		text = text.replace(/&AElig;/g,'Æ'); // 198 C6
		text = text.replace(/&Ccedil;/g,'Ç'); // 199 C7
		text = text.replace(/&Egrave;/g,'È'); // 200 C8
		text = text.replace(/&Eacute;/g,'É'); // 201 C9
		text = text.replace(/&Ecirc;/g,'Ê'); // 202 CA
		text = text.replace(/&Euml;/g,'Ë'); // 203 CB
		text = text.replace(/&Igrave;/g,'Ì'); // 204 CC
		text = text.replace(/&Iacute;/g,'Í'); // 205 CD
		text = text.replace(/&Icirc;/g,'Î'); // 206 CE
		text = text.replace(/&Iuml;/g,'Ï'); // 207 CF
		text = text.replace(/&ETH;/g,'Ð'); // 208 D0
		text = text.replace(/&Ntilde;/g,'Ñ'); // 209 D1
		text = text.replace(/&Ograve;/g,'Ò'); // 210 D2
		text = text.replace(/&Oacute;/g,'Ó'); // 211 D3
		text = text.replace(/&Ocirc;/g,'Ô'); // 212 D4
		text = text.replace(/&Otilde;/g,'Õ'); // 213 D5
		text = text.replace(/&Ouml;/g,'Ö'); // 214 D6
		text = text.replace(/&times;/g,'×'); // 215 D7
		text = text.replace(/&Oslash;/g,'Ø'); // 216 D8
		text = text.replace(/&Ugrave;/g,'Ù'); // 217 D9
		text = text.replace(/&Uacute;/g,'Ú'); // 218 DA
		text = text.replace(/&Ucirc;/g,'Û'); // 219 DB
		text = text.replace(/&Uuml;/g,'Ü'); // 220 DC
		text = text.replace(/&Yacute;/g,'Ý'); // 221 DD
		text = text.replace(/&THORN;/g,'Þ'); // 222 DE
		text = text.replace(/&szlig;/g,'ß'); // 223 DF
		text = text.replace(/&agrave;/g,'à'); // 224 E0
		text = text.replace(/&aacute;/g,'á'); // 225 E1
		text = text.replace(/&acirc;/g,'â'); // 226 E2
		text = text.replace(/&atilde;/g,'ã'); // 227 E3
		text = text.replace(/&auml;/g,'ä'); // 228 E4
		text = text.replace(/&aring;/g,'å'); // 229 E5
		text = text.replace(/&aelig;/g,'æ'); // 230 E6
		text = text.replace(/&ccedil;/g,'ç'); // 231 E7
		text = text.replace(/&egrave;/g,'è'); // 232 E8
		text = text.replace(/&eacute;/g,'é'); // 233 E9
		text = text.replace(/&ecirc;/g,'ê'); // 234 EA
		text = text.replace(/&euml;/g,'ë'); // 235 EB
		text = text.replace(/&igrave;/g,'ì'); // 236 EC
		text = text.replace(/&iacute;/g,'í'); // 237 ED
		text = text.replace(/&icirc;/g,'î'); // 238 EE
		text = text.replace(/&iuml;/g,'ï'); // 239 EF
		text = text.replace(/&eth;/g,'ð'); // 240 F0
		text = text.replace(/&ntilde;/g,'ñ'); // 241 F1
		text = text.replace(/&ograve;/g,'ò'); // 242 F2
		text = text.replace(/&oacute;/g,'ó'); // 243 F3
		text = text.replace(/&ocirc;/g,'ô'); // 244 F4
		text = text.replace(/&otilde;/g,'õ'); // 245 F5
		text = text.replace(/&ouml;/g,'ö'); // 246 F6
		text = text.replace(/&divide;/g,'÷'); // 247 F7
		text = text.replace(/&oslash;/g,'ø'); // 248 F8
		text = text.replace(/&ugrave;/g,'ù'); // 249 F9
		text = text.replace(/&uacute;/g,'ú'); // 250 FA
		text = text.replace(/&ucirc;/g,'û'); // 251 FB
		text = text.replace(/&uuml;/g,'ü'); // 252 FC
		text = text.replace(/&yacute;/g,'ý'); // 253 FD
		text = text.replace(/&thorn;/g,'þ'); // 254 FE
		text = text.replace(/&yuml;/g,'ÿ'); // 255 FF
		return text;
	};
	
	
	// Required for the ListField
	inputEx.spacerUrl = "../images/space.gif";
	
	
	YAHOO.util.Event.onDOMReady(function() {
		
		var examples, i, length, textarea, code;
		
		examples = YAHOO.util.Dom.getElementsByClassName('JScript');
		
		for(i = 0, length = examples.length ; i < length ; i += 1) {
			
			textarea = examples[i];
			
			try {
				// get example code and filter html entities
				code = html_entity_decode(textarea.innerHTML);
				
				// wrap in anonymous to create a separate context for local variables
				// (avoid collision between variables from different examples !)
				code = "(function () {"+code+"}());";
				
				eval(code);
			}
			catch(ex) {
				if(console) {
					console.log("Error while executing example "+(i+1), ex);
				}
			}
		}
		
		dp.SyntaxHighlighter.HighlightAll('code');
	});

}());
