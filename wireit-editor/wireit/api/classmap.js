YAHOO.env.classMap = {"WireIt.Container": "WireIt", "inputEx.WireIt.Layout.Spring": "layout-plugin", "WireIt.ArrowWire": "WireIt", "WireIt.BezierArrowWire": "WireIt", "WireIt.WiringEditor": "editor-plugin", "WireIt.Layer": "WireIt", "WireIt.Group": "editor-plugin", "WireIt.Grouper": "editor-plugin", "WireIt.LeftSquareArrow": "WireIt", "WireIt.Wire": "WireIt", "WireIt.util.Anim": "animations-plugin", "WireIt.RightSquareArrow": "WireIt", "WireIt.TextareaContainer": "inputex-plugin", "WireIt.TerminalProxy": "WireIt", "WireIt.WiringEditor.adapters.JsonRpc": "editor-plugin", "WireIt.CanvasElement": "WireIt", "WireIt.Scissors": "WireIt", "WireIt.BaseEditor": "editor-plugin", "WireIt.WiringEditor.adapters.Ajax": "editor-plugin", "WireIt.util.ComposedContainer": "composable-plugin", "WireIt.util.DDResize": "WireIt", "WireIt.util.TerminalOutput": "WireIt", "WireIt.util.DD": "WireIt", "WireIt.BezierWire": "WireIt", "WireIt.WireIt": "WireIt", "WireIt.util.InOutContainer": "WireIt", "WireIt.RubberBand": "editor-plugin", "WireIt.Terminal": "WireIt", "WireIt.util.ImageContainer": "WireIt", "WireIt.WiringEditor.adapters.Gears": "editor-plugin", "WireIt.util.ComposableWiringEditor": "composable-plugin", "inputEx.Field": "inputex-plugin", "inputEx.BaseField": "inputex-plugin", "WireIt.StepWire": "WireIt", "WireIt.GroupUtils": "editor-plugin", "WireIt.ModuleProxy": "editor-plugin", "WireIt.FormContainer": "inputex-plugin", "WireIt.CanvasContainer": "WireIt", "WireIt.util.EllipseLabelContainer": "WireIt", "WireIt.LayerMap": "WireIt", "inputEx.LayerContainer": "inputex-plugin", "WireIt.util.TerminalInput": "WireIt", "WireIt.RectLabelContainer": "WireIt"};

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
