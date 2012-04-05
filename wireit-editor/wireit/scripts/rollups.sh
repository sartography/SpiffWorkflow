#!/bin/sh
# Build WireIt rollup files
# Compressed using the YUI compressor

YUIcompressorJar=~/Tools/yuicompressor-2.3.6/build/yuicompressor-2.3.6.jar

cd ../build

# Core wireit rollup
rm -f wireit.js wireit-min.js
cat ../js/WireIt.js ../js/CanvasElement.js ../js/Wire.js ../js/StepWire.js ../js/ArrowWire.js ../js/BezierWire.js ../js/BezierArrowWire.js ../js/TerminalProxy.js ../js/Scissors.js ../js/Terminal.js ../js/TerminalInput.js ../js/TerminalOutput.js ../js/DD.js ../js/DDResize.js ../js/Container.js ../js/Layer.js ../js/LayerMap.js ../js/ImageContainer.js ../js/InOutContainer.js > wireit.js
java -jar $YUIcompressorJar  wireit.js -o wireit-min.js --charset utf8


# wireit-inputex rollup
rm -f wireit-inputex.js wireit-inputex-min.js
cat wireit.js ../plugins/inputex/lib/inputex/js/inputex.js ../plugins/inputex/lib/inputex/js/Field.js ../plugins/inputex/js/WirableField.js ../plugins/inputex/js/FormContainer.js ../plugins/inputex/lib/inputex/js/Group.js ../plugins/inputex/lib/inputex/js/Visus.js ../plugins/inputex/lib/inputex/js/widgets/Button.js ../plugins/inputex/lib/inputex/js/fields/StringField.js ../plugins/inputex/lib/inputex/js/mixins/choice.js ../plugins/inputex/lib/inputex/js/fields/SelectField.js ../plugins/inputex/lib/inputex/js/fields/EmailField.js ../plugins/inputex/lib/inputex/js/fields/UrlField.js ../plugins/inputex/lib/inputex/js/fields/ListField.js ../plugins/inputex/lib/inputex/js/fields/CheckBox.js ../plugins/inputex/lib/inputex/js/fields/Textarea.js ../plugins/inputex/lib/inputex/js/fields/InPlaceEdit.js ../plugins/inputex/lib/inputex/js/fields/TypeField.js > wireit-inputex.js
java -jar $YUIcompressorJar  wireit-inputex.js -o wireit-inputex-min.js --charset utf8


# wireit-inputex-editor rollup
rm -f wireit-inputex-editor.js wireit-inputex-editor-min.js
cat wireit-inputex.js ../plugins/editor/js/BaseEditor.js ../plugins/editor/js/ModuleProxy.js ../plugins/editor/js/WiringEditor.js > wireit-inputex-editor.js
java -jar $YUIcompressorJar  wireit-inputex-editor.js -o wireit-inputex-editor-min.js --charset utf8


# wireit-inputex-editor-composable
rm -f wireit-inputex-editor-composable.js wireit-inputex-editor-composable-min.js
cat wireit-inputex-editor.js ../plugins/composable/js/ComposedContainer.js ../plugins/composable/js/ComposableWiringEditor.js > wireit-inputex-editor-composable.js
java -jar $YUIcompressorJar  wireit-inputex-editor-composable.js -o wireit-inputex-editor-composable-min.js --charset utf8


# wireit-inputex-editor-grouping
rm -f wireit-inputex-editor-grouping.js wireit-inputex-editor-grouping-min.js
cat wireit-inputex-editor.js ../plugins/grouping/js/Container.js ../plugins/grouping/js/Group.js ../plugins/grouping/js/Grouper.js ../plugins/grouping/js/GroupFormContainer.js ../plugins/grouping/js/GroupUtils.js ../plugins/grouping/js/RubberBand.js > wireit-inputex-editor-grouping.js
java -jar $YUIcompressorJar  wireit-inputex-editor-grouping.js -o wireit-inputex-editor-grouping-min.js --charset utf8
