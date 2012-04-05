YAHOO.env.classMap = {"inputEx.CheckBox": "inputEx", "inputEx.YQL": "inputEx", "inputEx.KeyOpValueField": "inputEx", "inputEx.RPC.Envelope.PATH": "inputEx", "inputEx.widget.CellEditor": "inputEx", "inputEx.widget.DDList": "inputEx", "inputEx.MapField": "inputEx", "inputEx.VectorField": "inputEx", "inputEx.widget.dtInPlaceEdit": "inputEx", "inputEx.MultiAutoCompleteCustom": "inputEx", "inputEx.RPC.Service": "inputEx", "inputEx.KeyValueField": "inputEx", "inputEx.RadioField": "inputEx", "inputEx.MenuField": "inputEx", "inputEx.FileField": "inputEx", "inputEx.RPC.Envelope.JSON-RPC-1.0": "inputEx", "inputEx.DatePickerField": "inputEx", "inputEx.RPC.Transport": "inputEx", "inputEx.ColorPickerField": "inputEx", "inputEx.TimeField": "inputEx", "inputEx.TypeField": "inputEx", "inputEx.MultiAutoComplete": "inputEx", "inputEx.MultiSelectFieldCustom": "inputEx", "inputEx.UneditableField": "inputEx", "inputEx.ColorField": "inputEx", "inputEx.IPv4Field": "inputEx", "inputEx.widget.DataTable": "inputEx", "inputEx.JsonSchema.Builder": "inputEx", "inputEx.Lens": "inputEx", "inputEx.visus": "inputEx", "inputEx.RPC.Envelope": "inputEx", "inputEx.RPC.Envelope.JSON": "inputEx", "inputEx.JsonSchema": "inputEx", "inputEx.Field": "inputEx", "inputEx.EmailField": "inputEx", "inputEx.RTEField": "inputEx", "inputEx.widget.DDListItem": "inputEx", "inputEx.InPlaceEdit": "inputEx", "inputEx.ListField": "inputEx", "inputEx.IntegerField": "inputEx", "inputEx.TreeField": "inputEx", "inputEx.CombineField": "inputEx", "inputEx.RPC.Envelope.JSON-RPC-2.0": "inputEx", "inputEx.PasswordField": "inputEx", "inputEx.TimeIntervalField": "inputEx", "inputEx.StringAvailability": "inputEx", "inputEx.widget.JsonTreeInspector": "inputEx", "inputEx.SliderField": "inputEx", "inputEx.RPC.Envelope.URL": "inputEx", "inputEx.UrlField": "inputEx", "inputEx.SerializeField": "inputEx", "inputEx.DateTimeField": "inputEx", "inputEx.MultiSelectField": "inputEx", "inputEx.RadioButton": "inputEx", "inputEx.SelectField": "inputEx", "inputEx.NumberField": "inputEx", "inputEx.Group": "inputEx", "inputEx.AutoComplete": "inputEx", "inputEx.DateSplitField": "inputEx", "inputEx.RPC.SMDTester": "inputEx", "inputEx.DateField": "inputEx", "inputEx.Form": "inputEx", "inputEx.HiddenField": "inputEx", "inputEx.StringField": "inputEx", "inputEx": "inputEx", "inputEx.SerializeField.serializers": "inputEx", "inputEx.RPC": "inputEx", "inputEx.DSSelectField": "inputEx", "inputEx.Textarea": "inputEx", "inputEx.DateSelectMonthField": "inputEx", "inputEx.UpperCaseField": "inputEx", "inputEx.widget.Dialog": "inputEx", "inputEx.widget.Button": "inputEx", "inputEx.TinyMCEField": "inputEx"};

YAHOO.env.resolveClass = function(className) {
    var a=className.split('.'), ns=YAHOO.env.classMap;

    for (var i=0; i<a.length; i=i+1) {
        if (ns[a[i]]) {
            ns = ns[a[i]];
        } else {
            return null;
        }
    }

    return ns;
};
