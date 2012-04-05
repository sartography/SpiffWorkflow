/**
 * Crappy DOT parser
 *
 * 	Usage: DotParser.parse(dotString);
 *
 */
DotParser = (function() {
	
	var Tokenizer = function(str) {
		this.str = str;
	};

	Tokenizer.prototype = {

		reco: function(s) {
			var matches = this.str.match(/^(\S+)\s*/);
			if (matches) {
				return (s == matches[1]);
			} else {
				return false;
			}
		},

		recoA: function(s) {
			var matches = this.str.match(/^(\S+)\s*/);
			if (matches) {
				this.str = this.str.substr(matches[0].length);
				return (s == matches[1]);
			} else {
				return false;
			}
		},

		takeChars: function(num) {
			if (!num) {
				num = 1;
			}
			var tokens = new Array();
			while (num--) {
				var matches = this.str.match(/^(\S+)\s*/);
				if (matches) {
					this.str = this.str.substr(matches[0].length);
					tokens.push(matches[1]);
				} else {
					tokens.push(false);
				}
			}
			if (1 == tokens.length) {
				return tokens[0];
			} else {
				return tokens;
			}
		},
		takeNumber: function(num) {
			if (!num) {
				num = 1;
			}
			if (1 == num) {
				return Number(this.takeChars());
			} else {
				var tokens = this.takeChars(num);
				while (num--) {
					tokens[num] = Number(tokens[num]);
				}
				return tokens;
			}
		},
		takeString: function() {
			var byte_count = Number(this.takeChars()), char_count = 0, char_code;
			if ('-' != this.str.charAt(0)) {
				return false;
			}
			while (0 < byte_count) {
				++char_count;
				char_code = this.str.charCodeAt(char_count);
				if (0x80 > char_code) {
					--byte_count;
				} else if (0x800 > char_code) {
					byte_count -= 2;
				} else {
					byte_count -= 3;
				}
			}
			var str = this.str.substr(1, char_count);
			this.str = this.str.substr(1 + char_count).replace(/^\s+/, '');
			return str;
		}
	};


	
	var _graph = null;
	var tokenizer = null;
	var _log = null;
	
	function log(o) {
		_log.push(o);
	}

	function parse(text) {
		_graph = {
			nodes: [],
			edges: []
		};
		_log = [];
		tokenizer = new Tokenizer(text);	
		
		graph();
		
		return _graph;
	}
	
	function graph() {
		
		// strict property
		_graph.strict = tokenizer.reco("strict") ? tokenizer.recoA("strict") : false;
		
		// type property
		_graph.type = tokenizer.takeChars();
		if( _graph.type != "graph" && _graph.type != "digraph") {
			log("Error, expecting 'graph' or 'digraph'");
		}
		
		// id
		if( !tokenizer.reco('{') ) {
			_graph.ID = id();
		}
		
		// {
		if( !tokenizer.recoA('{') ) {
			log("Error, expecting '{'");
		}
		
		stmt_list();
		
		// }
		if( !tokenizer.recoA('}') ) {
			log("Error, expecting '}' got "+tokenizer.takeChars());
		}
		
	}
	
	function id() {
		return tokenizer.takeChars(); // TODO
	}
	
	
	function stmt_list() { 
		stmt(); 
		stmt_list1(); 
	}
	
	function stmt_list1() {  
		while( tokenizer.recoA(";") ) { 
			stmt(); 
		} 
	}
	
	function stmt () { 
		if(tokenizer.reco('}')) {
			return;
		} 
		_graph.edges.push( edge_stmt() ); 
	}
	
	function edge_stmt() {
		return {
			node1: node_id(),
			op: tokenizer.takeChars(),
			node2: node_id()
		};
	}
	
	function node_id() {
		var id = tokenizer.takeChars();
		if(_graph.nodes.indexOf(id) == -1) {
			_graph.nodes.push(id);
		}
		return id;
	}
	
	return {
		parse: parse
	};
	
})();