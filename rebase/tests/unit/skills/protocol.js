const babylon = require('babylon');
const traverse = require('babel-traverse');
const types = require('babel-types');

const TechProfile = require('./tech_profile.js').TechProfile;

const {
    JS_LANGUAGE,
    THIRD_PARTY,
    GRAMMAR,
    BABYLON_OPTIONS,
    STANDARD_LIBRARY
} = require('./constants.js');


function parse(code) {
    return babylon.parse(code, BABYLON_OPTIONS);
}


function add(profile, tech, count) {
    if (profile.hasKey(tech)) {
        profile.set(tech, count + profile.get(tech));
    } else {
        profile.set(tech, count);
    }
}


function scan_contents(language_index, filename, code, context) {
    /*
       Returns a Map of technology elements to their use count in 'code'
       by walking through the abstract syntax tree of the code.

       See https://docs.python.org/3.5/library/ast.html#abstract-grammar
       for details.

       Raises SyntaxError if parsing fails.

        Note:
        'language_index' is unused because we only support javascript in this implementation but that could change in the future.
        'filename' is unused.
        'context' is unused.

       */
    let profile = new Map();
    try {
        let bindings = new Map(STANDARD_LIBRARY);
        traverse.default(parse(code), {
            enter(path) {
                let node = path.node;
                add(profile, GRAMMAR+node.type, 1);
                if (node.type == 'ImportDeclaration') {
                    let importDeclaration = node;
                    let source = node.source;
                    if (source.value.startsWith('.') || source.value.startsWith('/')) {
                        //console.log('Local import, ignoring: import "%s"', source.value);
                        // TODO use rsyslog instead...
                    } else {
                        importDeclaration.specifiers.forEach( specifier => {
                            switch (specifier.type) {
                                case "ImportSpecifier":
                                    bindings.set(specifier.local.name, THIRD_PARTY+source.value+'.'+specifier.imported.name);
                                break;

                                case "ImportDefaultSpecifier":
                                    bindings.set(specifier.local.name, THIRD_PARTY+source.value+'.'+specifier.local.name);
                                break;

                                case "ImportNamespaceSpecifier":
                                    bindings.set(specifier.local.name, THIRD_PARTY+source.value+'.'+specifier.local.name);
                                break;
                            }
                        });
                    }
                } else if (node.type == 'Identifier') {
                    if (bindings.has(node.name)) {
                        add(profile, bindings.get(node.name), 1);
                    }
                }
            }
        });
    } catch (e) {
        console.log(e);
    }
    return profile
}


function languages() {
    return [ JS_LANGUAGE ];
}


function grammar() {
    return types.TYPES;
}


const methods = [ languages, grammar, scan_contents ];


function run(call) {
    let method = methods[call[0]];
    let args = call.slice(1);
    let result = method.apply(this, args);
    return result;
}


exports.run = run;
