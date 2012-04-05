(function() {
    var lang = YAHOO.lang, Event = YAHOO.util.Event, Dom = YAHOO.util.Dom;

/**
 * Create a YUI Radio button. Here are the added options :
 * <ul>
 *    <li>choices: list of choices (array of string)</li>
 *    <li>values: list of returned values (array )</li>
 *    <li>allowAny: add an option with a string field</li>
 * </ul>
 * @class inputEx.RadioButton
 * @extends inputEx.RadioField
 * @constructor
 * @param {Object} options inputEx.Field options object
 */
inputEx.RadioButton = function(options) {
  inputEx.RadioButton.superclass.constructor.call(this, options);
};

lang.extend(inputEx.RadioButton, inputEx.RadioField);

// Register this class as "radio" type
inputEx.registerType("radiobutton", inputEx.RadioButton);

})();

/*
var oButtonGroup3 = new YAHOO.widget.ButtonGroup({ 
                                id:  "buttongroup3", 
                                name:  "radiofield3", 
                                container:  "radiobuttonsfromjavascript" });

oButtonGroup3.addButtons([

    { label: "Radio 9", value: "Radio 9", checked: true },
    { label: "Radio 10", value: "Radio 10" }, 
    { label: "Radio 11", value: "Radio 11" }, 
    { label: "Radio 12", value: "Radio 12" }

]);
*/