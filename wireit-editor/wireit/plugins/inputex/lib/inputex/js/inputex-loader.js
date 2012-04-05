(function() {
/**
 * Add inputEx modules to a YUI loader
 * @param {YUILoader} yuiLoader YUI Loader instance
 * @param {String} inputExPath (optional) inputExPath
 */
YAHOO.addInputExModules = function(yuiLoader, inputExPath) {
	var pathToInputEx = inputExPath || '../';
	var modules = [
	   // inputEx base
		{
			name: 'inputex-css',
			type: 'css',
			fullpath: pathToInputEx+'css/inputEx.css',
			requires: ['reset', 'fonts']
		},
   	{
   	   name: 'inputex',
   	   type: 'js',
   	   fullpath: pathToInputEx+'js/inputex.js',
   	 	varName: 'inputEx',
   		requires: ['yahoo', 'dom', 'event', 'inputex-css']
   	},
		{
			name: 'inputex-field',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/Field.js',
	  	   varName: 'inputEx.Field',
			requires: ['inputex']
		},
      {
			name: 'inputex-visus',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/Visus.js',
	  	   varName: 'inputEx.visus',
			requires: ['inputex']
		},
		{
 			name: 'inputex-jsonschema',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/json-schema.js',
 	  	   varName: 'inputEx.JsonSchema',
 			requires: ['inputex']
 		},
 		// RPC
 		{
 			name: 'inputex-rpc',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/rpc/inputex-rpc.js',
 	  	   varName: 'inputEx.RPC',
 			requires: ['yahoo','connection','inputex-jsonschema']
 		},
		{
 			name: 'inputex-smdtester',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/rpc/smdTester.js',
 	  	   varName: 'inputEx.RPC.SMDTester',
 			requires: ['inputex-rpc', 'inputex-jsontreeinspector']
 		},
		{
 			name: 'inputex-yql',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/rpc/yql.js',
 	  	   varName: 'inputEx.YQL',
 			requires: ['inputex']
 		},
		// Mixins
		{
			name: 'inputex-choice',
			type: 'js',
			fullpath: pathToInputEx+'js/mixins/choice.js',
			varName: 'inputEx.mixin.choice',
			requires: ['inputex']
		},
		// Widgets
		{
 			name: 'inputex-ddlist',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/widgets/ddlist.js',
 	  	   varName: 'inputEx.widget.DDList',
 			requires: ['inputex', 'dragdrop']
 		},
 		{
 			name: 'inputex-dialog',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/widgets/Dialog.js',
 	  	   varName: 'inputEx.widget.Dialog',
 			requires: ['inputex', 'inputex-group', 'dragdrop', 'container']
 		},
 		{
 			name: 'inputex-datatable',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/widgets/DataTable.js',
 	  	   varName: 'inputEx.widget.DataTable',
 			requires: ['datatable', 'inputex', 'inputex-dialog']
 		},
		{
 			name: 'inputex-inplace-datatable',
 			type: 'js',
 	  	   fullpath: pathToInputEx+'js/widgets/dtInPlaceEdit.js',
 	  	   varName: 'inputEx.widget.dtInPlaceEdit',
 			requires: ['inputex-datatable']
 		},
      {
         name: 'inputex-jsontreeinspector',
         type: 'js',
         fullpath: pathToInputEx+'js/widgets/json-tree-inspector.js',
         varName: 'inputEx.widget.JsonTreeInspector',
         requires: ['inputex']
      },
      {
         name: 'inputex-button',
         type: 'js',
         fullpath: pathToInputEx+'js/widgets/Button.js',
         varName: 'inputEx.widget.Button',
         requires: ['inputex']
      },
		// MetaFields
		{
			name: 'inputex-group',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/Group.js',
	  	   varName: 'inputEx.Group',
			requires: ['inputex-field']
		},
		{
			name: 'inputex-form',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/Form.js',
	  	   varName: 'inputEx.Form',
			requires: ['inputex-group','inputex-button']
		},
		{
			name: 'inputex-listfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/ListField.js',
	  	   varName: 'inputEx.ListField',
			requires: ['inputex-field']
		},
		{
			name: 'inputex-treefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/TreeField.js',
	  	   varName: 'inputEx.TreeField',
			requires: ['inputex-listfield']
		},
		{
			name: 'inputex-combinefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/CombineField.js',
	  	   varName: 'inputEx.CombineField',
			requires: ['inputex-group']
		},
		{
			name: 'inputex-inplaceedit',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/InPlaceEdit.js',
	  	   varName: 'inputEx.InPlaceEdit',
			requires: ['inputex-field', 'inputex-button', 'animation'] // animation is optional, required if animColors option
		},
		{
			name: 'inputex-lens',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/Lens-beta.js',
	  	   varName: 'inputEx.Lens',
			requires: ['inputex-group']
		},
		// Fields
		{
			name: 'inputex-stringfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/StringField.js',
	  	   varName: 'inputEx.StringField',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-autocomplete',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/AutoComplete.js',
	  	   varName: 'inputEx.AutoComplete',
			requires: ['inputex-stringfield', 'autocomplete']
		},
		{
		   name: 'inputex-checkbox',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/CheckBox.js',
	  	   varName: 'inputEx.CheckBox',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-colorfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/ColorField.js',
	  	   varName: 'inputEx.ColorField',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-colorpickerfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/ColorPickerField.js',
	  	   varName: 'inputEx.ColorPickerField',
			requires: ['inputex-field','colorpicker']
		},
		{
		   name: 'inputex-datefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DateField.js',
	  	   varName: 'inputEx.DateField',
			requires: ['inputex-stringfield']
		},
		{
		   name: 'inputex-datepickerfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DatePickerField.js',
	  	   varName: 'inputEx.DatePickerField',
			requires: ['calendar', 'button', 'inputex-datefield']
		},
		{
		   name: 'inputex-dateselectmonthfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DateSelectMonthField.js',
	  	   varName: 'inputEx.DateSelectMonthField',
			requires: ['inputex-combinefield']
		},
		{
		   name: 'inputex-integerfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/IntegerField.js',
	  	   varName: 'inputEx.IntegerField',
			requires: ['inputex-stringfield']
		},
		{
		   name: 'inputex-datesplitfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DateSplitField.js',
	  	   varName: 'inputEx.DateSplitField',
			requires: ['inputex-combinefield', 'inputex-integerfield']
		},
		{
			name: 'inputex-selectfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/SelectField.js',
	  	   varName: 'inputEx.SelectField',
			requires: ['inputex-field','inputex-choice']
		},
		{
		   name: 'inputex-timefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/TimeField.js',
	  	   varName: 'inputEx.TimeField',
			requires: ['inputex-combinefield', 'inputex-selectfield']
		},
		{
		   name: 'inputex-datetimefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DateTimeField.js',
	  	   varName: 'inputEx.DateTimeField',
			requires: ['inputex-datepickerfield', 'inputex-combinefield', 'inputex-timefield']
		},
		{
		   name: 'inputex-timeintervalfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/TimeIntervalField.js',
	  	   varName: 'inputEx.TimeIntervalField',
			requires: ['inputex-combinefield', 'inputex-selectfield']
		},
		{
		   name: 'inputex-dsselectfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/DSSelectField.js',
	  	   varName: 'inputEx.DSSelectField',
			requires: ['inputex-selectfield', 'datasource']
		},
		{
			name: 'inputex-emailfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/EmailField.js',
	  	   varName: 'inputEx.EmailField',
			requires: ['inputex-stringfield']
		},
		{
		   name: 'inputex-hiddenfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/HiddenField.js',
	  	   varName: 'inputEx.HiddenField',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-keyvaluefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/KeyValueField-beta.js',
	  	   varName: 'inputEx.KeyValueField',
			requires: ['inputex-combinefield']
		},
		{
		   name: 'inputex-keyopvaluefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/KeyOpValueField-beta.js',
	  	   varName: 'inputEx.KeyOpValueField',
			requires: ['inputex-keyvaluefield']
		},
      {
		   name: 'inputex-multiautocomplete',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/MultiAutoComplete.js',
	  	   varName: 'inputEx.MultiAutoComplete',
			requires: ['inputex-autocomplete', 'inputex-ddlist']
      },
      {
		   name: 'inputex-multiselectfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/MultiSelectField.js',
	  	   varName: 'inputEx.MultiSelectField',
			requires: ['inputex-selectfield', 'inputex-ddlist']
      },
      {
		   name: 'inputex-numberfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/NumberField.js',
	  	   varName: 'inputEx.NumberField',
			requires: ['inputex-stringfield']
		},
 		{
		   name: 'inputex-passwordfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/PasswordField.js',
	  	   varName: 'inputEx.PasswordField',
			requires: ['inputex-stringfield']
		},
 		{
		   name: 'inputex-radiofield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/RadioField.js',
	  	   varName: 'inputEx.RadioField',
			requires: ['selector','event-delegate','inputex-field','inputex-choice','inputex-stringfield']
		},
		{
		   name: 'inputex-rtefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/RTEField.js',
	  	   varName: 'inputEx.RTEField',
			requires: ['inputex-field', 'editor']
		},
		{
		   name: 'inputex-sliderfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/SliderField.js',
	  	   varName: 'inputEx.SliderField',
			requires: ['inputex-field', 'slider']
		},
		{
		   name: 'inputex-textarea',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/Textarea.js',
	  	   varName: 'inputEx.Textarea',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-typefield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/TypeField.js',
	  	   varName: 'inputEx.TypeField',
			requires: ['inputex-field']
		},
		{
		   name: 'inputex-uneditable',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/UneditableField.js',
	  	   varName: 'inputEx.UneditableField',
			requires: ['inputex-field', 'inputex-visus']
		},
		{
			name: 'inputex-urlfield',
			type: 'js',
	  	   fullpath: pathToInputEx+'js/fields/UrlField.js',
	  	   varName: 'inputEx.UrlField',
			requires: ['inputex-stringfield']
		},
 		{
  			name: 'inputex-dateselectmonthfield',
  			type: 'js',
  	  	   fullpath: pathToInputEx+'js/fields/DateSelectMonthField.js',
  	  	   varName: 'inputEx.DateSelectMonthField',
  			requires: ['inputex-combinefield', 'inputex-stringfield', 'inputex-selectfield']
  		},
  		{
  			name: 'inputex-ipv4field',
  			type: 'js',
  	  	   fullpath: pathToInputEx+'js/fields/IPv4Field.js',
  	  	   varName: 'inputEx.IPv4Field',
  			requires: ['inputex-stringfield']
  		},
  		{
  			name: 'inputex-vectorfield',
  			type: 'js',
  	  	   fullpath: pathToInputEx+'js/fields/VectorField.js',
  	  	   varName: 'inputEx.VectorField',
  			requires: ['inputex-combinefield']
  		},
  		{
  			name: 'inputex-mapfield',
  			type: 'js',
  	  	   fullpath: pathToInputEx+'js/fields/MapField.js',
  	  	   varName: 'inputEx.MapField',
  			requires: ['inputex-field']
  		},
  		// Locals
  		{
  		   name: 'inputex-lang-fr',
  			type: 'js',
  	  	   fullpath: pathToInputEx+'js/locals/fr.js',
  	  	   varName: 'inputEx.lang_fr',
  			requires: ['inputex']
  		},
  		{
        	name: 'inputex-lang-it',
        	type: 'js',
        	fullpath: pathToInputEx+'js/locals/it.js',
        	varName: 'inputEx.lang_it',
         requires: ['inputex']
      },
		{
		   name: 'inputex-lang-nl',
		   type: 'js',
		   fullpath: pathToInputEx+'js/locals/nl.js',
		   varName: 'inputEx.lang_nl',
		   requires: ['inputex']
		},
		{
		   name: 'inputex-lang-es',
		   type: 'js',
		   fullpath: pathToInputEx+'js/locals/es.js',
		   varName: 'inputEx.lang_es',
		   requires: ['inputex']
		},
		{
		   name: 'inputex-lang-de',
		   type: 'js',
		   fullpath: pathToInputEx+'js/locals/de.js',
		   varName: 'inputEx.lang_de',
		   requires: ['inputex']
		}
	];
	for(var i = 0 ; i < modules.length ; i++) {
		yuiLoader.addModule(modules[i]);
	}
};

})();