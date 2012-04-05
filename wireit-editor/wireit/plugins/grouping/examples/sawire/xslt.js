// Copyright 2005 Google Inc.
// All Rights Reserved
//
//
// An XSL-T processor written in JavaScript. The implementation is NOT
// complete; some xsl element are left out.
//
// References:
//
// [XSLT] XSL-T Specification
// <http://www.w3.org/TR/1999/REC-xslt-19991116>.
//
// [ECMA] ECMAScript Language Specification
// <http://www.ecma-international.org/publications/standards/Ecma-262.htm>.
//
// The XSL processor API has one entry point, the function
// xsltProcessContext(). It receives as arguments the starting point in the
// input document as an XPath expression context, the DOM root node of
// the XSL-T stylesheet, and a DOM node that receives the output.
//
// NOTE: Actually, XSL-T processing according to the specification is
// defined as operation on text documents, not as operation on DOM
// trees. So, strictly speaking, this implementation is not an XSL-T
// processor, but the processing engine that needs to be complemented
// by an XML parser and serializer in order to be complete. Those two
// are found in the file xml.js.
//
//
// TODO(mesch): add jsdoc comments. Use more coherent naming. Finish
// remaining XSLT features.
//
//
// Author: Steffen Meschkat <mesch@google.com>


// The exported entry point of the XSL-T processor, as explained
// above.
//
// @param xmlDoc The input document root, as DOM node.
// @param template The stylesheet document root, as DOM node.
// @return the processed document, as XML text in a string.

function xsltProcess(xmlDoc, stylesheet) {
  var output = domCreateDocumentFragment(new XDocument);
  xsltProcessContext(new ExprContext(xmlDoc), stylesheet, output);
  var ret = xmlText(output);
  return ret;
}

// The main entry point of the XSL-T processor, as explained above.
//
// @param input The input document root, as XPath ExprContext.
// @param template The stylesheet document root, as DOM node.
// @param the root of the generated output, as DOM node.

function xsltProcessContext(input, template, output) {
  var outputDocument = xmlOwnerDocument(output);

  var nodename = template.nodeName.split(/:/);
  if (nodename.length == 1 || nodename[0] != 'xsl') {
    xsltPassThrough(input, template, output, outputDocument);

  } else {
    switch(nodename[1]) {
    case 'apply-imports':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'apply-templates':
      var select = xmlGetAttribute(template, 'select');
      var nodes;
      if (select) {
        nodes = xpathEval(select,input).nodeSetValue();
      } else {
        nodes = input.node.childNodes;
      }

      var sortContext = input.clone(nodes[0], 0, nodes);
      xsltWithParam(sortContext, template);
      xsltSort(sortContext, template);

      var mode = xmlGetAttribute(template, 'mode');
      var top = template.ownerDocument.documentElement;
      var templates = [];
      for (var i = 0; i < top.childNodes.length; ++i) {
        var c = top.childNodes[i];
        if (c.nodeType == DOM_ELEMENT_NODE &&
            c.nodeName == 'xsl:template' &&
            c.getAttribute('mode') == mode) {
          templates.push(c);
        }
      }
      for (var j = 0; j < sortContext.contextSize(); ++j) {
        var nj = sortContext.nodelist[j];
        for (var i = 0; i < templates.length; ++i) {
          xsltProcessContext(sortContext.clone(nj, j), templates[i], output);
        }
      }
      break;

    case 'attribute':
      var nameexpr = xmlGetAttribute(template, 'name');
      var name = xsltAttributeValue(nameexpr, input);
      var node = domCreateDocumentFragment(outputDocument);
      xsltChildNodes(input, template, node);
      var value = xmlValue(node);
      domSetAttribute(output, name, value);
      break;

    case 'attribute-set':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'call-template':
      var name = xmlGetAttribute(template, 'name');
      var top = template.ownerDocument.documentElement;

      var paramContext = input.clone();
      xsltWithParam(paramContext, template);

      for (var i = 0; i < top.childNodes.length; ++i) {
        var c = top.childNodes[i];
        if (c.nodeType == DOM_ELEMENT_NODE &&
            c.nodeName == 'xsl:template' &&
            domGetAttribute(c, 'name') == name) {
          xsltChildNodes(paramContext, c, output);
          break;
        }
      }
      break;

    case 'choose':
      xsltChoose(input, template, output);
      break;

    case 'comment':
      var node = domCreateDocumentFragment(outputDocument);
      xsltChildNodes(input, template, node);
      var commentData = xmlValue(node);
      var commentNode = domCreateComment(outputDocument, commentData);
      output.appendChild(commentNode);
      break;

    case 'copy':
      var node = xsltCopy(output, input.node, outputDocument);
      if (node) {
        xsltChildNodes(input, template, node);
      }
      break;

    case 'copy-of':
      var select = xmlGetAttribute(template, 'select');
      var value = xpathEval(select, input);
      if (value.type == 'node-set') {
        var nodes = value.nodeSetValue();
        for (var i = 0; i < nodes.length; ++i) {
          xsltCopyOf(output, nodes[i], outputDocument);
        }

      } else {
        var node = domCreateTextNode(outputDocument, value.stringValue());
        domAppendChild(output, node);
      }
      break;

    case 'decimal-format':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'element':
      var nameexpr = xmlGetAttribute(template, 'name');
      var name = xsltAttributeValue(nameexpr, input);
      var node = domCreateElement(outputDocument, name);
      domAppendChild(output, node);
      xsltChildNodes(input, template, node);
      break;

    case 'fallback':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'for-each':
      xsltForEach(input, template, output);
      break;

    case 'if':
      var test = xmlGetAttribute(template, 'test');
      if (xpathEval(test, input).booleanValue()) {
        xsltChildNodes(input, template, output);
      }
      break;

    case 'import':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'include':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'key':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'message':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'namespace-alias':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'number':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'otherwise':
      alert('error if here: ' + nodename[1]);
      break;

    case 'output':
      // Ignored. -- Since we operate on the DOM, and all further use
      // of the output of the XSL transformation is determined by the
      // browser that we run in, this parameter is not applicable to
      // this implementation.
      break;

    case 'preserve-space':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'processing-instruction':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'sort':
      // just ignore -- was handled by xsltSort()
      break;

    case 'strip-space':
      alert('not implemented: ' + nodename[1]);
      break;

    case 'stylesheet':
    case 'transform':
      xsltChildNodes(input, template, output);
      break;

    case 'template':
      var match = xmlGetAttribute(template, 'match');
      if (match && xsltMatch(match, input)) {
        xsltChildNodes(input, template, output);
      }
      break;

    case 'text':
      var text = xmlValue(template);
      var node = domCreateTextNode(outputDocument, text);
      output.appendChild(node);
      break;

    case 'value-of':
      var select = xmlGetAttribute(template, 'select');
      var value = xpathEval(select, input).stringValue();
      var node = domCreateTextNode(outputDocument, value);
      output.appendChild(node);
      break;

    case 'param':
      xsltVariable(input, template, false);
      break;

    case 'variable':
      xsltVariable(input, template, true);
      break;

    case 'when':
      alert('error if here: ' + nodename[1]);
      break;

    case 'with-param':
      alert('error if here: ' + nodename[1]);
      break;

    default:
      alert('error if here: ' + nodename[1]);
      break;
    }
  }
}


// Sets parameters defined by xsl:with-param child nodes of the
// current template node, in the current input context. This happens
// before the operation specified by the current template node is
// executed.

function xsltWithParam(input, template) {
  for (var i = 0; i < template.childNodes.length; ++i) {
    var c = template.childNodes[i];
    if (c.nodeType == DOM_ELEMENT_NODE && c.nodeName == 'xsl:with-param') {
      xsltVariable(input, c, true);
    }
  }
}


// Orders the current node list in the input context according to the
// sort order specified by xsl:sort child nodes of the current
// template node. This happens before the operation specified by the
// current template node is executed.
//
// TODO(mesch): case-order is not implemented.

function xsltSort(input, template) {
  var sort = [];
  for (var i = 0; i < template.childNodes.length; ++i) {
    var c = template.childNodes[i];
    if (c.nodeType == DOM_ELEMENT_NODE && c.nodeName == 'xsl:sort') {
      var select = xmlGetAttribute(c, 'select');
      var expr = xpathParse(select);
      var type = xmlGetAttribute(c, 'data-type') || 'text';
      var order = xmlGetAttribute(c, 'order') || 'ascending';
      sort.push({ expr: expr, type: type, order: order });
    }
  }

  xpathSort(input, sort);
}


// Evaluates a variable or parameter and set it in the current input
// context. Implements xsl:variable, xsl:param, and xsl:with-param.
//
// @param override flag that defines if the value computed here
// overrides the one already in the input context if that is the
// case. I.e. decides if this is a default value or a local
// value. xsl:variable and xsl:with-param override; xsl:param doesn't.

function xsltVariable(input, template, override) {
  var name = xmlGetAttribute(template, 'name');
  var select = xmlGetAttribute(template, 'select');

  var value;

  if (template.childNodes.length > 0) {
    var root = domCreateDocumentFragment(template.ownerDocument);
    xsltChildNodes(input, template, root);
    value = new NodeSetValue([root]);

  } else if (select) {
    value = xpathEval(select, input);

  } else {
    value = new StringValue('');
  }

  if (override || !input.getVariable(name)) {
    input.setVariable(name, value);
  }
}


// Implements xsl:chose and its child nodes xsl:when and
// xsl:otherwise.

function xsltChoose(input, template, output) {
  for (var i = 0; i < template.childNodes.length; ++i) {
    var childNode = template.childNodes[i];
    if (childNode.nodeType != DOM_ELEMENT_NODE) {
      continue;

    } else if (childNode.nodeName == 'xsl:when') {
      var test = xmlGetAttribute(childNode, 'test');
      if (xpathEval(test, input).booleanValue()) {
        xsltChildNodes(input, childNode, output);
        break;
      }

    } else if (childNode.nodeName == 'xsl:otherwise') {
      xsltChildNodes(input, childNode, output);
      break;
    }
  }
}


// Implements xsl:for-each.

function xsltForEach(input, template, output) {
  var select = xmlGetAttribute(template, 'select');
  var nodes = xpathEval(select, input).nodeSetValue();
  var sortContext = input.clone(nodes[0], 0, nodes);
  xsltSort(sortContext, template);
  for (var i = 0; i < sortContext.contextSize(); ++i) {
    var ni = sortContext.nodelist[i];
    xsltChildNodes(sortContext.clone(ni, i), template, output);
  }
}


// Traverses the template node tree. Calls the main processing
// function with the current input context for every child node of the
// current template node.

function xsltChildNodes(input, template, output) {
  // Clone input context to keep variables declared here local to the
  // siblings of the children.
  var context = input.clone();
  for (var i = 0; i < template.childNodes.length; ++i) {
    xsltProcessContext(context, template.childNodes[i], output);
  }
}


// Passes template text to the output. The current template node does
// not specify an XSL-T operation and therefore is appended to the
// output with all its attributes. Then continues traversing the
// template node tree.

function xsltPassThrough(input, template, output, outputDocument) {
  if (template.nodeType == DOM_TEXT_NODE) {
    if (xsltPassText(template)) {
      var node = domCreateTextNode(outputDocument, template.nodeValue);
      domAppendChild(output, node);
    }

  } else if (template.nodeType == DOM_ELEMENT_NODE) {
    var node = domCreateElement(outputDocument, template.nodeName);
    for (var i = 0; i < template.attributes.length; ++i) {
      var a = template.attributes[i];
      if (a) {
        var name = a.nodeName;
        var value = xsltAttributeValue(a.nodeValue, input);
        domSetAttribute(node, name, value);
      }
    }
    domAppendChild(output, node);
    xsltChildNodes(input, template, node);

  } else {
    // This applies also to the DOCUMENT_NODE of the XSL stylesheet,
    // so we don't have to treat it specially.
    xsltChildNodes(input, template, output);
  }
}

// Determines if a text node in the XSLT template document is to be
// stripped according to XSLT whitespace stipping rules.
//
// See [XSLT], section 3.4.
//
// TODO(mesch): Whitespace stripping on the input document is
// currently not implemented.

function xsltPassText(template) {
  if (!template.nodeValue.match(/^\s*$/)) {
    return true;
  }

  var element = template.parentNode;
  if (element.nodeName == 'xsl:text') {
    return true;
  }

  while (element && element.nodeType == DOM_ELEMENT_NODE) {
    var xmlspace = domGetAttribute(element, 'xml:space');
    if (xmlspace) {
      if (xmlspace == 'default') {
        return false;
      } else if (xmlspace == 'preserve') {
        return true;
      }
    }

    element = element.parentNode;
  }

  return false;
}

// Evaluates an XSL-T attribute value template. Attribute value
// templates are attributes on XSL-T elements that contain XPath
// expressions in braces {}. The XSL-T expressions are evaluated in
// the current input context. NOTE(mesch): We are using stringSplit()
// instead of string.split() for IE compatibility, see comment on
// stringSplit().

function xsltAttributeValue(value, context) {
  var parts = stringSplit(value, '{');
  if (parts.length == 1) {
    return value;
  }

  var ret = '';
  for (var i = 0; i < parts.length; ++i) {
    var rp = stringSplit(parts[i], '}');
    if (rp.length != 2) {
      // first literal part of the value
      ret += parts[i];
      continue;
    }

    var val = xpathEval(rp[0], context).stringValue();
    ret += val + rp[1];
  }

  return ret;
}


// Wrapper function to access attribute values of template element
// nodes. Currently this calls xmlResolveEntities because in some DOM
// implementations the return value of node.getAttributeValue()
// contains unresolved XML entities, although the DOM spec requires
// that entity references are resolved by te DOM.
function xmlGetAttribute(node, name) {
  // TODO(mesch): This should not be necessary if the DOM is working
  // correctly. The DOM is responsible for resolving entities, not the
  // application.
  var value = domGetAttribute(node, name);
  if (value) {
    return xmlResolveEntities(value);
  } else {
    return value;
  }
};


// Implements xsl:copy-of for node-set values of the select
// expression. Recurses down the source node tree, which is part of
// the input document.
//
// @param {Node} dst the node being copied to, part of output document,
// @param {Node} src the node being copied, part in input document,
// @param {Document} dstDocument

function xsltCopyOf(dst, src, dstDocument) {
  if (src.nodeType == DOM_DOCUMENT_FRAGMENT_NODE ||
      src.nodeType == DOM_DOCUMENT_NODE) {
    for (var i = 0; i < src.childNodes.length; ++i) {
      arguments.callee(dst, src.childNodes[i], dstDocument);
    }
  } else {
    var node = xsltCopy(dst, src, dstDocument);
    if (node) {
      // This was an element node -- recurse to attributes and
      // children.
      for (var i = 0; i < src.attributes.length; ++i) {
        arguments.callee(node, src.attributes[i], dstDocument);
      }

      for (var i = 0; i < src.childNodes.length; ++i) {
        arguments.callee(node, src.childNodes[i], dstDocument);
      }
    }
  }
}


// Implements xsl:copy for all node types.
//
// @param {Node} dst the node being copied to, part of output document,
// @param {Node} src the node being copied, part in input document,
// @param {Document} dstDocument
// @return {Node|Null} If an element node was created, the element
// node. Otherwise null.

function xsltCopy(dst, src, dstDocument) {
  if (src.nodeType == DOM_ELEMENT_NODE) {
    var node = domCreateElement(dstDocument, src.nodeName);
    domAppendChild(dst, node);
    return node;
  }

  if (src.nodeType == DOM_TEXT_NODE) {
    var node = domCreateTextNode(dstDocument, src.nodeValue);
    domAppendChild(dst, node);

  } else if (src.nodeType == DOM_CDATA_SECTION_NODE) {
    var node = domCreateCDATASection(dstDocument, src.nodeValue);
    domAppendChild(dst, node);

  } else if (src.nodeType == DOM_COMMENT_NODE) {
    var node = domCreateComment(dstDocument, src.nodeValue);
    domAppendChild(dst, node);

  } else if (src.nodeType == DOM_ATTRIBUTE_NODE) {
    domSetAttribute(dst, src.nodeName, src.nodeValue);
  }

  return null;
}


// Evaluates an XPath expression in the current input context as a
// match (see [XSLT] section 5.2, paragraph 1).
function xsltMatch(match, context) {
  var expr = xpathParse(match);

  var ret;
  // Shortcut for the most common case.
  if (expr.steps && !expr.absolute && expr.steps.length == 1 &&
      expr.steps[0].axis == 'child' && expr.steps[0].predicate.length == 0) {
    ret = expr.steps[0].nodetest.evaluate(context).booleanValue();

  } else {

    ret = false;
    var node = context.node;

    while (!ret && node) {
      var result = expr.evaluate(context.clone(node,0,[node])).nodeSetValue();
      for (var i = 0; i < result.length; ++i) {
        if (result[i] == context.node) {
          ret = true;
          break;
        }
      }
      node = node.parentNode;
    }
  }

  return ret;
}
