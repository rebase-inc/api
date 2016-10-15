# Language Parsing TCP Protocol

## Internal TechProfile Data Organization
{
    '<language>.<sub_level>.<node>': [ <first>, <last>, repetitions ],
}

<language> is the capitalized name of the language. Example: 'Python', 'Java', 'Javascript', etc.
<sub_level> is in ['__language__', '__standard_library__', '__third_party__']
<node> is any string describing the used element.

All data shall be JSON encoded

## Request:
[ <method_number>, *<args> ]

### scan_contents
Return a description of all the language constructs added in the 'code', 
as well as all the added elements from libraries.

#### Request
method_number = 0
args = [ <filename>, <code>, <date>] 
filename: a string containing the path to the file analyzed
code: a string containing the code to be parsed
date: a number containing the UTC Epoch date when the file was committed

Example:

request = '[0, "/foo.js", "function foo(bar)\n{ console.log(\"boo\");\n}", 1340648513 ]'

#### Response
{
    'Javascript.__language__.ArrayPattern': [ 1340648513, 1340748280, 41 ],
    'Javascript.__language__.Function': [ 1340648513, 1340748280, 29 ],
}

### scan_patch
Return a description of all the language constructs added in the 'code', 
as well as all the added elements from libraries.

#### Request
method_number = 1
args = [ <filename>, <code>, <previous_code>, <date>] 
filename: a string containing the path to the file analyzed
code: a string containing the code to be parsed
previous_code: a string containing the previous version of the code to be parsed
date: a number containing the UTC Epoch date when the file was committed

Example:

request = '[0, "/foo.js", "function foo(bar)\n{ var a=1;\nconsole.log(\"boo\");\n}", "function foo(bar)\n{ console.log(\"boo\");\n}", 1340648513 ]'

#### Response
{
    'Javascript.__language__.ArrayPattern': [ 1340648513, 1340748280, 41 ],
    'Javascript.__language__.Function': [ 1340648513, 1340748280, 29 ],
}

### language
Returns the list of abstract syntax tree nodes that constitute the grammar of the language.

#### Request
method_number = 2
no arguments

request = '[2]'

#### Response
[
    'Javascript.__language__.ImportNamespaceSpecifier',
    'Javascript.__language__.ThisExpression',
    ...
]


